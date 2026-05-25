"""D-Wave (Leap / Ocean) backend.

Three operating modes, chosen at solve() time:

* **Cloud, hybrid** — when ``DWAVE_API_TOKEN`` is set and the BQM has more
  variables than ``HIGHS_QUANTUM_DWAVE_LEAP_THRESHOLD`` (default 200): use
  ``LeapHybridSampler``, which handles up to ~1M binary variables.
* **Cloud, direct QPU** — token set and smaller problem: use
  ``EmbeddingComposite(DWaveSampler())``. Smaller QPU footprint, more direct
  but limited by hardware connectivity.
* **Local, simulated annealing** — token missing or cloud import fails: use
  ``neal.SimulatedAnnealingSampler`` (bundled in dwave-ocean-sdk). No
  network, useful as a CI / no-creds default.

Credentials follow Ocean SDK conventions:
* ``DWAVE_API_TOKEN`` (preferred), or
* ``~/.config/dwave/dwave.conf``.

Extra args from ``quantum_extra_args``:
* ``--num-reads=N`` (QPU path; default 1000)
* ``--chain-strength=F`` (QPU path; default uses
  ``dwave.system.utilities.uniform_torque_compensation``)
"""
from __future__ import annotations

import os
import time
from typing import Any

import numpy as np

from ..model import Bqm
from .base import BackendUnavailable, Sample

# Threshold above which we prefer LeapHybridSampler over direct-QPU embedding.
_LEAP_HYBRID_THRESHOLD = int(
    os.environ.get("HIGHS_QUANTUM_DWAVE_LEAP_THRESHOLD", "200")
)


def _parse_extra(extra: str) -> dict[str, str]:
    """Parse `--key=value` flags from the user's quantum_extra_args string."""
    out: dict[str, str] = {}
    for tok in extra.split():
        if tok.startswith("--") and "=" in tok:
            k, v = tok[2:].split("=", 1)
            out[k] = v
    return out


class DWaveBackend:
    name = "dwave"

    def __init__(self) -> None:
        # dimod is the data layer; required for *any* mode (we always need
        # to convert Bqm → dimod.BinaryQuadraticModel).
        try:
            import dimod  # noqa: F401
        except ImportError as e:
            raise BackendUnavailable(
                "D-Wave backend requires 'dwave-ocean-sdk' (or at minimum "
                "'dimod' + 'dwave-samplers'). Install with "
                "`pip install highspy-quantum[dwave]`."
            ) from e

    def _select_sampler(self, num_vars: int) -> tuple[Any, str]:
        """Pick a sampler given problem size and DWAVE_API_TOKEN availability.

        Returns (sampler_instance, label). Falls back to neal SA if any cloud
        import fails or no token is set.
        """
        token = os.environ.get("DWAVE_API_TOKEN", "").strip()
        if token:
            try:
                if num_vars >= _LEAP_HYBRID_THRESHOLD:
                    from dwave.system import LeapHybridSampler  # type: ignore

                    return LeapHybridSampler(), "LeapHybridSampler"
                from dwave.system import (  # type: ignore
                    DWaveSampler,
                    EmbeddingComposite,
                )

                return (
                    EmbeddingComposite(DWaveSampler()),
                    "EmbeddingComposite(DWaveSampler)",
                )
            except Exception:  # noqa: BLE001 — any cloud failure → SA
                pass

        # Local SA fallback. neal is part of dwave-ocean-sdk's standard install.
        try:
            from neal import SimulatedAnnealingSampler  # type: ignore

            return SimulatedAnnealingSampler(), "neal.SimulatedAnnealingSampler"
        except ImportError:
            try:
                from dwave.samplers import (  # type: ignore
                    SimulatedAnnealingSampler,
                )

                return SimulatedAnnealingSampler(), "dwave.samplers.SimulatedAnnealingSampler"
            except ImportError as e:
                raise BackendUnavailable(
                    "D-Wave fallback needs 'neal' or 'dwave-samplers'. "
                    "Install with `pip install highspy-quantum[dwave]`."
                ) from e

    def solve(self, bqm: Bqm, time_limit_s: float) -> list[Sample]:
        if bqm.num_vars == 0:
            return [Sample(assignment=np.zeros(0), bqm_objective=bqm.offset, info={})]

        sampler, label = self._select_sampler(bqm.num_vars)

        dimod_bqm = bqm.to_dimod()
        extra = _parse_extra(os.environ.get("HIGHS_QUANTUM_EXTRA_ARGS", ""))
        kwargs: dict[str, Any] = {}
        if "LeapHybridSampler" in label:
            kwargs["time_limit"] = max(3.0, float(time_limit_s))
        else:
            kwargs["num_reads"] = int(extra.get("num-reads", 1000))
            if "chain-strength" in extra:
                kwargs["chain_strength"] = float(extra["chain-strength"])

        started = time.monotonic()
        try:
            sampleset = sampler.sample(dimod_bqm, **kwargs)
        except Exception as e:  # noqa: BLE001 — backends must never crash caller
            raise RuntimeError(f"{label} failed: {type(e).__name__}: {e}") from e

        elapsed = time.monotonic() - started

        # Take up to 16 best samples (low energy first).
        samples_out: list[Sample] = []
        for row in sampleset.lowest().record[:16]:
            sample_array = np.asarray(
                [float(row.sample[i]) for i in range(bqm.num_vars)],
                dtype=np.float64,
            )
            samples_out.append(
                Sample(
                    assignment=sample_array,
                    bqm_objective=float(row.energy),
                    info={
                        "sampler": label,
                        "wall_time": elapsed,
                        "num_occurrences": int(row.num_occurrences),
                    },
                )
            )
        return samples_out
