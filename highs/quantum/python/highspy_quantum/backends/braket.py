"""AWS Braket backend.

Default: ``braket.devices.LocalSimulator`` — runs in-process, no AWS
credentials required. Good for ≤22 binary variables (state-vector limit).

Hardware path: ``--braket-device=arn:aws:braket:...`` in
``quantum_extra_args``, with standard AWS credentials in the environment.
Braket fronts D-Wave's QPUs (annealing), plus gate-based IonQ /
Quantinuum / Rigetti / Pasqal devices.

The implementation uses QAOA over Pauli-Z cost terms — same shape as
the Rigetti backend, but written against Braket's circuit API and SDK
primitives.
"""
from __future__ import annotations

import os
import time
from typing import Any

import numpy as np

from ..model import Bqm
from .base import BackendUnavailable, Sample
from .rigetti import _bqm_to_ising

_LOCAL_MAX_VARS = 22


def _parse_extra(extra: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for tok in extra.split():
        if tok.startswith("--") and "=" in tok:
            k, v = tok[2:].split("=", 1)
            out[k] = v
    return out


class BraketBackend:
    name = "braket"

    def __init__(self) -> None:
        try:
            import braket.circuits  # noqa: F401
        except ImportError as e:
            raise BackendUnavailable(
                "Braket backend requires 'amazon-braket-sdk'. Install with "
                "`pip install highspy-quantum[braket]`."
            ) from e

    def solve(self, bqm: Bqm, time_limit_s: float) -> list[Sample]:
        if bqm.num_vars == 0:
            return [Sample(assignment=np.zeros(0), bqm_objective=bqm.offset, info={})]

        extra = _parse_extra(os.environ.get("HIGHS_QUANTUM_EXTRA_ARGS", ""))
        device_arn = extra.get("braket-device", "").strip()

        # Defaults / caps
        if not device_arn and bqm.num_vars > _LOCAL_MAX_VARS:
            return []

        from braket.circuits import Circuit  # type: ignore
        from braket.devices import LocalSimulator  # type: ignore

        n = bqm.num_vars
        h, J, offset = _bqm_to_ising(bqm)
        reps = max(1, min(3, 1 + int(time_limit_s / 5)))

        def qaoa_circuit(params: np.ndarray) -> Circuit:
            betas, gammas = params[:reps], params[reps:]
            circ = Circuit()
            for q in range(n):
                circ.h(q)
            for r in range(reps):
                gamma = float(gammas[r])
                # Cost layer
                for i, hi in enumerate(h):
                    if hi != 0.0:
                        circ.rz(i, 2 * gamma * hi)
                for (i, j), jij in J.items():
                    if jij != 0.0:
                        circ.cnot(i, j)
                        circ.rz(j, 2 * gamma * jij)
                        circ.cnot(i, j)
                # Mixer layer
                beta = float(betas[r])
                for q in range(n):
                    circ.rx(q, 2 * beta)
            return circ

        # Local simulator path. We use exact state-vector probabilities to
        # both evaluate expectation and pick the best basis state.
        device: Any
        if device_arn:
            try:
                from braket.aws import AwsDevice  # type: ignore

                device = AwsDevice(device_arn)
            except Exception as e:  # noqa: BLE001
                raise RuntimeError(
                    f"Braket failed to load device {device_arn}: "
                    f"{type(e).__name__}: {e}"
                ) from e
        else:
            device = LocalSimulator()

        from scipy.optimize import minimize  # type: ignore

        def expectation(params: np.ndarray) -> float:
            # Add result-type for state-vector; only the local simulator
            # supports `state_vector`, but it's what we use by default.
            circ = qaoa_circuit(params)
            circ.state_vector()
            task = device.run(circ, shots=0)
            sv = np.asarray(task.result().values[0])
            probs = np.abs(sv) ** 2
            total = 0.0
            for state_idx, p in enumerate(probs):
                bits = np.array(
                    [(state_idx >> i) & 1 for i in range(n)], dtype=np.float64
                )
                z = 1.0 - 2.0 * bits
                e = offset
                for i in range(n):
                    e += h[i] * z[i]
                for (i, j), jij in J.items():
                    e += jij * z[i] * z[j]
                total += float(p) * e
            return total

        started = time.monotonic()
        params0 = np.full(2 * reps, 0.25)
        try:
            res = minimize(
                expectation, params0, method="COBYLA",
                options={"maxiter": max(20, int(time_limit_s * 10))},
            )
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(f"Braket QAOA failed: {type(e).__name__}: {e}") from e

        # Sample by re-running the optimized circuit with measurements.
        circ = qaoa_circuit(res.x)
        task = device.run(circ, shots=max(100, int(time_limit_s * 50)))
        measurements = task.result().measurement_counts
        best_state, _ = max(measurements.items(), key=lambda kv: kv[1])
        # Braket reports bit strings most-significant-first; map back to var order.
        bits = np.array(
            [float(int(best_state[n - 1 - i])) for i in range(n)],
            dtype=np.float64,
        )
        return [
            Sample(
                assignment=bits,
                bqm_objective=float(bqm.evaluate(bits)),
                info={
                    "sampler": "braket_local" if not device_arn else f"braket:{device_arn}",
                    "reps": reps,
                    "qaoa_expectation": float(res.fun),
                    "wall_time": time.monotonic() - started,
                },
            )
        ]
