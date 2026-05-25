"""IBM Qiskit Optimization (QAOA) backend.

Default execution path uses ``qiskit_aer``'s primitive sampler for a
local state-vector simulation — no IBMQ credentials required, fine for
small problems (~20 binary variables).

Real-hardware path activates when ``IBMQ_TOKEN`` is in the environment AND
the user passes ``--qiskit-backend=<device>`` in ``quantum_extra_args``.
That path goes through ``qiskit_ibm_runtime.Sampler`` and queues a job on
the named device; expect long latencies.

Sizing
------
Aer's state-vector simulator stores 2^n complex amplitudes, so memory blows
up around n=25. We refuse anything above ``_AER_MAX_VARS`` (20 by default;
override via ``HIGHS_QUANTUM_QISKIT_MAX_AER_VARS``). Real hardware caps at
``_HW_MAX_VARS`` (50).
"""
from __future__ import annotations

import os
import time
from typing import Any

import numpy as np

from ..model import Bqm
from .base import BackendUnavailable, Sample

_AER_MAX_VARS = int(os.environ.get("HIGHS_QUANTUM_QISKIT_MAX_AER_VARS", "20"))
_HW_MAX_VARS = 50


def _parse_extra(extra: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for tok in extra.split():
        if tok.startswith("--") and "=" in tok:
            k, v = tok[2:].split("=", 1)
            out[k] = v
    return out


def _build_quadratic_program(bqm: Bqm):
    """Bqm → qiskit_optimization.QuadraticProgram (minimization)."""
    from qiskit_optimization import QuadraticProgram

    qp = QuadraticProgram(name="highs_quantum_qubo")
    for i in range(bqm.num_vars):
        qp.binary_var(name=f"x{i}")
    linear = {f"x{i}": float(bqm.linear[i]) for i in range(bqm.num_vars)}
    quadratic = {
        (f"x{i}", f"x{j}"): float(coef) for (i, j), coef in bqm.quadratic.items()
    }
    qp.minimize(linear=linear, quadratic=quadratic, constant=float(bqm.offset))
    return qp


class QiskitBackend:
    name = "qiskit"

    def __init__(self) -> None:
        try:
            import qiskit_optimization  # noqa: F401
        except ImportError as e:
            raise BackendUnavailable(
                "Qiskit backend requires 'qiskit-optimization' (and either "
                "'qiskit-aer' for local simulation or 'qiskit-ibm-runtime' "
                "for hardware). Install with `pip install highspy-quantum[qiskit]`."
            ) from e

    def _select_sampler(self):
        """Pick (sampler, label) given env. Defaults to Aer."""
        token = os.environ.get("IBMQ_TOKEN", "").strip()
        extra = _parse_extra(os.environ.get("HIGHS_QUANTUM_EXTRA_ARGS", ""))
        if token and "qiskit-backend" in extra:
            try:
                from qiskit_ibm_runtime import (  # type: ignore
                    QiskitRuntimeService,
                    Sampler as RuntimeSampler,
                )

                service = QiskitRuntimeService(token=token, channel="ibm_quantum")
                backend = service.backend(extra["qiskit-backend"])
                return RuntimeSampler(backend=backend), f"ibm_runtime:{extra['qiskit-backend']}"
            except Exception:  # noqa: BLE001 — fall through to Aer
                pass
        # Local Aer simulator.
        try:
            from qiskit_aer.primitives import Sampler as AerSampler  # type: ignore

            return AerSampler(), "qiskit_aer"
        except ImportError as e:
            raise BackendUnavailable(
                "Qiskit backend's default Aer simulator requires 'qiskit-aer'. "
                "Install with `pip install highspy-quantum[qiskit]`."
            ) from e

    def solve(self, bqm: Bqm, time_limit_s: float) -> list[Sample]:
        if bqm.num_vars == 0:
            return [Sample(assignment=np.zeros(0), bqm_objective=bqm.offset, info={})]

        token_set = bool(os.environ.get("IBMQ_TOKEN", "").strip())
        cap = _HW_MAX_VARS if token_set else _AER_MAX_VARS
        if bqm.num_vars > cap:
            return []  # caller logs an empty-sample warning

        sampler, label = self._select_sampler()

        from qiskit.algorithms.minimum_eigensolvers import QAOA  # type: ignore  # noqa: I001
        from qiskit.algorithms.optimizers import COBYLA  # type: ignore
        from qiskit_optimization.algorithms import MinimumEigenOptimizer  # type: ignore

        qp = _build_quadratic_program(bqm)

        reps = max(1, min(5, 1 + int(time_limit_s / 5)))
        qaoa = QAOA(sampler=sampler, optimizer=COBYLA(maxiter=100), reps=reps)
        opt = MinimumEigenOptimizer(qaoa)

        started = time.monotonic()
        try:
            result = opt.solve(qp)
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(f"QAOA failed on {label}: {type(e).__name__}: {e}") from e
        elapsed = time.monotonic() - started

        assignment = np.asarray(result.x, dtype=np.float64)
        return [
            Sample(
                assignment=assignment,
                bqm_objective=float(result.fval),
                info={"sampler": label, "reps": reps, "wall_time": elapsed},
            )
        ]
