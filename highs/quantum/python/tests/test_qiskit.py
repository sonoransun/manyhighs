"""Qiskit backend tests. Stays within qiskit_optimization's QuadraticProgram
shape — no actual QAOA runs (would require qiskit-aer to be installed)."""
from __future__ import annotations

import sys

import numpy as np
import pytest

from highspy_quantum.backends import get_backend
from highspy_quantum.backends.base import BackendUnavailable
from highspy_quantum.model import Bqm


_HAS_QO = False
try:
    import qiskit_optimization  # noqa: F401

    _HAS_QO = True
except ImportError:
    pass


def test_unavailable_when_qiskit_optimization_missing(monkeypatch):
    monkeypatch.setitem(sys.modules, "qiskit_optimization", None)
    with pytest.raises(BackendUnavailable, match="qiskit-optimization"):
        get_backend("qiskit")


@pytest.mark.skipif(not _HAS_QO, reason="qiskit-optimization not installed")
def test_bqm_to_quadratic_program():
    """Independent of any sampler: just verify the QP shape we build."""
    from highspy_quantum.backends.qiskit import _build_quadratic_program

    bqm = Bqm(num_vars=3, linear=np.array([1.0, -2.0, 3.0]))
    bqm.add_quadratic(0, 1, 0.5)
    bqm.add_quadratic(1, 2, -0.25)
    bqm.offset = 0.75

    qp = _build_quadratic_program(bqm)
    assert qp.get_num_vars() == 3
    obj = qp.objective
    assert obj.constant == 0.75
    linear_arr = obj.linear.to_array()
    np.testing.assert_allclose(linear_arr, [1.0, -2.0, 3.0])
