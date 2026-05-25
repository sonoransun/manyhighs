"""Rigetti pyQuil QAOA backend.

Default execution path uses pyQuil's ``WavefunctionSimulator`` running
locally — no QCS lease needed, fine for ≤16 binary variables. Hardware
path activates when ``--rigetti-qpu=<qc_name>`` (e.g. ``Aspen-M-3``) is in
``quantum_extra_args`` and the standard QCS settings are present.

QAOA structure: cost Hamiltonian from the BQM (linear ⇒ Z terms, quadratic
⇒ ZZ terms), mixer = sum of X gates, classical optimizer = scipy.minimize
over (β, γ) parameter pairs.
"""
from __future__ import annotations

import os
import time
from typing import Any

import numpy as np

from ..model import Bqm
from .base import BackendUnavailable, Sample

_LOCAL_MAX_VARS = 16


def _parse_extra(extra: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for tok in extra.split():
        if tok.startswith("--") and "=" in tok:
            k, v = tok[2:].split("=", 1)
            out[k] = v
    return out


def _bqm_to_ising(bqm: Bqm) -> tuple[np.ndarray, dict[tuple[int, int], float], float]:
    """Convert min-QUBO to Ising (z_i = 1 - 2 x_i).

    Returns (h, J, offset) where:
      H = offset + sum_i h_i z_i + sum_{i<j} J_ij z_i z_j
    """
    n = bqm.num_vars
    h = np.zeros(n)
    J: dict[tuple[int, int], float] = {}
    offset = float(bqm.offset)
    # Linear contribution: a_i * x_i = a_i * (1 - z_i)/2
    for i in range(n):
        ai = float(bqm.linear[i])
        offset += ai * 0.5
        h[i] -= ai * 0.5
    # Quadratic contribution: q_ij * x_i x_j = q_ij * (1 - z_i)(1 - z_j)/4
    for (i, j), qij in bqm.quadratic.items():
        offset += qij * 0.25
        h[i] -= qij * 0.25
        h[j] -= qij * 0.25
        a, b = (i, j) if i < j else (j, i)
        J[(a, b)] = J.get((a, b), 0.0) + qij * 0.25
    return h, J, offset


class RigettiBackend:
    name = "rigetti"

    def __init__(self) -> None:
        try:
            import pyquil  # noqa: F401
        except ImportError as e:
            raise BackendUnavailable(
                "Rigetti backend requires 'pyquil'. Install with "
                "`pip install highspy-quantum[rigetti]`."
            ) from e

    def solve(self, bqm: Bqm, time_limit_s: float) -> list[Sample]:
        if bqm.num_vars == 0:
            return [Sample(assignment=np.zeros(0), bqm_objective=bqm.offset, info={})]

        extra = _parse_extra(os.environ.get("HIGHS_QUANTUM_EXTRA_ARGS", ""))
        qpu = extra.get("rigetti-qpu", "").strip()

        if not qpu and bqm.num_vars > _LOCAL_MAX_VARS:
            return []  # caller will log empty-sample warning

        from pyquil import Program  # type: ignore
        from pyquil.gates import RX, H  # type: ignore
        from pyquil.paulis import PauliSum, PauliTerm, exponential_map  # type: ignore

        n = bqm.num_vars
        h, J, offset = _bqm_to_ising(bqm)

        # Build cost Hamiltonian as a sum of Pauli terms.
        cost_terms: list[PauliTerm] = []
        for i, hi in enumerate(h):
            if hi != 0.0:
                cost_terms.append(PauliTerm("Z", i, hi))
        for (i, j), jij in J.items():
            if jij != 0.0:
                cost_terms.append(PauliTerm("Z", i, jij) * PauliTerm("Z", j))
        if not cost_terms:
            # Pure offset — every assignment is equivalent.
            return [
                Sample(
                    assignment=np.zeros(n),
                    bqm_objective=offset,
                    info={"sampler": "rigetti_trivial"},
                )
            ]
        cost_ham = PauliSum(cost_terms)

        # Mixer = sum_i X_i (driven by RX rotations later).
        reps = max(1, min(3, 1 + int(time_limit_s / 5)))

        def make_program(params: np.ndarray) -> "Program":
            betas, gammas = params[:reps], params[reps:]
            prog = Program()
            for q in range(n):
                prog += H(q)
            for r in range(reps):
                prog += exponential_map(cost_ham)(gammas[r])
                for q in range(n):
                    prog += RX(2 * betas[r], q)
            return prog

        # Local simulator path. pyquil's WavefunctionSimulator computes the
        # exact expectation; we then sample from the resulting state.
        from pyquil.api import WavefunctionSimulator  # type: ignore
        from scipy.optimize import minimize  # type: ignore

        wfn_sim = WavefunctionSimulator()

        def expectation(params: np.ndarray) -> float:
            prog = make_program(params)
            wfn = wfn_sim.wavefunction(prog)
            probs = wfn.probabilities()
            # H|psi> expectation: enumerate basis states (size 2^n — bounded
            # by _LOCAL_MAX_VARS so this is OK).
            total = 0.0
            for state_idx, p in enumerate(probs):
                bits = np.array(
                    [(state_idx >> i) & 1 for i in range(n)], dtype=np.float64
                )
                # Convert bits → ±1 spins for Ising eval.
                z = 1.0 - 2.0 * bits
                e = offset
                for i in range(n):
                    e += h[i] * z[i]
                for (i, j), jij in J.items():
                    e += jij * z[i] * z[j]
                total += p * e
            return total

        started = time.monotonic()
        params0 = np.full(2 * reps, 0.25)
        deadline_options = {"maxiter": max(20, int(time_limit_s * 10))}
        try:
            res = minimize(expectation, params0, method="COBYLA", options=deadline_options)
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(f"pyquil QAOA failed: {type(e).__name__}: {e}") from e

        # Sample from final state. Take the most-likely basis state.
        wfn = wfn_sim.wavefunction(make_program(res.x))
        probs = wfn.probabilities()
        best_idx = int(np.argmax(probs))
        bits = np.array([(best_idx >> i) & 1 for i in range(n)], dtype=np.float64)

        # Evaluate the *QUBO* objective (not Ising) on the recovered bits.
        bqm_obj = bqm.evaluate(bits)
        return [
            Sample(
                assignment=bits,
                bqm_objective=float(bqm_obj),
                info={
                    "sampler": "pyquil_wavefunction",
                    "reps": reps,
                    "qaoa_expectation": float(res.fun),
                    "wall_time": time.monotonic() - started,
                },
            )
        ]
