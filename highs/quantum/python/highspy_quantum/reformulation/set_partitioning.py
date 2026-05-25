"""Set-partitioning QUBO formulation.

For ``min cᵀx s.t. Ax = 1, x ∈ {0,1}^n`` with A ∈ {0, 1}^{m×n}, the standard
QUBO is

  H(x) = cᵀx + P · sum_i (sum_{j in row_i} x_j - 1)²

where P is large enough to dominate any single feasibility violation. Each
row expansion produces quadratic terms x_j x_k for variables in the same row;
the diagonal x_j² = x_j collapses into linear coefficients.
"""
from __future__ import annotations

import numpy as np

from ..model import Bqm, MipSubproblem


def build(sub: MipSubproblem, *, penalty: float | None = None) -> Bqm:
    if penalty is None:
        # Dominate the worst-case |objective| by a factor of n+1 — same heuristic
        # used in the generic penalty path, but tighter because we know the
        # constraints are =1.
        max_abs = float(np.max(np.abs(sub.linear))) if sub.linear.size else 1.0
        penalty = max(1.0, max_abs * max(1, sub.num_vars + 1))

    bqm = Bqm(num_vars=sub.num_vars, offset=sub.constant_offset)

    # Objective (minimization; sense_multiplier already folds maximization in).
    for i in range(sub.num_vars):
        bqm.add_linear(i, sub.sense_multiplier * float(sub.linear[i]))

    # For each row: P · (sum_j x_j - 1)² where j ranges over the row's nonzeros.
    # Expansion: P · ((sum x_j)² - 2 sum x_j + 1)
    #          = P · (sum x_j² + 2 sum_{j<k} x_j x_k - 2 sum x_j + 1)
    #          = P · (sum x_j + 2 sum_{j<k} x_j x_k - 2 sum x_j + 1)
    #          = P · (-sum x_j + 2 sum_{j<k} x_j x_k + 1)
    for row in range(sub.num_rows):
        start = int(sub.row_start[row])
        end = int(sub.row_start[row + 1])
        if start == end:
            continue
        indices = [int(x) for x in sub.col_index[start:end]]
        bqm.offset += penalty
        for j in indices:
            bqm.add_linear(j, -penalty)
        for a in range(len(indices)):
            for b in range(a + 1, len(indices)):
                bqm.add_quadratic(indices[a], indices[b], 2.0 * penalty)
    return bqm
