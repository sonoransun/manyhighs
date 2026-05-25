"""build_bqm_from_subproblem on known inputs."""
from __future__ import annotations

import numpy as np

from highspy_quantum.model import MipSubproblem, build_bqm_from_subproblem


def _empty_sub(num_vars: int, linear: list[float]) -> MipSubproblem:
    return MipSubproblem(
        num_vars=num_vars,
        num_rows=0,
        sense_multiplier=1.0,
        constant_offset=0.0,
        linear=np.array(linear, dtype=np.float64),
        lower=np.zeros(num_vars),
        upper=np.ones(num_vars),
        original_indices=np.arange(num_vars, dtype=np.int64),
        row_start=np.array([0], dtype=np.int64),
        col_index=np.zeros(0, dtype=np.int64),
        coef_value=np.zeros(0, dtype=np.float64),
        row_lower=np.zeros(0),
        row_upper=np.zeros(0),
        seed_full_solution=np.zeros(num_vars),
    )


def test_unconstrained_objective_pass_through():
    sub = _empty_sub(3, [1.0, -2.0, 3.0])
    bqm = build_bqm_from_subproblem(sub)
    assert bqm.num_vars == 3
    np.testing.assert_allclose(bqm.linear, [1.0, -2.0, 3.0])
    assert bqm.quadratic == {}
    # x=[0,1,0] should yield objective -2
    assert bqm.evaluate(np.array([0.0, 1.0, 0.0])) == -2.0


def test_max_sense_negates_objective():
    sub = _empty_sub(2, [1.0, 1.0])
    sub.sense_multiplier = -1.0
    bqm = build_bqm_from_subproblem(sub)
    np.testing.assert_allclose(bqm.linear, [-1.0, -1.0])


def test_equality_constraint_quadratic_expansion():
    # min x0 + x1 + x2  s.t. x0 + x1 + x2 == 2; penalty P=10
    sub = MipSubproblem(
        num_vars=3,
        num_rows=1,
        sense_multiplier=1.0,
        constant_offset=0.0,
        linear=np.array([1.0, 1.0, 1.0]),
        lower=np.zeros(3),
        upper=np.ones(3),
        original_indices=np.arange(3, dtype=np.int64),
        row_start=np.array([0, 3], dtype=np.int64),
        col_index=np.array([0, 1, 2], dtype=np.int64),
        coef_value=np.array([1.0, 1.0, 1.0]),
        row_lower=np.array([2.0]),
        row_upper=np.array([2.0]),
        seed_full_solution=np.zeros(3),
    )
    bqm = build_bqm_from_subproblem(sub, penalty=10.0)
    # On a feasible point (1,1,0): objective should equal original (=2) +
    # offset (=40 from 10*2^2) - (linear adjustments that cancel out)
    # Easiest correctness check: any feasible 0/1 assignment that sums to 2
    # should yield the same BQM value, and that value should be lower than
    # any infeasible one.
    feasible_values = [
        bqm.evaluate(np.array(x, dtype=np.float64))
        for x in [(1, 1, 0), (1, 0, 1), (0, 1, 1)]
    ]
    infeasible = bqm.evaluate(np.array([1.0, 1.0, 1.0]))  # sums to 3
    assert all(abs(v - feasible_values[0]) < 1e-9 for v in feasible_values)
    assert infeasible > feasible_values[0]
