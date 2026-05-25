//! The core [`Highs`] solver handle plus its load/solve/options/extraction API.

use crate::enums::{BasisStatus, ModelStatus};
use crate::error::{check, check_len, HighsError, Result};
use crate::problem::{LpProblem, MipProblem, QpProblem};
use crate::solution::{Basis, Solution};
use highs_sys as sys;
use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_void};

/// An owned HiGHS solver instance.
///
/// Wraps the opaque `void*` from `Highs_create` and frees it on drop. The
/// instance is **not** internally thread-safe, so mutating methods take
/// `&mut self`; it *is* [`Send`], so it can be moved onto another thread (the
/// foundation of the GIL-free parallel runtime in [`crate::parallel`]).
pub struct Highs {
    ptr: *mut c_void,
    /// Boxed callback state kept alive for the lifetime of the instance so the
    /// pointer handed to `Highs_setCallback` stays valid (see `callback.rs`).
    pub(crate) callback: Option<Box<crate::callback::CallbackState>>,
}

// SAFETY: a Highs instance owns a self-contained C++ object reachable only
// through `ptr`. Nothing pins it to its creating thread (the work-stealing
// scheduler lives in thread-local storage, initialized lazily on whichever
// thread calls `run`). Exclusive ownership transfer across threads is sound.
// It is deliberately NOT `Sync`: concurrent `&self` access would race the
// un-synchronized C++ state.
unsafe impl Send for Highs {}

impl Highs {
    /// Create a fresh solver instance.
    pub fn new() -> Self {
        let ptr = unsafe { sys::Highs_create() };
        assert!(!ptr.is_null(), "Highs_create returned null");
        Highs {
            ptr,
            callback: None,
        }
    }

    /// The raw opaque handle. Use with [`crate::ffi`] for capabilities not yet
    /// wrapped. The pointer is valid until this `Highs` is dropped.
    pub fn as_ptr(&self) -> *mut c_void {
        self.ptr
    }

    // ----- options ---------------------------------------------------------

    /// Set a boolean option by name (e.g. `"output_flag"`).
    pub fn set_bool_option(&mut self, name: &str, value: bool) -> Result<()> {
        let cname = CString::new(name)?;
        check(unsafe {
            sys::Highs_setBoolOptionValue(self.ptr, cname.as_ptr(), value as sys::HighsInt)
        })
    }

    /// Set an integer option by name (e.g. `"threads"`).
    pub fn set_int_option(&mut self, name: &str, value: i32) -> Result<()> {
        let cname = CString::new(name)?;
        check(unsafe {
            sys::Highs_setIntOptionValue(self.ptr, cname.as_ptr(), value as sys::HighsInt)
        })
    }

    /// Set a floating-point option by name (e.g. `"time_limit"`).
    pub fn set_double_option(&mut self, name: &str, value: f64) -> Result<()> {
        let cname = CString::new(name)?;
        check(unsafe { sys::Highs_setDoubleOptionValue(self.ptr, cname.as_ptr(), value) })
    }

    /// Set a string option by name (e.g. `"solver"`, `"presolve"`).
    pub fn set_string_option(&mut self, name: &str, value: &str) -> Result<()> {
        let cname = CString::new(name)?;
        let cval = CString::new(value)?;
        check(unsafe {
            sys::Highs_setStringOptionValue(self.ptr, cname.as_ptr(), cval.as_ptr())
        })
    }

    /// Read a boolean option by name.
    pub fn get_bool_option(&self, name: &str) -> Result<bool> {
        let cname = CString::new(name)?;
        let mut v: sys::HighsInt = 0;
        check(unsafe { sys::Highs_getBoolOptionValue(self.ptr, cname.as_ptr(), &mut v) })?;
        Ok(v != 0)
    }

    /// Read an integer option by name.
    pub fn get_int_option(&self, name: &str) -> Result<i32> {
        let cname = CString::new(name)?;
        let mut v: sys::HighsInt = 0;
        check(unsafe { sys::Highs_getIntOptionValue(self.ptr, cname.as_ptr(), &mut v) })?;
        Ok(v as i32)
    }

