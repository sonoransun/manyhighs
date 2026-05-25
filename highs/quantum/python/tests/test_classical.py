"""Classical SA backend on a tiny known-optimum problem."""
from __future__ import annotations

import numpy as np

from highspy_quantum.backends.classical import ClassicalBackend
from highspy_quantum.model import Bqm


def test_sa_solves_2var_problem():
    # min  x0 + x1 + x0*x1  →  optimal at x=(0,0) with objective 0.
    bqm = Bqm(num_vars=2, linear=np.array([1.0, 1.0]))
    bqm.add_quadratic(0, 1, 1.0)
    backend = ClassicalBackend(seed=0)
    samples = backend.solve(bqm, time_limit_s=1.0)
    assert samples, "SA returned no samples"
    best = min(samples, key=lambda s: s.bqm_objective)
    assert best.bqm_objective == 0.0
    np.testing.assert_array_equal(best.assignment, [0.0, 0.0])


def test_sa_solves_3var_max_cut():
    # max-cut on a triangle: minimize -(x0+x1+x2) + 2*(x0*x1 + x1*x2 + x0*x2),
    # optimal value -1 at any (1,0,1)/(0,1,0)/(1,1,0) etc. — assignments with
    # exactly one or two "ones" produce cuts of weight 2 → objective -2+2=0
    # wait let's recompute: f(x) = -(x0+x1+x2) + 2*(x0 x1 + x1 x2 + x0 x2).
    # On (1,0,0): -1 + 0 = -1.  On (1,1,0): -2 + 2 = 0.  Best is single-1.
    bqm = Bqm(num_vars=3, linear=np.array([-1.0, -1.0, -1.0]))
    bqm.add_quadratic(0, 1, 2.0)
    bqm.add_quadratic(1, 2, 2.0)
    bqm.add_quadratic(0, 2, 2.0)
    backend = ClassicalBackend(seed=42)
    samples = backend.solve(bqm, time_limit_s=1.0)
    best = min(samples, key=lambda s: s.bqm_objective)
    assert best.bqm_objective == -1.0
    assert int(best.assignment.sum()) == 1
