"""Subprocess-protocol JSON schema, decoder, and result encoder.

The C++ side (``highs/quantum/HighsQubo.cpp``) writes the input JSON; this
module decodes it into a :class:`MipSubproblem`. The result JSON has the
inverse direction — encoded here, read back in C++.

If you change a field, bump ``PROTOCOL_VERSION`` and the matching constant in
``highs/quantum/HighsQuantumOptions.h``.
"""
from __future__ import annotations

import json
import math
from typing import Any

import numpy as np

PROTOCOL_VERSION = 1

# Input fields are all required (the C++ emitter always writes them, even if
# empty). We tolerate extras for forward compatibility.
_INPUT_REQUIRED = [
    "protocol_version",
    "num_vars",
    "num_rows",
    "sense_multiplier",
    "constant_offset",
    "linear",
    "lower",
    "upper",
    "original_indices",
    "row_start",
    "col_index",
    "coef_value",
    "row_lower",
    "row_upper",
    "seed_full_solution",
    "structure_tag",
]


def _coerce_number(v: Any) -> float:
    """Accept the sentinel strings the C++ side uses for ±inf / nan."""
    if isinstance(v, str):
        if v == "inf":
            return math.inf
        if v == "-inf":
            return -math.inf
        if v == "nan":
            return math.nan
        raise ValueError(f"unexpected string in numeric field: {v!r}")
    return float(v)


def _coerce_array(v: Any, dtype: str = "float") -> np.ndarray:
    if dtype == "int":
        return np.asarray([int(x) for x in v], dtype=np.int64)
    return np.asarray([_coerce_number(x) for x in v], dtype=np.float64)


def decode_input(text: str) -> "MipSubproblem":
    """Parse the JSON the C++ side writes into a :class:`MipSubproblem`."""
    raw = json.loads(text)
    for k in _INPUT_REQUIRED:
        if k not in raw:
            raise ValueError(f"input JSON missing required key: {k!r}")
    if int(raw["protocol_version"]) != PROTOCOL_VERSION:
        raise ValueError(
            f"protocol mismatch: C++ sent {raw['protocol_version']}, Python "
            f"expects {PROTOCOL_VERSION}"
        )

    # Local import to avoid a circular dependency at module load time.
    from .model import MipSubproblem

    return MipSubproblem(
        num_vars=int(raw["num_vars"]),
        num_rows=int(raw["num_rows"]),
        sense_multiplier=_coerce_number(raw["sense_multiplier"]),
        constant_offset=_coerce_number(raw["constant_offset"]),
        linear=_coerce_array(raw["linear"]),
        lower=_coerce_array(raw["lower"]),
        upper=_coerce_array(raw["upper"]),
        original_indices=_coerce_array(raw["original_indices"], dtype="int"),
        row_start=_coerce_array(raw["row_start"], dtype="int"),
        col_index=_coerce_array(raw["col_index"], dtype="int"),
        coef_value=_coerce_array(raw["coef_value"]),
        row_lower=_coerce_array(raw["row_lower"]),
        row_upper=_coerce_array(raw["row_upper"]),
        seed_full_solution=_coerce_array(raw["seed_full_solution"]),
        structure_tag=str(raw["structure_tag"]),
    )


def encode_result(
    *,
    ok: bool,
    backend: str,
    objective: float,
    wall_time: float,
    assignment: list[float] | np.ndarray,
    error: str = "",
) -> str:
    """Build the result JSON the C++ side reads back via ``parseResult``."""
    arr = (
        assignment.tolist()
        if isinstance(assignment, np.ndarray)
        else list(assignment)
    )
    payload = {
        "ok": bool(ok),
        "backend": backend,
        "objective": float(objective),
        "wall_time": float(wall_time),
        "assignment": [float(x) for x in arr],
        "error": error,
    }
    return json.dumps(payload)
