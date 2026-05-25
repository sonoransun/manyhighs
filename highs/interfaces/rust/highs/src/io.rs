//! File I/O and model introspection, as methods on [`Highs`].

use crate::enums::{ObjSense, OptionType, VarType};
use crate::error::{check, HighsError, Result};
use crate::expression::Col;
use crate::model::Highs;
use highs_sys as sys;
use std::ffi::CString;

impl Highs {
    // ----- file I/O --------------------------------------------------------

    /// Read a model from a file (`.mps`, `.lp`, optionally gzip-compressed),
    /// replacing any existing model.
    pub fn read_model(&mut self, path: &str) -> Result<()> {
        let c = CString::new(path)?;
        check(unsafe { sys::Highs_readModel(self.as_ptr(), c.as_ptr()) })
    }

    /// Write the current model to a file. The format follows the extension
    /// (`.mps`, `.lp`).
    pub fn write_model(&self, path: &str) -> Result<()> {
        let c = CString::new(path)?;
        check(unsafe { sys::Highs_writeModel(self.as_ptr(), c.as_ptr()) })
    }

    /// Write a human-readable solution report to a file.
    pub fn write_solution_pretty(&self, path: &str) -> Result<()> {
        let c = CString::new(path)?;
        check(unsafe { sys::Highs_writeSolutionPretty(self.as_ptr(), c.as_ptr()) })
    }

    /// Write the current options to a file.
    pub fn write_options(&self, path: &str) -> Result<()> {
        let c = CString::new(path)?;
        check(unsafe { sys::Highs_writeOptions(self.as_ptr(), c.as_ptr()) })
    }

    /// Read options from a file.
    pub fn read_options(&mut self, path: &str) -> Result<()> {
        let c = CString::new(path)?;
        check(unsafe { sys::Highs_readOptions(self.as_ptr(), c.as_ptr()) })
    }

    /// Reset all options to their defaults.
    pub fn reset_options(&mut self) -> Result<()> {
        check(unsafe { sys::Highs_resetOptions(self.as_ptr()) })
    }

    // ----- introspection ---------------------------------------------------

    /// The current optimization sense.
    pub fn objective_sense(&self) -> ObjSense {
        let mut s: sys::HighsInt = 0;
        unsafe { sys::Highs_getObjectiveSense(self.as_ptr(), &mut s) };
        ObjSense::from_raw(s)
    }

    /// The current objective offset.
    pub fn objective_offset(&self) -> f64 {
        let mut o = 0.0;
        unsafe { sys::Highs_getObjectiveOffset(self.as_ptr(), &mut o) };
        o
    }

    /// The integrality of a variable.
    pub fn col_integrality(&self, col: Col) -> Result<VarType> {
        let mut t: sys::HighsInt = 0;
        check(unsafe { sys::Highs_getColIntegrality(self.as_ptr(), col.0, &mut t) })?;
        Ok(VarType::from_raw(t))
    }

    /// The runtime type of an option.
    pub fn option_type(&self, name: &str) -> Result<OptionType> {
        let c = CString::new(name)?;
        let mut t: sys::HighsInt = 0;
        check(unsafe { sys::Highs_getOptionType(self.as_ptr(), c.as_ptr(), &mut t) })?;
        Ok(OptionType::from_raw(t))
    }

    /// Number of stored matrix nonzeros.
    pub fn num_nz(&self) -> usize {
        unsafe { sys::Highs_getNumNz(self.as_ptr()) as usize }
    }

    /// The HiGHS git hash the library was built from.
    pub fn git_hash(&self) -> Result<String> {
        let p = unsafe { sys::Highs_githash() };
        if p.is_null() {
            return Ok(String::new());
        }
        unsafe { std::ffi::CStr::from_ptr(p) }
            .to_str()
            .map(str::to_owned)
            .map_err(|_| HighsError::InvalidUtf8)
    }
}
