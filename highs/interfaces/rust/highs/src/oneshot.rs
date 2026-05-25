//! One-shot convenience: build, solve, and extract in a single call without
//! managing a [`Highs`] instance. These silence solver output and reuse the
//! same load/extract paths as the stateful API. The raw `Highs_lpCall` /
//! `Highs_mipCall` / `Highs_qpCall` entry points remain available via
//! [`crate::ffi`].

use crate::error::Result;
use crate::model::Highs;
use crate::parallel::SolveOutcome;
use crate::problem::{LpProblem, MipProblem, QpProblem};

/// Solve a linear program and return its outcome.
pub fn solve_lp(lp: &LpProblem) -> Result<SolveOutcome> {
    let mut h = Highs::new().silenced();
    h.pass_lp(lp)?;
    outcome(&mut h)
}

/// Solve a mixed-integer program and return its outcome.
pub fn solve_mip(mip: &MipProblem) -> Result<SolveOutcome> {
    let mut h = Highs::new().silenced();
    h.pass_mip(mip)?;
    outcome(&mut h)
}

/// Solve a convex quadratic program and return its outcome.
pub fn solve_qp(qp: &QpProblem) -> Result<SolveOutcome> {
    let mut h = Highs::new().silenced();
    h.pass_qp(qp)?;
    outcome(&mut h)
}

fn outcome(h: &mut Highs) -> Result<SolveOutcome> {
    let status = h.run()?;
    Ok(SolveOutcome {
        status,
        objective: h.objective_value(),
        solution: h.solution()?,
    })
}
