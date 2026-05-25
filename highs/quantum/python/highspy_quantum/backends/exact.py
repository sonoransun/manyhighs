"""Brute-force exact backend.

Enumerates all 2^n assignments. Used as ground truth for the test suite and
as the POC's exact-value oracle on tiny instances. Refuses to run on more
than 24 variables (~16M evaluations is already several seconds in Python).
"""
from __future__ import annotations

import itertools
import time

import numpy as np

from ..model import Bqm
from .base import Sample

_MAX_VARS = 24


class ExactBackend:
    name = "exact"

    def solve(self, bqm: Bqm, time_limit_s: float) -> list[Sample]:
        if bqm.num_vars > _MAX_VARS:
            return []
        deadline = time.monotonic() + max(0.1, time_limit_s)
        n = bqm.num_vars
        best_x: np.ndarray | None = None
        best_obj = float("inf")
        # Build dense Q once.
        Q = np.zeros((n, n))
        for (i, j), coef in bqm.quadratic.items():
            Q[i, j] = coef
            Q[j, i] = coef
        for bits in itertools.product((0.0, 1.0), repeat=n):
            if time.monotonic() >= deadline:
                # Out of budget; return whatever we have. May be suboptimal.
                break
            x = np.array(bits, dtype=np.float64)
            obj = float(bqm.offset + bqm.linear @ x + 0.5 * x @ Q @ x)
            if obj < best_obj:
                best_obj = obj
                best_x = x
        if best_x is None:
            return []
        return [
            Sample(
                assignment=best_x,
                bqm_objective=best_obj,
                info={"method": "brute_force", "evaluated": 2 ** n},
            )
        ]
