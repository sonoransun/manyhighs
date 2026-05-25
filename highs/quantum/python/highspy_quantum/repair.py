"""Feasibility-projection / round-and-repair pass.

When a backend returns a sample that violates constraints (penalty too weak,
SA got stuck in a local minimum, noisy QPU readout, etc.), this module
attempts to greedily flip variables until the sample is feasible. Cheap to
run, often turns a near-feasible quantum sample into a usable HiGHS incumbent.

Algorithm
---------
1. Score current violation: sum of max(0, lo - aᵀx)² + max(0, aᵀx - hi)² across rows.
2. While violation > 0 and not over budget:
   a. For each variable, compute the marginal change in violation if we flip it.
   b. If any flip strictly reduces violation, take the best one.
   c. Otherwise stop — we're at a local minimum.
3. Return the (possibly partially-) repaired assignment plus the new
   feasibility status.

This is a deliberately simple heuristic. It guarantees no regression in
violation; it does *not* guarantee feasibility (the QUBO may be infeasible
in a global sense for the given fixings). If the original assignment was
feasible we return it untouched.
"""
from __future__ import annotations

import time
from typing import Tuple

import numpy as np

from .model import MipSubproblem


def _row_violation(
    sub: MipSubproblem, row: int, assignment: np.ndarray
) -> float:
    start = int(sub.row_start[row])
    end = int(sub.row_start[row + 1])
    if start == end:
        return 0.0
    activity = float(
        sub.coef_value[start:end] @ assignment[sub.col_index[start:end]]
    )
    lo = float(sub.row_lower[row])
    hi = float(sub.row_upper[row])
    v = 0.0
    if np.isfinite(lo) and activity < lo:
        v += (lo - activity) ** 2
    if np.isfinite(hi) and activity > hi:
        v += (activity - hi) ** 2
    return v


def _total_violation(sub: MipSubproblem, assignment: np.ndarray) -> float:
    return sum(_row_violation(sub, r, assignment) for r in range(sub.num_rows))


def _rows_touching_var(sub: MipSubproblem, var: int) -> list[int]:
    """Index of rows that have a nonzero coefficient in column `var`.

    Linear scan over the row arrays. For Sprint 0 this is fine; if it ever
    becomes hot we can precompute a column-indexed adjacency once per call.
    """
    rows = []
    for r in range(sub.num_rows):
        start = int(sub.row_start[r])
        end = int(sub.row_start[r + 1])
        if var in sub.col_index[start:end]:
            rows.append(r)
    return rows


def repair(
    sub: MipSubproblem,
    assignment: np.ndarray,
    *,
    time_limit_s: float = 1.0,
    max_passes: int = 200,
) -> Tuple[np.ndarray, bool, float]:
    """Greedy-flip repair. Returns (assignment, feasible, final_violation)."""
    x = assignment.copy()
    # Snap to {0, 1}: quantum samples should already be binary but be defensive.
    x = np.clip(np.round(x), 0.0, 1.0)
    if sub.num_rows == 0:
        return x, True, 0.0
    violation = _total_violation(sub, x)
    if violation == 0.0:
        return x, True, 0.0

    # Precompute var → list of rows once (huge speedup over per-pass scans).
    var_rows: list[list[int]] = [[] for _ in range(sub.num_vars)]
    for r in range(sub.num_rows):
        start = int(sub.row_start[r])
        end = int(sub.row_start[r + 1])
        for k in range(start, end):
            var_rows[int(sub.col_index[k])].append(r)

    deadline = time.monotonic() + max(0.01, time_limit_s)
    for _ in range(max_passes):
        if time.monotonic() >= deadline:
            break
        best_delta = 0.0
        best_var = -1
        for v in range(sub.num_vars):
            touched = var_rows[v]
            if not touched:
                continue
            before = sum(_row_violation(sub, r, x) for r in touched)
            x[v] = 1.0 - x[v]
            after = sum(_row_violation(sub, r, x) for r in touched)
            x[v] = 1.0 - x[v]
            delta = after - before
            if delta < best_delta:
                best_delta = delta
                best_var = v
        if best_var < 0:
            # No single flip improves; we're stuck.
            break
        x[best_var] = 1.0 - x[best_var]
        violation += best_delta
        if violation <= 0.0:
            violation = 0.0
            break

    return x, violation == 0.0, violation