    /// Read a floating-point option by name.
    pub fn get_double_option(&self, name: &str) -> Result<f64> {
        let cname = CString::new(name)?;
        let mut v: f64 = 0.0;
        check(unsafe { sys::Highs_getDoubleOptionValue(self.ptr, cname.as_ptr(), &mut v) })?;
        Ok(v)
    }

    /// Read a string option by name.
    pub fn get_string_option(&self, name: &str) -> Result<String> {
        let cname = CString::new(name)?;
        let mut buf = vec![0 as c_char; sys::kHighsMaximumStringLength as usize + 1];
        check(unsafe {
            sys::Highs_getStringOptionValue(self.ptr, cname.as_ptr(), buf.as_mut_ptr())
        })?;
        let s = unsafe { CStr::from_ptr(buf.as_ptr()) };
        s.to_str()
            .map(str::to_owned)
            .map_err(|_| HighsError::InvalidUtf8)
    }

    // ----- option convenience ---------------------------------------------

    /// Number of internal threads HiGHS may use (0 = auto). For the GIL-free
    /// many-instance pattern set this to 1 to avoid oversubscription.
    pub fn set_threads(&mut self, n: i32) -> Result<()> {
        self.set_int_option("threads", n)
    }

    /// Wall-clock time limit in seconds.
    pub fn set_time_limit(&mut self, seconds: f64) -> Result<()> {
        self.set_double_option("time_limit", seconds)
    }

    /// Presolve mode: `"on"`, `"off"`, or `"choose"`.
    pub fn set_presolve(&mut self, mode: &str) -> Result<()> {
        self.set_string_option("presolve", mode)
    }

    /// Solver selection: `"choose"`, `"simplex"`, `"ipm"`, `"hipo"`, `"qpasm"`, or `"pdlp"`.
    pub fn set_solver(&mut self, solver: &str) -> Result<()> {
        self.set_string_option("solver", solver)
    }

    /// Parallelism: `"off"`, `"choose"`, or `"on"`.
    pub fn set_parallel(&mut self, mode: &str) -> Result<()> {
        self.set_string_option("parallel", mode)
    }

    /// Toggle solver console/log output.
    pub fn set_output(&mut self, on: bool) -> Result<()> {
        self.set_bool_option("output_flag", on)
    }

    /// Silence all solver output. Returns `self` for chaining at construction.
    pub fn silenced(mut self) -> Self {
        let _ = self.set_output(false);
        self
    }

    // ----- model loading ---------------------------------------------------

    /// Load a linear program, replacing any existing model.
    pub fn pass_lp(&mut self, lp: &LpProblem) -> Result<()> {
        let num_col = lp.num_col();
        let num_row = lp.num_row();
        check_len("col_lower", lp.col_lower.len(), num_col)?;
        check_len("col_upper", lp.col_upper.len(), num_col)?;
        check_len("row_upper", lp.row_upper.len(), num_row)?;
        check_len("matrix.value", lp.matrix.value.len(), lp.matrix.index.len())?;
        let major = match lp.matrix.format {
            crate::enums::MatrixFormat::ColWise => num_col,
            crate::enums::MatrixFormat::RowWise => num_row,
        };
        check_len("matrix.start", lp.matrix.start.len(), major)?;
        let num_nz = lp.matrix.nnz();
        check(unsafe {
            sys::Highs_passLp(
                self.ptr,
                num_col as sys::HighsInt,
                num_row as sys::HighsInt,
                num_nz as sys::HighsInt,
                lp.matrix.format.as_raw(),
                lp.sense.as_raw(),
                lp.offset,
                lp.col_cost.as_ptr(),
                lp.col_lower.as_ptr(),
                lp.col_upper.as_ptr(),
                lp.row_lower.as_ptr(),
                lp.row_upper.as_ptr(),
                lp.matrix.start.as_ptr(),
                lp.matrix.index.as_ptr(),
                lp.matrix.value.as_ptr(),
            )
        })
    }

