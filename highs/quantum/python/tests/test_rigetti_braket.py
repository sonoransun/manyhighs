"""Smoke tests for Rigetti / Braket backends. Real SDKs aren't installed in
CI — these check the `BackendUnavailable` failure mode and the BQM→Ising
conversion utility (which has no SDK dependency)."""
from __future__ import annotations

import sys

import numpy as np
import pytest

from highspy_quantum.backends import get_backend
from highspy_quantum.backends.base import BackendUnavailable
from highspy_quantum.backends.rigetti import _bqm_to_ising
from highspy_quantum.model import Bqm


def test_rigetti_unavailable(monkeypatch):
    monkeypatch.setitem(sys.modules, "pyquil", None)
    with pytest.raises(BackendUnavailable, match="pyquil"):
        get_backend("rigetti")


def test_braket_unavailable(monkeypatch):
    # braket.circuits is what __init__ imports.
    monkeypatch.setitem(sys.modules, "braket.circuits", None)
    with pytest.raises(BackendUnavailable, match="amazon-braket"):
        get_backend("braket")


def test_bqm_to_ising_offset_and_signs():
    """min x0 + x1 + x0*x1, x in {0,1}^2.

    Re-derived by hand to verify the spin transform:
      x = (1 - z) / 2
      x0 + x1 = 1 - (z0 + z1)/2
      x0*x1 = (1 - z0 - z1 + z0*z1) / 4

    So the Ising form (sum over spins) should be
      offset = 1 + 0.25 = 1.25
      h0 = -0.5 - 0.25 = -0.75
      h1 = -0.5 - 0.25 = -0.75
      J(0,1) = 0.25
    """
    bqm = Bqm(num_vars=2, linear=np.array([1.0, 1.0]))
    bqm.add_quadratic(0, 1, 1.0)
    h, J, offset = _bqm_to_ising(bqm)
    assert offset == 1.25
    np.testing.assert_allclose(h, [-0.75, -0.75])
    assert J == {(0, 1): 0.25}
