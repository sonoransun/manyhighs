//! Error and status types.

use crate::enums::ModelStatus;
use std::fmt;

/// The three return codes every HiGHS C API call produces.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HighsStatus {
    Ok,
    Warning,
    Error,
}

impl HighsStatus {
    pub(crate) fn from_raw(c: highs_sys::HighsInt) -> Self {
        match c {
            highs_sys::kHighsStatusError => HighsStatus::Error,
            highs_sys::kHighsStatusWarning => HighsStatus::Warning,
            _ => HighsStatus::Ok,
        }
    }
}

/// Errors surfaced by the safe wrapper.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum HighsError {
    /// A C API call returned [`HighsStatus::Error`].
    Status,
    /// `run` completed but the model status was not [`ModelStatus::Optimal`].
    NotOptimal(ModelStatus),
    /// A string passed to HiGHS contained an interior NUL byte.
    NulByte,
    /// A C string returned by HiGHS was not valid UTF-8.
    InvalidUtf8,
    /// Input slice lengths were inconsistent with the declared dimensions.
    DimensionMismatch {
        what: &'static str,
        expected: usize,
        got: usize,
    },
    /// An option or info name was not recognized by HiGHS.
    UnknownName(String),
}

impl fmt::Display for HighsError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            HighsError::Status => write!(f, "HiGHS returned an error status"),
            HighsError::NotOptimal(s) => write!(f, "model not solved to optimality: {s:?}"),
            HighsError::NulByte => write!(f, "string contained an interior NUL byte"),
            HighsError::InvalidUtf8 => write!(f, "HiGHS returned a non-UTF-8 string"),
            HighsError::DimensionMismatch {
                what,
                expected,
                got,
            } => write!(f, "dimension mismatch for {what}: expected {expected}, got {got}"),
            HighsError::UnknownName(n) => write!(f, "unknown option/info name: {n}"),
        }
    }
}

impl std::error::Error for HighsError {}

impl From<std::ffi::NulError> for HighsError {
    fn from(_: std::ffi::NulError) -> Self {
        HighsError::NulByte
    }
}

/// Result alias used throughout the crate.
pub type Result<T> = std::result::Result<T, HighsError>;

/// Map a raw status code to `Ok(())`, treating warnings as success.
pub(crate) fn check(c: highs_sys::HighsInt) -> Result<()> {
    match HighsStatus::from_raw(c) {
        HighsStatus::Ok | HighsStatus::Warning => Ok(()),
        HighsStatus::Error => Err(HighsError::Status),
    }
}

/// Validate that a slice has the expected length.
pub(crate) fn check_len(what: &'static str, got: usize, expected: usize) -> Result<()> {
    if got == expected {
        Ok(())
    } else {
        Err(HighsError::DimensionMismatch {
            what,
            expected,
            got,
        })
    }
}
