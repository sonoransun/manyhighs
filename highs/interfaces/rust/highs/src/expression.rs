//! A small linear-expression DSL, mirroring highspy's `highs_linear_expression`.
//!
//! ```
//! use highs::{Highs, ObjSense, ModelStatus, qsum};
//!
//! let mut h = Highs::new().silenced();
//! let x = h.add_var(0.0, 10.0).unwrap();
//! let y = h.add_var(0.0, 10.0).unwrap();
//! h.add_constr((x + y).le(4.0)).unwrap();          // x + y <= 4
//! h.add_constr((x + 3.0 * y).le(6.0)).unwrap();    // x + 3y <= 6
//! h.maximize(2.0 * x + 3.0 * y).unwrap();          // max 2x + 3y
//! assert_eq!(h.run().unwrap(), ModelStatus::Optimal);
//! assert!((h.objective_value() - 9.0).abs() < 1e-7);
//! let _ = qsum([x, y]); // sum helper
//! ```

use highs_sys::HighsInt;
use std::ops::{Add, AddAssign, Mul, Neg, Sub};

/// The value HiGHS uses for ±infinity in bounds.
pub const INF: f64 = 1.0e30;

/// A variable handle (column index). Cheap to copy.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct Col(pub HighsInt);

/// A constraint handle (row index). Cheap to copy.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct Row(pub HighsInt);

impl Col {
    /// The 0-based column index as `usize`.
    pub fn index(self) -> usize {
        self.0 as usize
    }
}

impl Row {
    /// The 0-based row index as `usize`.
    pub fn index(self) -> usize {
        self.0 as usize
    }
}

/// A linear expression `Σ cᵢ·xᵢ + k`. Terms may repeat; they are summed when the
/// expression is consumed (in [`Highs::set_objective`](crate::Highs::set_objective)
/// or [`Highs::add_constr`](crate::Highs::add_constr)).
#[derive(Debug, Clone, Default, PartialEq)]
pub struct LinearExpr {
    pub(crate) terms: Vec<(Col, f64)>,
    pub(crate) constant: f64,
}

impl LinearExpr {
    /// An empty expression (value 0).
    pub fn new() -> Self {
        Self::default()
    }

    /// Combine repeated columns into a single coefficient each, dropping zeros.
    pub(crate) fn collapsed(&self) -> Vec<(Col, f64)> {
        let mut out: Vec<(Col, f64)> = Vec::with_capacity(self.terms.len());
        for &(col, coef) in &self.terms {
            if let Some(slot) = out.iter_mut().find(|(c, _)| *c == col) {
                slot.1 += coef;
            } else {
                out.push((col, coef));
            }
        }
        out.retain(|(_, c)| *c != 0.0);
        out
    }

    /// `expr ≤ rhs`.
    pub fn le(self, rhs: f64) -> Constraint {
        Constraint::ranged(self, -INF, rhs)
    }

    /// `expr ≥ rhs`.
    pub fn ge(self, rhs: f64) -> Constraint {
        Constraint::ranged(self, rhs, INF)
    }

    /// `expr = rhs`.
    pub fn equal_to(self, rhs: f64) -> Constraint {
        Constraint::ranged(self, rhs, rhs)
    }

    /// `lo ≤ expr ≤ hi`.
    pub fn in_range(self, lo: f64, hi: f64) -> Constraint {
        Constraint::ranged(self, lo, hi)
    }
}

/// A ranged linear constraint `lower ≤ Σ cᵢ·xᵢ ≤ upper`, with the expression's
/// constant already folded into the bounds.
#[derive(Debug, Clone, PartialEq)]
pub struct Constraint {
    pub(crate) terms: Vec<(Col, f64)>,
    pub(crate) lower: f64,
    pub(crate) upper: f64,
}

impl Constraint {
    fn ranged(expr: LinearExpr, lo: f64, hi: f64) -> Self {
        // Move the constant to the right-hand side: lo - k ≤ Σ cᵢxᵢ ≤ hi - k.
        let shift = |b: f64| {
            if b >= INF {
                INF
            } else if b <= -INF {
                -INF
            } else {
                b - expr.constant
            }
        };
        Constraint {
            terms: expr.collapsed(),
            lower: shift(lo),
            upper: shift(hi),
        }
    }
}

// ----- conversions ---------------------------------------------------------

impl From<Col> for LinearExpr {
    fn from(c: Col) -> Self {
        LinearExpr {
            terms: vec![(c, 1.0)],
            constant: 0.0,
        }
    }
}

impl From<f64> for LinearExpr {
    fn from(k: f64) -> Self {
        LinearExpr {
            terms: Vec::new(),
            constant: k,
        }
    }
}