    /// Load a mixed-integer program, replacing any existing model.
    pub fn pass_mip(&mut self, mip: &MipProblem) -> Result<()> {
        let lp = &mip.lp;
        let num_col = lp.num_col();
        let num_row = lp.num_row();
        check_len("col_lower", lp.col_lower.len(), num_col)?;
        check_len("col_upper", lp.col_upper.len(), num_col)?;
        check_len("row_upper", lp.row_upper.len(), num_row)?;
        check_len("integrality", mip.integrality.len(), num_col)?;
        check_len("matrix.value", lp.matrix.value.len(), lp.matrix.index.len())?;
        let major = match lp.matrix.format {
            crate::enums::MatrixFormat::ColWise => num_col,
            crate::enums::MatrixFormat::RowWise => num_row,
        };
        check_len("matrix.start", lp.matrix.start.len(), major)?;
        let integ: Vec<sys::HighsInt> = mip.integrality.iter().map(|t| t.as_raw()).collect();
        check(unsafe {
            sys::Highs_passMip(
                self.ptr,
                num_col as sys::HighsInt,
                num_row as sys::HighsInt,
                lp.matrix.nnz() as sys::HighsInt,
                lp.matrix.format.as_raw(),
                lp.sense.as_raw(),
                lp.offset,
                lp.col_cost.as_ptr(),
                lp.col_lower.as_ptr(),
                lp.col_upper.as_ptr(),
                lp.row_lower.as_ptr(),
                lp.row_upper.as_ptr(),
                lp.matrix.start.as_ptr(),
                lp.matrix.index.as_ptr(),
                lp.matrix.value.as_ptr(),
                integ.as_ptr(),
            )
        })
    }

    /// Load a convex quadratic program (`½ xᵀQx + cᵀx`), replacing any existing
    /// model. The LP part is loaded first, then the Hessian `Q`.
    pub fn pass_qp(&mut self, qp: &QpProblem) -> Result<()> {
        self.pass_lp(&qp.lp)?;
        let dim = qp.lp.num_col();
        check_len("hessian.start", qp.hessian.start.len(), dim)?;
        check_len("hessian.value", qp.hessian.value.len(), qp.hessian.index.len())?;
        check(unsafe {
            sys::Highs_passHessian(
                self.ptr,
                dim as sys::HighsInt,
                qp.hessian.nnz() as sys::HighsInt,
                qp.hessian_format.as_raw(),
                qp.hessian.start.as_ptr(),
                qp.hessian.index.as_ptr(),
                qp.hessian.value.as_ptr(),
            )
        })
    }

    // ----- solving ---------------------------------------------------------

    /// Run the solver and return the resulting [`ModelStatus`].
    ///
    /// If a registered callback panicked during the solve, the panic was caught
    /// at the FFI boundary and is re-raised here.
    pub fn run(&mut self) -> Result<ModelStatus> {
        let rc = unsafe { sys::Highs_run(self.ptr) };
        if let Some(panic) = self.take_callback_panic() {
            std::panic::resume_unwind(panic);
        }
        check(rc)?;
        Ok(self.model_status())
    }

    /// The status of the most recent solve.
    pub fn model_status(&self) -> ModelStatus {
        ModelStatus::from_raw(unsafe { sys::Highs_getModelStatus(self.ptr) })
    }

    /// The objective value of the incumbent solution.
    pub fn objective_value(&self) -> f64 {
        unsafe { sys::Highs_getObjectiveValue(self.ptr) }
    }

    /// Number of columns (variables) in the model.
    pub fn num_col(&self) -> usize {
        unsafe { sys::Highs_getNumCol(self.ptr) as usize }
    }

    /// Number of rows (constraints) in the model.
    pub fn num_row(&self) -> usize {
        unsafe { sys::Highs_getNumRow(self.ptr) as usize }
    }

    /// The value HiGHS treats as infinity (for unbounded bounds).
    pub fn infinity(&self) -> f64 {
        unsafe { sys::Highs_getInfinity(self.ptr) }
    }

