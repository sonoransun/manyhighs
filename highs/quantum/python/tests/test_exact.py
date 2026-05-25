"""Brute-force backend ground-truth tests."""
from __future__ import annotations

import numpy as np

from highspy_quantum.backends.exact import ExactBackend
from highspy_quantum.model import Bqm


def test_exact_recovers_minimum():
    # min  -x0 - 2*x1 + 3*x0*x1  →  best is (0,1) → -2
    bqm = Bqm(num_vars=2, linear=np.array([-1.0, -2.0]))
    bqm.add_quadratic(0, 1, 3.0)
    backend = ExactBackend()
    samples = backend.solve(bqm, time_limit_s=5.0)
    assert samples
    s = samples[0]
    assert s.bqm_objective == -2.0
    np.testing.assert_array_equal(s.assignment, [0.0, 1.0])


def test_exact_refuses_large_problem():
    bqm = Bqm(num_vars=25)
    backend = ExactBackend()
    assert backend.solve(bqm, time_limit_s=1.0) == []
