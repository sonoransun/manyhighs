//! User callbacks.
//!
//! A Rust closure is boxed into a [`CallbackState`] owned by the [`Highs`]
//! instance, so the pointer handed to `Highs_setCallback` stays valid for the
//! instance's lifetime. An `extern "C"` trampoline reconstructs the closure and
//! invokes it with a safe [`CallbackContext`]. The trampoline wraps the call in
//! [`std::panic::catch_unwind`] — unwinding across the C++ frame would be UB —
//! and a caught panic both interrupts the solve and is re-raised from
//! [`Highs::run`](crate::Highs::run).

use crate::enums::CallbackType;
use crate::error::{check, HighsError, Result};
use crate::model::Highs;
use highs_sys::{self as sys, HighsInt};
use std::any::Any;
use std::ffi::CStr;
use std::os::raw::{c_char, c_int, c_void};
use std::panic::{catch_unwind, AssertUnwindSafe};

/// What a callback asks the solver to do when it returns.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CallbackAction {
    /// Continue solving.
    Continue,
    /// Request that the solver stop as soon as possible.
    Interrupt,
}

type BoxedFn = Box<dyn for<'a> FnMut(&mut CallbackContext<'a>) -> CallbackAction + Send>;

/// Boxed callback closure plus a slot for a panic caught across the FFI
/// boundary. Stored in [`Highs`] so its address is stable and outlives `run`.
pub(crate) struct CallbackState {
    closure: BoxedFn,
    panic: Option<Box<dyn Any + Send + 'static>>,
}

impl CallbackState {
    pub(crate) fn take_panic(&mut self) -> Option<Box<dyn Any + Send + 'static>> {
        self.panic.take()
    }
}

/// Safe view of the data passed to a callback. Read solver progress through the
/// accessors; influence the solve with [`interrupt`](Self::interrupt) or
/// [`set_solution`](Self::set_solution).
pub struct CallbackContext<'a> {
    kind: CallbackType,
    message: Option<&'a str>,
    out: &'a sys::HighsCallbackDataOut,
    data_in: *mut sys::HighsCallbackDataIn,
}

impl<'a> CallbackContext<'a> {
    /// Which callback fired.
    pub fn kind(&self) -> CallbackType {
        self.kind
    }

    /// Log/diagnostic message, if any.
    pub fn message(&self) -> Option<&str> {
        self.message
    }

    /// Elapsed solve time in seconds.
    pub fn running_time(&self) -> f64 {
        self.out.running_time
    }

    /// Current objective value.
    pub fn objective(&self) -> f64 {
        self.out.objective_function_value
    }

    /// Cumulative simplex iterations.
    pub fn simplex_iterations(&self) -> i64 {
        self.out.simplex_iteration_count as i64
    }

    /// Cumulative interior-point iterations.
    pub fn ipm_iterations(&self) -> i64 {
        self.out.ipm_iteration_count as i64
    }

    /// MIP branch-and-bound nodes explored.
    pub fn mip_node_count(&self) -> i64 {
        self.out.mip_node_count
    }

    /// Best MIP primal (incumbent) bound.
    pub fn mip_primal_bound(&self) -> f64 {
        self.out.mip_primal_bound
    }

    /// Best MIP dual bound.
    pub fn mip_dual_bound(&self) -> f64 {
        self.out.mip_dual_bound
    }

    /// Current MIP optimality gap.
    pub fn mip_gap(&self) -> f64 {
        self.out.mip_gap
    }

    /// The incumbent MIP solution, when provided by this callback (otherwise empty).
    pub fn mip_solution(&self) -> &[f64] {
        if self.out.mip_solution.is_null() || self.out.mip_solution_size <= 0 {
            &[]
        } else {
            unsafe {
                std::slice::from_raw_parts(
                    self.out.mip_solution,
                    self.out.mip_solution_size as usize,
                )
            }
        }
    }

    /// Request that the solve be interrupted (equivalent to returning
    /// [`CallbackAction::Interrupt`]).
    ///
    /// Only effective for interruptible callback categories (simplex/IPM/MIP
    /// interrupt and logging); HiGHS forbids interrupting from the MIP
    /// information callbacks, so the request is ignored there.
    pub fn interrupt(&mut self) {
        if self.kind.allows_interrupt() && !self.data_in.is_null() {
            unsafe { (*self.data_in).user_interrupt = 1 };
        }
    }

