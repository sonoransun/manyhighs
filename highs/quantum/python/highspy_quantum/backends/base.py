"""Backend abstraction.

Backends consume a :class:`~highspy_quantum.model.Bqm` plus a wall-time
budget and return one or more :class:`Sample` objects. The CLI picks the
best feasible sample by re-evaluating against the original
:class:`~highspy_quantum.model.MipSubproblem`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from ..model import Bqm


class BackendUnavailable(RuntimeError):
    """Raised when a backend can't run (missing SDK, no credentials, etc.)."""


@dataclass
class Sample:
    assignment: np.ndarray
    bqm_objective: float
    info: dict[str, object]


class Backend(Protocol):
    name: str

    def solve(self, bqm: Bqm, time_limit_s: float) -> list[Sample]:
        """Return zero or more candidate solutions for the given BQM.

        Implementations should respect ``time_limit_s`` best-effort and never
        raise; on failure return an empty list and let the caller decide.
        """
        ...