// ----- scaling: f64 * Col, Col * f64, f64 * expr, expr * f64 ---------------

impl Mul<f64> for Col {
    type Output = LinearExpr;
    fn mul(self, k: f64) -> LinearExpr {
        LinearExpr {
            terms: vec![(self, k)],
            constant: 0.0,
        }
    }
}

impl Mul<Col> for f64 {
    type Output = LinearExpr;
    fn mul(self, c: Col) -> LinearExpr {
        c * self
    }
}

impl Mul<f64> for LinearExpr {
    type Output = LinearExpr;
    fn mul(mut self, k: f64) -> LinearExpr {
        for t in &mut self.terms {
            t.1 *= k;
        }
        self.constant *= k;
        self
    }
}

impl Mul<LinearExpr> for f64 {
    type Output = LinearExpr;
    fn mul(self, e: LinearExpr) -> LinearExpr {
        e * self
    }
}

// ----- negation ------------------------------------------------------------

impl Neg for LinearExpr {
    type Output = LinearExpr;
    fn neg(self) -> LinearExpr {
        self * -1.0
    }
}

impl Neg for Col {
    type Output = LinearExpr;
    fn neg(self) -> LinearExpr {
        self * -1.0
    }
}

// ----- addition / subtraction ----------------------------------------------
// Two generic impls (one per Self type) keep the surface small while accepting
// Col, f64, and LinearExpr on the right-hand side.

impl<T: Into<LinearExpr>> Add<T> for LinearExpr {
    type Output = LinearExpr;
    fn add(mut self, rhs: T) -> LinearExpr {
        let rhs = rhs.into();
        self.terms.extend(rhs.terms);
        self.constant += rhs.constant;
        self
    }
}

impl<T: Into<LinearExpr>> Sub<T> for LinearExpr {
    type Output = LinearExpr;
    fn sub(self, rhs: T) -> LinearExpr {
        self + (rhs.into() * -1.0)
    }
}

impl<T: Into<LinearExpr>> Add<T> for Col {
    type Output = LinearExpr;
    fn add(self, rhs: T) -> LinearExpr {
        LinearExpr::from(self) + rhs
    }
}

impl<T: Into<LinearExpr>> Sub<T> for Col {
    type Output = LinearExpr;
    fn sub(self, rhs: T) -> LinearExpr {
        LinearExpr::from(self) - rhs
    }
}

// f64 on the left for `+`/`-`. A generic `impl<T: Into<LinearExpr>>` here would
// collide with std's `f64 - f64`, so the right-hand types are spelled out.
impl Add<Col> for f64 {
    type Output = LinearExpr;
    fn add(self, rhs: Col) -> LinearExpr {
        LinearExpr::from(rhs) + self
    }
}

impl Sub<Col> for f64 {
    type Output = LinearExpr;
    fn sub(self, rhs: Col) -> LinearExpr {
        LinearExpr::from(self) - rhs
    }
}

impl Add<LinearExpr> for f64 {
    type Output = LinearExpr;
    fn add(self, rhs: LinearExpr) -> LinearExpr {
        rhs + self
    }
}

impl Sub<LinearExpr> for f64 {
    type Output = LinearExpr;
    fn sub(self, rhs: LinearExpr) -> LinearExpr {
        LinearExpr::from(self) - rhs
    }
}

impl<T: Into<LinearExpr>> AddAssign<T> for LinearExpr {
    fn add_assign(&mut self, rhs: T) {
        let rhs = rhs.into();
        self.terms.extend(rhs.terms);
        self.constant += rhs.constant;
    }
}

// ----- comparison helpers on a bare Col ------------------------------------

impl Col {
    pub fn le(self, rhs: f64) -> Constraint {
        LinearExpr::from(self).le(rhs)
    }
    pub fn ge(self, rhs: f64) -> Constraint {
        LinearExpr::from(self).ge(rhs)
    }
    pub fn equal_to(self, rhs: f64) -> Constraint {
        LinearExpr::from(self).equal_to(rhs)
    }
    pub fn in_range(self, lo: f64, hi: f64) -> Constraint {
        LinearExpr::from(self).in_range(lo, hi)
    }
}

/// Sum any iterator of expressions (or columns) into one [`LinearExpr`].
///
/// Mirrors highspy's `qsum`. `qsum(vars.iter().map(|&v| cost[v] * v))` is the
/// idiomatic way to build a large objective.
pub fn qsum<T, I>(iter: I) -> LinearExpr
where
    I: IntoIterator<Item = T>,
    T: Into<LinearExpr>,
{
    let mut acc = LinearExpr::new();
    for t in iter {
        acc += t;
    }
    acc
}
