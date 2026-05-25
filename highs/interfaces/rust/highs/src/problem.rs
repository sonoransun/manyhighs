//! Low-level problem containers passed wholesale to HiGHS.
//!
//! These mirror the `Highs_passLp` / `Highs_passModel` argument lists with owned
//! vectors. For incremental construction or an expression DSL, see
//! [`crate::Highs::add_var`] and [`crate::LinearExpr`].

use crate::enums::{HessianFormat, MatrixFormat, ObjSense, VarType};
use highs_sys::HighsInt;

/// A sparse matrix in compressed column or row form.
///
/// `start` has one entry per column (CSC) or row (CSR); `index` and `value`
/// have one entry per nonzero. Column/row `j` occupies `start[j]..start[j+1]`,
/// with `start[n]` implicitly equal to the nonzero count.
#[derive(Debug, Clone, Default, PartialEq)]
pub struct Sparse {
    pub format: MatrixFormat,
    pub start: Vec<HighsInt>,
    pub index: Vec<HighsInt>,
    pub value: Vec<f64>,
}

impl Sparse {
    /// Number of stored nonzeros.
    pub fn nnz(&self) -> usize {
        self.value.len()
    }
}

/// A linear program: `min/max cᵀx + offset  s.t.  rl ≤ Ax ≤ ru, l ≤ x ≤ u`.
#[derive(Debug, Clone, PartialEq)]
pub struct LpProblem {
    pub sense: ObjSense,
    pub offset: f64,
    pub col_cost: Vec<f64>,
    pub col_lower: Vec<f64>,
    pub col_upper: Vec<f64>,
    pub row_lower: Vec<f64>,
    pub row_upper: Vec<f64>,
    pub matrix: Sparse,
}

impl LpProblem {
    pub fn num_col(&self) -> usize {
        self.col_cost.len()
    }
    pub fn num_row(&self) -> usize {
        self.row_lower.len()
    }
}

/// A mixed-integer program: an [`LpProblem`] plus per-column integrality.
#[derive(Debug, Clone, PartialEq)]
pub struct MipProblem {
    pub lp: LpProblem,
    pub integrality: Vec<VarType>,
}

/// A convex quadratic program: an [`LpProblem`] plus a Hessian `Q` such that the
/// objective is `½ xᵀQx + cᵀx`.
#[derive(Debug, Clone, PartialEq)]
pub struct QpProblem {
    pub lp: LpProblem,
    pub hessian_format: HessianFormat,
    pub hessian: Sparse,
}