    // ----- extraction ------------------------------------------------------

    /// Extract the full primal/dual solution.
    pub fn solution(&self) -> Result<Solution> {
        let nc = self.num_col();
        let nr = self.num_row();
        let mut col_value = vec![0.0; nc];
        let mut col_dual = vec![0.0; nc];
        let mut row_value = vec![0.0; nr];
        let mut row_dual = vec![0.0; nr];
        check(unsafe {
            sys::Highs_getSolution(
                self.ptr,
                col_value.as_mut_ptr(),
                col_dual.as_mut_ptr(),
                row_value.as_mut_ptr(),
                row_dual.as_mut_ptr(),
            )
        })?;
        Ok(Solution {
            col_value,
            col_dual,
            row_value,
            row_dual,
        })
    }

    /// Primal value of a single variable after a solve.
    pub fn col_value(&self, col: usize) -> Result<f64> {
        Ok(self.solution()?.col_value[col])
    }

    /// Extract the simplex basis (valid after an LP solve).
    pub fn basis(&self) -> Result<Basis> {
        let nc = self.num_col();
        let nr = self.num_row();
        let mut cs = vec![0 as sys::HighsInt; nc];
        let mut rs = vec![0 as sys::HighsInt; nr];
        check(unsafe { sys::Highs_getBasis(self.ptr, cs.as_mut_ptr(), rs.as_mut_ptr()) })?;
        Ok(Basis {
            col_status: cs.into_iter().map(BasisStatus::from_raw).collect(),
            row_status: rs.into_iter().map(BasisStatus::from_raw).collect(),
        })
    }

    // ----- info ------------------------------------------------------------

    /// Read a 32-bit integer info value by name (e.g. `"simplex_iteration_count"`).
    pub fn info_i32(&self, name: &str) -> Result<i32> {
        let cname = CString::new(name)?;
        let mut v: sys::HighsInt = 0;
        check(unsafe { sys::Highs_getIntInfoValue(self.ptr, cname.as_ptr(), &mut v) })?;
        Ok(v as i32)
    }

    /// Read a 64-bit integer info value by name (e.g. `"mip_node_count"`).
    pub fn info_i64(&self, name: &str) -> Result<i64> {
        let cname = CString::new(name)?;
        let mut v: i64 = 0;
        check(unsafe { sys::Highs_getInt64InfoValue(self.ptr, cname.as_ptr(), &mut v) })?;
        Ok(v)
    }

    /// Read a floating-point info value by name (e.g. `"mip_gap"`).
    pub fn info_f64(&self, name: &str) -> Result<f64> {
        let cname = CString::new(name)?;
        let mut v: f64 = 0.0;
        check(unsafe { sys::Highs_getDoubleInfoValue(self.ptr, cname.as_ptr(), &mut v) })?;
        Ok(v)
    }

    // ----- reset -----------------------------------------------------------

    /// Drop the model but keep options and solver state (cheap reuse).
    pub fn clear_model(&mut self) -> Result<()> {
        check(unsafe { sys::Highs_clearModel(self.ptr) })
    }

    /// Drop solver state (basis etc.) but keep the model.
    pub fn clear_solver(&mut self) -> Result<()> {
        check(unsafe { sys::Highs_clearSolver(self.ptr) })
    }

    /// Reset everything (model, solution, options) to defaults.
    pub fn clear(&mut self) -> Result<()> {
        check(unsafe { sys::Highs_clear(self.ptr) })
    }
}

impl Default for Highs {
    fn default() -> Self {
        Self::new()
    }
}

impl Drop for Highs {
    fn drop(&mut self) {
        // Drop the boxed callback (if any) before destroying the instance, so
        // no live callback pointer can outlive its target.
        self.callback = None;
        unsafe { sys::Highs_destroy(self.ptr) };
    }
}

/// The HiGHS version string, e.g. `"1.14.0"`.
pub fn version() -> String {
    unsafe {
        CStr::from_ptr(sys::Highs_version())
            .to_string_lossy()
            .into_owned()
    }
}
