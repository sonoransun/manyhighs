"""Structure detectors that tag a :class:`MipSubproblem` for specialized
QUBO reformulation. First-match wins.

Recognized tags:

* ``"qubo"``      — pure binary, no constraints. Trivial path.
* ``"set_partitioning"`` — every row is ``Ax = 1`` with 0/1 coefficients.
* ``"max_cut"``   — the canonical y_ij-linearization of a max-cut MIP.
* ``"tsp"``       — currently detected but falls back to the generic builder.

``build_for`` returns the specialized :class:`Bqm` for a detected tag, or
``None`` so the caller can use the generic penalty builder.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from .model import Bqm, MipSubproblem
from .reformulation import set_partitioning as ref_sp
from .reformulation import max_cut as ref_mc
from .reformulation import tsp as ref_tsp


def _is_pure_binary(sub: MipSubproblem) -> bool:
    if sub.num_vars == 0:
        return False
    if not np.all(sub.lower == 0.0):
        return False
    if not np.all(sub.upper == 1.0):
        return False
    return True


def _detect_qubo(sub: MipSubproblem) -> bool:
    return _is_pure_binary(sub) and sub.num_rows == 0


def _detect_set_partitioning(sub: MipSubproblem) -> bool:
    if not _is_pure_binary(sub):
        return False
    if sub.num_rows == 0:
        return False
    if not (np.all(sub.row_lower == 1.0) and np.all(sub.row_upper == 1.0)):
        return False
    # All coefficients must be 0 or 1.
    if sub.coef_value.size == 0:
        return False
    if not np.all((sub.coef_value == 0.0) | (sub.coef_value == 1.0)):
        return False
    return True


def _detect_max_cut(sub: MipSubproblem) -> bool:
    """The canonical y_ij-linearized max-cut: every row is one of four
    forms ``y - x_i - x_j ≤ 0``, ``y + x_i + x_j ≤ 2``, ``y - x_i + x_j ≥ 0``,
    ``y + x_i - x_j ≥ 0``, and the objective is linear-in-y only.

    Strict: requires num_rows % 4 == 0 and exactly two free variables in
    each row besides the y. We tolerate empty objective on x variables.
    """
    if not _is_pure_binary(sub):
        return False
    if sub.num_rows == 0 or sub.num_rows % 4 != 0:
        return False
    # Per-row size check: every row must have exactly 3 nonzeros.
    for r in range(sub.num_rows):
        start = int(sub.row_start[r])
        end = int(sub.row_start[r + 1])
        if end - start != 3:
            return False
    # Cheap check that ref_mc can recover it.
    bqm = ref_mc._try_recover(sub)
    return bqm is not None


def _detect_tsp(sub: MipSubproblem) -> bool:
    """Square assignment shape: n² binary vars with 2n equality rows of size n."""
    if not _is_pure_binary(sub):
        return False
    n_sq = sub.num_vars
    n = int(round(n_sq ** 0.5))
    if n < 3 or n * n != n_sq:
        return False
    if sub.num_rows != 2 * n:
        return False
    if not (np.all(sub.row_lower == 1.0) and np.all(sub.row_upper == 1.0)):
        return False
    return True


def detect(sub: MipSubproblem) -> str:
    """Return the structure tag, or empty string if no structure matches."""
    if _detect_qubo(sub):
        return "qubo"
    if _detect_max_cut(sub):
        return "max_cut"
    if _detect_set_partitioning(sub):
        return "set_partitioning"
    if _detect_tsp(sub):
        return "tsp"
    return ""


def build_for(tag: str, sub: MipSubproblem) -> Optional[Bqm]:
    """Return the specialized BQM for `tag`, or None to fall through."""
    if tag == "qubo":
        # Trivial: generic builder already handles no-constraint case correctly.
        return None
    if tag == "set_partitioning":
        return ref_sp.build(sub)
    if tag == "max_cut":
        return ref_mc.build(sub)
    if tag == "tsp":
        return ref_tsp.build(sub)
    return None
