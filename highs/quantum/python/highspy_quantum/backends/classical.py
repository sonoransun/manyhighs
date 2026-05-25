"""Classical fallback backend: simulated annealing on a Bqm.

Deliberately small and dependency-free (numpy only) so it ships in the base
package and works as the no-vendor-account default for the POC. Not a
research-grade SA — sufficient to validate the C++/Python plumbing
end-to-end and to give us a baseline for the vendor backends to beat.
"""
from __future__ import annotations

import time

import numpy as np

from ..model import Bqm
from .base import Sample


def _build_dense_q(bqm: Bqm) -> np.ndarray:
    """Build a symmetric n×n quadratic matrix (zero diagonal)."""
    n = bqm.num_vars
    Q = np.zeros((n, n))
    for (i, j), coef in bqm.quadratic.items():
        Q[i, j] = coef
        Q[j, i] = coef
    return Q


def _evaluate(bqm: Bqm, Q: np.ndarray, x: np.ndarray) -> float:
    return float(bqm.offset + bqm.linear @ x + 0.5 * x @ Q @ x)


class ClassicalBackend:
    name = "classical"

    def __init__(self, *, seed: int | None = None) -> None:
        self._rng = np.random.default_rng(seed)

    def solve(self, bqm: Bqm, time_limit_s: float) -> list[Sample]:
        deadline = time.monotonic() + max(0.05, time_limit_s)
        n = bqm.num_vars
        if n == 0:
            return [Sample(assignment=np.zeros(0), bqm_objective=bqm.offset, info={})]

        Q = _build_dense_q(bqm)
        # Multi-start SA: a handful of random initial points, anneal each.
        best_x: np.ndarray | None = None
        best_obj = float("inf")
        num_starts = 0
        # T_start chosen so a typical single-flip delta has ~50% accept rate.
        scale = max(1.0, float(np.abs(bqm.linear).sum() / max(1, n)) + Q.sum() / max(1, n * n))
        T_start = max(scale, 1.0)
        T_end = max(1e-3, T_start * 1e-3)

        while time.monotonic() < deadline:
            num_starts += 1
            x = self._rng.integers(0, 2, size=n).astype(np.float64)
            obj = _evaluate(bqm, Q, x)
            # Cooling schedule sized so each restart finishes well under the
            # remaining budget; we'll restart as long as time allows.
            steps = max(100, 50 * n)
            for k in range(steps):
                if time.monotonic() >= deadline:
                    break
                T = T_start * (T_end / T_start) ** (k / steps)
                i = int(self._rng.integers(0, n))
                # delta from flipping x[i]
                delta = (1 - 2 * x[i]) * (bqm.linear[i] + Q[i] @ x)
                if delta <= 0 or self._rng.random() < np.exp(-delta / T):
                    x[i] = 1 - x[i]
                    obj += delta
            if obj < best_obj:
                best_obj = obj
                best_x = x.copy()

        if best_x is None:
            return []
        return [
            Sample(
                assignment=best_x,
                bqm_objective=best_obj,
                info={"num_starts": num_starts, "method": "simulated_annealing"},
            )
        ]
