"""Structure detectors + specialized builders."""
from __future__ import annotations

import numpy as np
import pytest

from highspy_quantum import structure
from highspy_quantum.model import MipSubproblem


def _make(
    *, num_vars: int, num_rows: int, linear: list[float],
    row_start: list[int], col_index: list[int], coef_value: list[float],
    row_lower: list[float], row_upper: list[float],
) -> MipSubproblem:
    return MipSubproblem(
        num_vars=num_vars,
        num_rows=num_rows,
        sense_multiplier=1.0,
        constant_offset=0.0,
        linear=np.array(linear, dtype=np.float64),
        lower=np.zeros(num_vars),
        upper=np.ones(num_vars),
        original_indices=np.arange(num_vars, dtype=np.int64),
        row_start=np.array(row_start, dtype=np.int64),
        col_index=np.array(col_index, dtype=np.int64),
        coef_value=np.array(coef_value, dtype=np.float64),
        row_lower=np.array(row_lower, dtype=np.float64),
        row_upper=np.array(row_upper, dtype=np.float64),
        seed_full_solution=np.zeros(num_vars),
    )


def test_detect_qubo_is_unconstrained_binary():
    sub = _make(
        num_vars=3, num_rows=0, linear=[1.0, -1.0, 2.0],
        row_start=[0], col_index=[], coef_value=[],
        row_lower=[], row_upper=[],
    )
    assert structure.detect(sub) == "qubo"


def test_detect_set_partitioning():
    # 2 rows, 3 cols. Row 0: x0 + x1 = 1. Row 1: x1 + x2 = 1.
    sub = _make(
        num_vars=3, num_rows=2, linear=[2.0, 3.0, 5.0],
        row_start=[0, 2, 4],
        col_index=[0, 1, 1, 2],
        coef_value=[1.0, 1.0, 1.0, 1.0],
        row_lower=[1.0, 1.0], row_upper=[1.0, 1.0],
    )
    assert structure.detect(sub) == "set_partitioning"


def test_set_partitioning_builder_prefers_feasible_assignments():
    sub = _make(
        num_vars=3, num_rows=2, linear=[2.0, 3.0, 5.0],
        row_start=[0, 2, 4],
        col_index=[0, 1, 1, 2],
        coef_value=[1.0, 1.0, 1.0, 1.0],
        row_lower=[1.0, 1.0], row_upper=[1.0, 1.0],
    )
    bqm = structure.build_for("set_partitioning", sub)
    assert bqm is not None
    # Feasible point: (1, 0, 1) sums to 1 in each row; objective = 2+0+5 = 7.
    # Penalty term is zero on feasible points → bqm.evaluate should give 7.
    # (Plus the constant offset from sum_i P · 1 — that's an irrelevant
    # constant, so we just compare relative ordering.)
    feasible = bqm.evaluate(np.array([1.0, 0.0, 1.0]))
    other_feasible = bqm.evaluate(np.array([0.0, 1.0, 0.0]))  # 0+3+0 = 3
    infeasible = bqm.evaluate(np.array([1.0, 1.0, 1.0]))      # both rows sum to 2
    assert other_feasible < feasible < infeasible


def test_detect_misses_continuous_or_general_int():
    sub = MipSubproblem(
        num_vars=2, num_rows=0, sense_multiplier=1.0, constant_offset=0.0,
        linear=np.array([1.0, 1.0]),
        lower=np.array([0.0, 0.0]),
        upper=np.array([5.0, 1.0]),  # not binary
        original_indices=np.arange(2, dtype=np.int64),
        row_start=np.array([0], dtype=np.int64),
        col_index=np.zeros(0, dtype=np.int64),
        coef_value=np.zeros(0),
        row_lower=np.zeros(0), row_upper=np.zeros(0),
        seed_full_solution=np.zeros(2),
    )
    assert structure.detect(sub) == ""
