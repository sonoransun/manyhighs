//! Incremental model construction and the expression-DSL entry points,
//! implemented as additional methods on [`Highs`].

use crate::enums::{ObjSense, VarType};
use crate::error::{check, Result};
use crate::expression::{Col, Constraint, LinearExpr, Row};
use crate::model::Highs;
use highs_sys::{self as sys, HighsInt};

impl Highs {
    // ----- adding variables ------------------------------------------------

    /// Add a continuous variable with the given bounds; returns its handle.
    pub fn add_var(&mut self, lower: f64, upper: f64) -> Result<Col> {
        let idx = self.num_col() as HighsInt;
        check(unsafe { sys::Highs_addVar(self.as_ptr(), lower, upper) })?;
        Ok(Col(idx))
    }

    /// Add an integer variable with the given bounds.
    pub fn add_integer(&mut self, lower: f64, upper: f64) -> Result<Col> {
        let c = self.add_var(lower, upper)?;
        self.set_integrality(c, VarType::Integer)?;
        Ok(c)
    }

    /// Add a binary (0/1) variable.
    pub fn add_binary(&mut self) -> Result<Col> {
        self.add_integer(0.0, 1.0)
    }

    /// Set a variable's integrality.
    pub fn set_integrality(&mut self, col: Col, kind: VarType) -> Result<()> {
        check(unsafe { sys::Highs_changeColIntegrality(self.as_ptr(), col.0, kind.as_raw()) })
    }

    // ----- adding constraints ----------------------------------------------

    /// Add a ranged linear constraint built from the expression DSL; returns its handle.
    pub fn add_constr(&mut self, c: Constraint) -> Result<Row> {
        let idx = self.num_row() as HighsInt;
        let index: Vec<HighsInt> = c.terms.iter().map(|(col, _)| col.0).collect();
        let value: Vec<f64> = c.terms.iter().map(|(_, v)| *v).collect();
        check(unsafe {
            sys::Highs_addRow(
                self.as_ptr(),
                c.lower,
                c.upper,
                value.len() as HighsInt,
                index.as_ptr(),
                value.as_ptr(),
            )
        })?;
        Ok(Row(idx))
    }

    // ----- objective -------------------------------------------------------

    /// Set the objective to `obj` with the given sense.
    ///
    /// Costs are written for every column appearing in `obj`, the objective
    /// offset is set to `obj`'s constant, and the sense is updated. Columns not
    /// mentioned keep their current cost.
    pub fn set_objective(&mut self, sense: ObjSense, obj: impl Into<LinearExpr>) -> Result<()> {
        let obj = obj.into();
        self.change_objective_sense(sense)?;
        for (col, coef) in obj.collapsed() {
            check(unsafe { sys::Highs_changeColCost(self.as_ptr(), col.0, coef) })?;
        }
        self.change_objective_offset(obj.constant)
    }

    /// Minimize the given expression.
    pub fn minimize(&mut self, obj: impl Into<LinearExpr>) -> Result<()> {
        self.set_objective(ObjSense::Minimize, obj)
    }

    /// Maximize the given expression.
    pub fn maximize(&mut self, obj: impl Into<LinearExpr>) -> Result<()> {
        self.set_objective(ObjSense::Maximize, obj)
    }

    /// Change only the optimization direction.
    pub fn change_objective_sense(&mut self, sense: ObjSense) -> Result<()> {
        check(unsafe { sys::Highs_changeObjectiveSense(self.as_ptr(), sense.as_raw()) })
    }

    /// Set the constant objective offset.
    pub fn change_objective_offset(&mut self, offset: f64) -> Result<()> {
        check(unsafe { sys::Highs_changeObjectiveOffset(self.as_ptr(), offset) })
    }

    // ----- modifying an existing model -------------------------------------

    /// Change one variable's objective coefficient.
    pub fn change_col_cost(&mut self, col: Col, cost: f64) -> Result<()> {
        check(unsafe { sys::Highs_changeColCost(self.as_ptr(), col.0, cost) })
    }

    /// Change one variable's bounds.
    pub fn change_col_bounds(&mut self, col: Col, lower: f64, upper: f64) -> Result<()> {
        check(unsafe { sys::Highs_changeColBounds(self.as_ptr(), col.0, lower, upper) })
    }

    /// Change one constraint's bounds.
    pub fn change_row_bounds(&mut self, row: Row, lower: f64, upper: f64) -> Result<()> {
        check(unsafe { sys::Highs_changeRowBounds(self.as_ptr(), row.0, lower, upper) })
    }

    /// Set a single matrix coefficient `A[row, col]`.
    pub fn change_coeff(&mut self, row: Row, col: Col, value: f64) -> Result<()> {
        check(unsafe { sys::Highs_changeCoeff(self.as_ptr(), row.0, col.0, value) })
    }

    // ----- deleting --------------------------------------------------------

    /// Delete the inclusive column range `from..=to` (0-based). Remaining
    /// columns are renumbered, so existing [`Col`] handles past `from` are
    /// invalidated.
    pub fn delete_cols(&mut self, from: usize, to: usize) -> Result<()> {
        check(unsafe {
            sys::Highs_deleteColsByRange(self.as_ptr(), from as HighsInt, to as HighsInt)
        })
    }

    /// Delete the inclusive row range `from..=to` (0-based). Remaining rows are
    /// renumbered.
    pub fn delete_rows(&mut self, from: usize, to: usize) -> Result<()> {
        check(unsafe {
            sys::Highs_deleteRowsByRange(self.as_ptr(), from as HighsInt, to as HighsInt)
        })
    }
}
