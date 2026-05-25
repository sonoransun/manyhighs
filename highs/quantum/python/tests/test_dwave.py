"""D-Wave backend tests. No real cloud calls."""
from __future__ import annotations

import sys
from unittest import mock

import numpy as np
import pytest

from highspy_quantum.backends import get_backend
from highspy_quantum.backends.base import BackendUnavailable
from highspy_quantum.model import Bqm


_HAS_DIMOD = False
try:
    import dimod  # noqa: F401

    _HAS_DIMOD = True
except ImportError:
    pass


def test_unavailable_when_dimod_missing(monkeypatch):
    """If dimod isn't importable, __init__ must raise BackendUnavailable."""
    # Patch out dimod from sys.modules and block re-import.
    monkeypatch.setitem(sys.modules, "dimod", None)
    with pytest.raises(BackendUnavailable, match="dimod"):
        get_backend("dwave")


@pytest.mark.skipif(not _HAS_DIMOD, reason="dimod not installed")
def test_solve_uses_fallback_without_token(monkeypatch):
    """No DWAVE_API_TOKEN → must use the SA fallback and return samples."""
    monkeypatch.setenv("DWAVE_API_TOKEN", "")
    backend = get_backend("dwave")
    # min x0 + x1 + x0 x1  → optimum at (0,0).
    bqm = Bqm(num_vars=2, linear=np.array([1.0, 1.0]))
    bqm.add_quadratic(0, 1, 1.0)
    samples = backend.solve(bqm, time_limit_s=1.0)
    assert samples
    best = min(samples, key=lambda s: s.bqm_objective)
    assert best.bqm_objective == 0.0
    assert "SimulatedAnnealing" in best.info["sampler"]


@pytest.mark.skipif(not _HAS_DIMOD, reason="dimod not installed")
def test_sampler_called_with_dimod_bqm(monkeypatch):
    """Verify the sampler receives a dimod.BinaryQuadraticModel of the right shape."""
    monkeypatch.setenv("DWAVE_API_TOKEN", "")
    backend = get_backend("dwave")

    received: dict = {}
    fake_sampleset = mock.MagicMock()
    fake_sampleset.lowest.return_value.record = []

    def fake_sample(dimod_bqm, **kwargs):
        received["bqm"] = dimod_bqm
        received["kwargs"] = kwargs
        return fake_sampleset

    fake_sampler = mock.MagicMock()
    fake_sampler.sample = fake_sample

    monkeypatch.setattr(
        backend, "_select_sampler", lambda n: (fake_sampler, "FakeSA")
    )

    bqm = Bqm(num_vars=3, linear=np.array([1.0, -2.0, 3.0]))
    bqm.add_quadratic(0, 1, 0.5)
    backend.solve(bqm, time_limit_s=1.0)

    sent = received["bqm"]
    assert sent.num_variables == 3
    # The linear coefficient is what we set.
    assert sent.get_linear(0) == 1.0
    assert sent.get_linear(1) == -2.0
    # The interaction we added.
    assert sent.get_quadratic(0, 1) == 0.5
