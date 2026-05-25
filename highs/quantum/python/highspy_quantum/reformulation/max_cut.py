"""Max-cut QUBO formulation.

When the MIP is the standard linearized max-cut (variables x_i ∈ {0,1} for
each vertex; y_ij ∈ {0,1} for each edge bounded by
``y_ij ≤ x_i + x_j``, ``y_ij ≤ 2 - x_i - x_j``, ``y_ij ≥ x_i - x_j``,
``y_ij ≥ x_j - x_i``; objective ``min -sum_e w_e y_e``), we want to
recover the pure-vertex QUBO

  min -sum_{(i,j)} w_ij · (x_i + x_j - 2 x_i x_j)
  = const + sum coupling-terms

which has *no* constraints — every binary assignment is feasible, so the
penalty failure mode goes away.

The recovery happens by inspecting the linearization rows and recovering
``w_e`` per edge. If the MIP doesn't fit the canonical shape, the caller
must fall back to the generic penalty builder.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from ..model import Bqm, MipSubproblem


def _try_recover(sub: MipSubproblem) -> Optional[Bqm]:
    """Best-effort recovery from a y_ij-linearized max-cut MIP. None on failure."""
    # We need exactly 4 rows per edge variable y_ij. The detector should
    # already have validated the basic shape; this builder just extracts.
    # For Sprint 4 we limit support to the strictest canonical form: every
    # variable is binary, the objective is linear-in-y only, and rows come
    # in groups of 4 per edge.
    if sub.num_rows == 0 or sub.num_vars == 0:
        return None
    if sub.num_rows % 4 != 0:
        return None
    num_edges = sub.num_rows // 4

    # Build a row-keyed coefficient lookup for fast inspection.
    # Each row: list of (col, value) tuples.
    rows: list[list[tuple[int, float]]] = []
    for r in range(sub.num_rows):
        s = int(sub.row_start[r])
        e = int(sub.row_start[r + 1])
        rows.append(
            list(zip([int(c) for c in sub.col_index[s:e]],
                     [float(v) for v in sub.coef_value[s:e]]))
        )

    # Recover edge weights: for each y variable we expect one row of the form
    # y - x_i - x_j ≤ 0 and so on. The objective coefficient on y is -w_e
    # under min sense_multiplier=1.
    edges: list[tuple[int, int, float]] = []
    for e_idx in range(num_edges):
        block = rows[4 * e_idx : 4 * e_idx + 4]
        # Find the y variable: it appears in all four rows. Find x_i, x_j as
        # the two non-y vars whose signs flip across the rows.
        y_candidates = set(block[0]) & set(block[1])
        # Simpler: y is the var that appears in EVERY row of the block.
        col_sets = [set(c for c, _ in row) for row in block]
        common = col_sets[0] & col_sets[1] & col_sets[2] & col_sets[3]
        if len(common) != 1:
            return None
        (y,) = common
        # The other vars in any of these rows must be x_i, x_j.
        others = (col_sets[0] | col_sets[1] | col_sets[2] | col_sets[3]) - {y}
        if len(others) != 2:
            return None
        i, j = sorted(others)
        # Edge weight = -objective coefficient on y under min sense.
        sense = float(sub.sense_multiplier)
        w = -float(sub.linear[y]) * sense
        if w == 0.0:
            continue
        edges.append((i, j, w))

    if not edges:
        return None

    # Build the QUBO over the vertex variables only. Reformulation:
    #   x_i + x_j - 2 x_i x_j  (binary XOR)
    # Sum_e w_e · (x_i + x_j - 2 x_i x_j) with min sense (negate for max).
    # Map QUBO indices to the original vertex columns. The y variables stay
    # at their incumbent (we'll need to populate them in seed_full_solution
    # before returning; that happens in detect() / cli.py).
    vertex_set: set[int] = set()
    for i, j, _ in edges:
        vertex_set.add(i)
        vertex_set.add(j)
    bqm = Bqm(num_vars=sub.num_vars, offset=sub.constant_offset)
    # We minimize -sum w_e (x_i + x_j - 2 x_i x_j) per max-cut convention.
    for i, j, w in edges:
        coef = -w * sub.sense_multiplier
        bqm.add_linear(i, coef)
        bqm.add_linear(j, coef)
        bqm.add_quadratic(i, j, -2.0 * coef)
    # y variables: drop their cost since they're determined by x. Leave the
    # bqm linear[y] at zero (already there).
    return bqm


def build(sub: MipSubproblem) -> Bqm:
    """Build a max-cut BQM. Falls back to None-handling at the caller if shape
    doesn't match the canonical form."""
    recovered = _try_recover(sub)
    if recovered is not None:
        return recovered
    # Shape didn't recover cleanly — caller should fall through to generic
    # builder. We import locally to avoid a cycle at module load.
    from ..model import build_bqm_from_subproblem

    return build_bqm_from_subproblem(sub)
