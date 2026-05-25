//! Safe, idiomatic Rust bindings to the [HiGHS](https://highs.dev) optimization
//! solver (LP, mixed-integer, and convex QP), with a GIL-free parallel runtime.
//!
//! ```
//! use highs::{Highs, LpProblem, Sparse, ObjSense, MatrixFormat, ModelStatus};
//!
//! // min x + y  s.t.  x + y >= 1,  0 <= x,y <= 10
//! let lp = LpProblem {
//!     sense: ObjSense::Minimize,
//!     offset: 0.0,
//!     col_cost: vec![1.0, 1.0],
//!     col_lower: vec![0.0, 0.0],
//!     col_upper: vec![10.0, 10.0],
//!     row_lower: vec![1.0],
//!     row_upper: vec![1.0e30],
//!     matrix: Sparse {
//!         format: MatrixFormat::RowWise,
//!         start: vec![0],
//!         index: vec![0, 1],
//!         value: vec![1.0, 1.0],
//!     },
//! };
//!
//! let mut h = Highs::new().silenced();
//! h.pass_lp(&lp).unwrap();
//! assert_eq!(h.run().unwrap(), ModelStatus::Optimal);
//! assert!((h.objective_value() - 1.0).abs() < 1e-9);
//! ```
//!
//! For capabilities not yet wrapped by the safe API, every raw `Highs_*`
//! function is available through [`ffi`].

mod builder;
mod enums;
mod error;
mod expression;
mod io;
mod model;
mod oneshot;
mod problem;
mod solution;

mod callback;

/// GIL-free parallel runtime: solve many independent models across OS threads.
pub mod parallel;

pub use callback::{CallbackAction, CallbackContext};
pub use parallel::{CancelToken, RunningSolve};
pub use enums::{
    BasisStatus, CallbackType, HessianFormat, MatrixFormat, ModelStatus, ObjSense, OptionType,
    VarType,
};
pub use error::{HighsError, HighsStatus, Result};
pub use expression::{qsum, Col, Constraint, LinearExpr, Row, INF};
pub use model::{version, Highs};
pub use oneshot::{solve_lp, solve_mip, solve_qp};
pub use parallel::SolveOutcome;
pub use problem::{LpProblem, MipProblem, QpProblem, Sparse};
pub use solution::{Basis, Solution};

/// The integer width HiGHS was compiled with (`i32` unless `HIGHSINT64`).
pub use highs_sys::HighsInt;

/// Raw FFI bindings. Anything not yet covered by the safe API is reachable here.
pub mod ffi {
    pub use highs_sys::*;
}