    /// Submit a user solution (e.g. from a MIP user-solution callback).
    pub fn set_solution(&mut self, values: &[f64]) -> Result<()> {
        if self.data_in.is_null() {
            return Err(HighsError::Status);
        }
        check(unsafe {
            sys::Highs_setCallbackSolution(
                self.data_in,
                values.len() as HighsInt,
                values.as_ptr(),
            )
        })
    }
}

/// The `extern "C"` function HiGHS calls. Never panics across the boundary.
extern "C" fn trampoline(
    callback_type: c_int,
    message: *const c_char,
    data_out: *const sys::HighsCallbackDataOut,
    data_in: *mut sys::HighsCallbackDataIn,
    user_data: *mut c_void,
) {
    if user_data.is_null() || data_out.is_null() {
        return;
    }
    // SAFETY: user_data is the address of the CallbackState boxed in the Highs
    // instance; it is only ever accessed from the thread driving the solve.
    let state = unsafe { &mut *(user_data as *mut CallbackState) };
    let kind = CallbackType::from_raw(callback_type);

    // Only set user_interrupt for categories where HiGHS permits it; doing so
    // for a MIP information callback would trip an internal assertion.
    let request_interrupt = |di: *mut sys::HighsCallbackDataIn| {
        if kind.allows_interrupt() && !di.is_null() {
            unsafe { (*di).user_interrupt = 1 };
        }
    };

    // If an earlier invocation panicked, stop calling the (poisoned) closure and
    // keep requesting interrupt (where allowed) so the solve winds down.
    if state.panic.is_some() {
        request_interrupt(data_in);
        return;
    }

    let result = catch_unwind(AssertUnwindSafe(|| {
        let msg = if message.is_null() {
            None
        } else {
            unsafe { CStr::from_ptr(message) }.to_str().ok()
        };
        let mut ctx = CallbackContext {
            kind,
            message: msg,
            out: unsafe { &*data_out },
            data_in,
        };
        let action = (state.closure)(&mut ctx);
        if matches!(action, CallbackAction::Interrupt) {
            ctx.interrupt();
        }
    }));

    if let Err(e) = result {
        state.panic = Some(e);
        request_interrupt(data_in);
    }
}

impl Highs {
    /// Register a callback closure. Replaces any previously set callback.
    ///
    /// After registering, enable the categories you care about with
    /// [`start_callback`](Self::start_callback). The closure receives a
    /// [`CallbackContext`] and returns a [`CallbackAction`].
    pub fn set_callback<F>(&mut self, f: F) -> Result<()>
    where
        F: for<'a> FnMut(&mut CallbackContext<'a>) -> CallbackAction + Send + 'static,
    {
        let mut state = Box::new(CallbackState {
            closure: Box::new(f),
            panic: None,
        });
        // Stable heap address of the CallbackState; survives moving the Box into
        // self.callback (Box move does not relocate the heap allocation).
        let ptr = state.as_mut() as *mut CallbackState as *mut c_void;
        let rc = unsafe { sys::Highs_setCallback(self.as_ptr(), Some(trampoline), ptr) };
        self.callback = Some(state);
        check(rc)
    }

    /// Enable a callback category for subsequent solves.
    pub fn start_callback(&mut self, kind: CallbackType) -> Result<()> {
        check(unsafe { sys::Highs_startCallback(self.as_ptr(), kind.as_raw()) })
    }

    /// Disable a callback category.
    pub fn stop_callback(&mut self, kind: CallbackType) -> Result<()> {
        check(unsafe { sys::Highs_stopCallback(self.as_ptr(), kind.as_raw()) })
    }

    /// Unregister the callback closure entirely.
    pub fn clear_callback(&mut self) -> Result<()> {
        let rc = unsafe { sys::Highs_setCallback(self.as_ptr(), None, std::ptr::null_mut()) };
        self.callback = None;
        check(rc)
    }

    /// If the registered callback panicked during the last solve, take and
    /// return that panic payload (used by `run` to re-raise it).
    pub(crate) fn take_callback_panic(&mut self) -> Option<Box<dyn Any + Send + 'static>> {
        self.callback.as_mut().and_then(|s| s.take_panic())
    }
}
