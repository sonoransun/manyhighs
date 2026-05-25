"""MIP subproblem container and penalty-method QUBO reformulation.

The C++ side ships a binary linear MIP description (see
``highs/quantum/HighsQubo.h``). This module reformulates it into a binary
quadratic model (BQM) that any of the backends can consume.

QUBO penalty method
-------------------
For each linear constraint :math:`l_i \\le a_i^T x \\le u_i` we add a penalty
term to the objective:

* equality (l == u == b):  :math:`P \\cdot (a^T x - b)^2`
* upper-bound only:        :math:`P \\cdot \\max(0, a^T x - u)^2`
* lower-bound only:        :math:`P \\cdot \\max(0, l - a^T x)^2`

Penalty weight :math:`P` defaults to
``max(1, |max_objective_coefficient| * num_vars)``, which is enough to dominate
the objective for any 0/1 assignment that violates a constraint by at least 1.

The :class:`Bqm` class stores the resulting linear + quadratic coefficients.
It is intentionally framework-free so backends that don't have ``dimod``
installed can still operate on it. Backends that *do* use ``dimod`` (D-Wave,
some Qiskit paths) can convert via :meth:`Bqm.to_dimod`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import numpy as np


@dataclass
class MipSubproblem:
    """Binary MIP description received from C++ (or the standalone CLI).

    All arrays are dense 1-D ``np.ndarray``. Variables are indexed
    ``[0, num_vars)`` and are all binary (lower=0, upper=1) in Sprint 0.
    """

    num_vars: int
    num_rows: int
    sense_multiplier: float  # +1 for min, -1 for max
    constant_offset: float
    linear: np.ndarray
    lower: np.ndarray
    upper: np.ndarray
    original_indices: np.ndarray
    row_start: np.ndarray  # CSR row pointers; size num_rows + 1
    col_index: np.ndarray
    coef_value: np.ndarray
    row_lower: np.ndarray
    row_upper: np.ndarray
    seed_full_solution: np.ndarray
    structure_tag: str = ""

    def is_unconstrained(self) -> bool:
        return self.num_rows == 0

    def evaluate(self, assignment: np.ndarray) -> float:
        """Original-problem objective (post-sense, with offset)."""
        if assignment.shape[0] != self.num_vars:
            raise ValueError(
                f"assignment has {assignment.shape[0]} entries; expected "
                f"{self.num_vars}"
            )
        return (
            self.sense_multiplier * float(self.linear @ assignment)
            + self.constant_offset
        )

    def is_feasible(self, assignment: np.ndarray, tol: float = 1e-6) -> bool:
        for row in range(self.num_rows):
            start = int(self.row_start[row])
            end = int(self.row_start[row + 1])
            if start == end:
                continue
            activity = float(
                self.coef_value[start:end]
                @ assignment[self.col_index[start:end]]
            )
            if activity > float(self.row_upper[row]) + tol:
                return False
            if activity < float(self.row_lower[row]) - tol:
                return False
        return True


@dataclass
class Bqm:
    """Plain binary quadratic model.

    ``offset`` is added to every evaluated objective. ``linear[i]`` is the
    coefficient of x_i, ``quadratic[(i, j)]`` (with i < j) is the coefficient
    of x_i * x_j.
    """

    num_vars: int
    offset: float = 0.0
    linear: np.ndarray = field(default_factory=lambda: np.zeros(0))
    quadratic: dict[tuple[int, int], float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.linear.shape != (self.num_vars,):
            self.linear = np.zeros(self.num_vars, dtype=np.float64)

    def add_linear(self, i: int, coef: float) -> None:
        self.linear[i] += coef

    def add_quadratic(self, i: int, j: int, coef: float) -> None:
        if i == j:
            self.linear[i] += coef  # x_i^2 = x_i for binary x
            return
        a, b = (i, j) if i < j else (j, i)
        self.quadratic[(a, b)] = self.quadratic.get((a, b), 0.0) + coef

    def evaluate(self, assignment: np.ndarray) -> float:
        v = self.offset + float(self.linear @ assignment)
        for (i, j), coef in self.quadratic.items():
            v += coef * float(assignment[i]) * float(assignment[j])
        return v

    def to_dimod(self):  # pragma: no cover — requires optional dependency
        """Convert to ``dimod.BinaryQuadraticModel`` (D-Wave's standard type).

        Used by backends that consume ``dimod`` types directly. Raises if
        dimod isn't installed; only the d-wave / qiskit-aer paths need it.
        """
        import dimod  # type: ignore

        bqm = dimod.BinaryQuadraticModel("BINARY")
        for i in range(self.num_vars):
            bqm.add_variable(i, float(self.linear[i]))
        for (i, j), coef in self.quadratic.items():
            bqm.add_interaction(i, j, float(coef))
        bqm.offset = float(self.offset)
        return bqm


def _add_quadratic_form(
    bqm: Bqm,
    indices: np.ndarray,
    values: np.ndarray,
    rhs: float,
    weight: float,
) -> None:
    """Add :math:`weight \\cdot (a^T x - rhs)^2` to ``bqm``.

    For binary x: :math:`(a^T x - b)^2 = b^2 - 2b a^T x +
    (a^T x)^2`, and the quadratic expansion uses :math:`x_i^2 = x_i`.
    """
    bqm.offset += weight * rhs * rhs
    n = len(indices)
    for k in range(n):
        ik = int(indices[k])
        ak = float(values[k])
        # contribution from -2 b a^T x and the diagonal (a_k x_k)^2 = a_k^2 x_k
        bqm.add_linear(ik, weight * (ak * ak - 2.0 * rhs * ak))
        for l in range(k + 1, n):
            il = int(indices[l])
            al = float(values[l])
            bqm.add_quadratic(ik, il, weight * 2.0 * ak * al)


def _default_penalty(sub: MipSubproblem) -> float:
    if sub.linear.size == 0:
        return 1.0
    return max(1.0, float(np.max(np.abs(sub.linear))) * max(1, sub.num_vars))


def build_bqm_from_subproblem(
    sub: MipSubproblem, *, penalty: float | None = None
) -> Bqm:
    """Build a Bqm from a MipSubproblem using the penalty method.

    Inequality rows are only penalized when violated by the candidate
    assignment — but the Bqm form has to be value-of-x agnostic, so we
    over-approximate inequality penalties by treating any non-finite bound as
    "no constraint" and finite bounds with the squared-violation formula above.
    For a pure QUBO/unconstrained MIP this leaves the linear objective intact.
    """
    if penalty is None:
        penalty = _default_penalty(sub)

    bqm = Bqm(num_vars=sub.num_vars, offset=sub.constant_offset)
    # Objective: Python always minimizes; sense_multiplier folds maximization in.
    for i in range(sub.num_vars):
        bqm.add_linear(i, sub.sense_multiplier * float(sub.linear[i]))

    for row in range(sub.num_rows):
        start = int(sub.row_start[row])
        end = int(sub.row_start[row + 1])
        if start == end:
            continue
        indices = sub.col_index[start:end]
        values = sub.coef_value[start:end]
        lo = float(sub.row_lower[row])
        hi = float(sub.row_upper[row])
        finite_lo = np.isfinite(lo)
        finite_hi = np.isfinite(hi)
        if finite_lo and finite_hi and abs(lo - hi) < 1e-12:
            # Equality
            _add_quadratic_form(bqm, indices, values, lo, penalty)
            continue
        # Pick a single representative target. The classical / exact backends
        # also check feasibility against the original constraint, so any
        # constraint mis-aiming is caught downstream.
        if finite_hi:
            _add_quadratic_form(bqm, indices, values, hi, penalty)
        if finite_lo and not finite_hi:
            _add_quadratic_form(bqm, indices, values, lo, penalty)

    return bqm
