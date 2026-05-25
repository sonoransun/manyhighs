"""Greedy round-and-repair on a few known instances."""
from __future__ import annotations

import numpy as np

from highspy_quantum.model import MipSubproblem
from highspy_quantum.repair import repair


def _sub_eq_sum_to_2_of_3() -> MipSubproblem:
    """min x0+x1+x2 s.t. x0+x1+x2 == 2, all binary."""
    return MipSubproblem(
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


def test_repair_already_feasible_passthrough():
    sub = _sub_eq_sum_to_2_of_3()
    x = np.array([1.0, 1.0, 0.0])
    repaired, feasible, violation = repair(sub, x)
    assert feasible
    assert violation == 0.0
    np.testing.assert_array_equal(repaired, x)


def test_repair_one_flip_recovery():
    # All-zero violates by 4 (need sum 2, got 0); a single flip recovers.
    # Actually one flip from (0,0,0) goes to violation (2-1)^2 = 1, still
    # infeasible. Two flips → feasible. Repair must do both.
    sub = _sub_eq_sum_to_2_of_3()
    x = np.zeros(3)
    repaired, feasible, _ = repair(sub, x)
    assert feasible
    assert int(repaired.sum()) == 2


def test_repair_no_constraints_is_trivial():
    sub = MipSubproblem(
        num_vars=3,
        num_rows=0,
        sense_multiplier=1.0,
        constant_offset=0.0,
        linear=np.array([1.0, 1.0, 1.0]),
        lower=np.zeros(3),
        upper=np.ones(3),
        original_indices=np.arange(3, dtype=np.int64),
        row_start=np.array([0], dtype=np.int64),
        col_index=np.zeros(0, dtype=np.int64),
        coef_value=np.zeros(0),
        row_lower=np.zeros(0),
        row_upper=np.zeros(0),
        seed_full_solution=np.zeros(3),
    )
    x = np.array([0.5, 0.0, 1.0])  # non-binary input deliberately
    repaired, feasible, violation = repair(sub, x)
    assert feasible
    assert violation == 0.0
    # Repair snaps the 0.5 to nearest integer (rounded; numpy.round → 0).
    assert repaired.tolist() == [0.0, 0.0, 1.0]
