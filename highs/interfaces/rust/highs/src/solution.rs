//! Solution and basis containers returned after a solve.

use crate::enums::BasisStatus;

/// Primal and dual values for every column and row.
#[derive(Debug, Clone, PartialEq)]
pub struct Solution {
    /// Primal value of each variable (column).
    pub col_value: Vec<f64>,
    /// Reduced cost (dual) of each variable.
    pub col_dual: Vec<f64>,
    /// Activity `Ax` of each constraint (row).
    pub row_value: Vec<f64>,
    /// Dual value of each constraint.
    pub row_dual: Vec<f64>,
}

/// A simplex basis: the status of every column and row.
#[derive(Debug, Clone, PartialEq)]
pub struct Basis {
    pub col_status: Vec<BasisStatus>,
    pub row_status: Vec<BasisStatus>,
}
