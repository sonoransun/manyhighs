"""Round-trip the JSON protocol C++ writes and we read."""
from __future__ import annotations

import math

import numpy as np

from highspy_quantum import PROTOCOL_VERSION
from highspy_quantum.protocol import decode_input, encode_result


def _canonical_input_json() -> str:
    # Hand-written to match what HighsQubo::toJson would produce.
    import json

    payload = {
        "protocol_version": PROTOCOL_VERSION,
        "num_vars": 3,
        "num_rows": 1,
        "sense_multiplier": 1.0,
        "constant_offset": 0.5,
        "linear": [1.0, -2.0, 3.0],
        "lower": [0.0, 0.0, 0.0],
        "upper": [1.0, 1.0, 1.0],
        "original_indices": [0, 1, 2],
        "row_start": [0, 3],
        "col_index": [0, 1, 2],
        "coef_value": [1.0, 1.0, 1.0],
        "row_lower": ["-inf"],
        "row_upper": [2.0],
        "seed_full_solution": [0.0, 1.0, 0.0],
        "structure_tag": "test",
    }
    return json.dumps(payload)


def test_decode_input_basic():
    sub = decode_input(_canonical_input_json())
    assert sub.num_vars == 3
    assert sub.num_rows == 1
    assert sub.sense_multiplier == 1.0
    assert sub.constant_offset == 0.5
    np.testing.assert_array_equal(sub.linear, [1.0, -2.0, 3.0])
    assert math.isinf(sub.row_lower[0]) and sub.row_lower[0] < 0
    assert sub.row_upper[0] == 2.0
    assert sub.structure_tag == "test"


def test_decode_input_rejects_wrong_version():
    import json

    bad = json.loads(_canonical_input_json())
    bad["protocol_version"] = PROTOCOL_VERSION + 1
    try:
        decode_input(json.dumps(bad))
    except ValueError as e:
        assert "protocol" in str(e).lower()
    else:
        raise AssertionError("expected ValueError for wrong protocol version")


def test_encode_result_round_trip():
    text = encode_result(
        ok=True,
        backend="classical",
        objective=-3.5,
        wall_time=0.12,
        assignment=np.array([0.0, 1.0, 1.0]),
        error="",
    )
    import json

    parsed = json.loads(text)
    assert parsed["ok"] is True
    assert parsed["backend"] == "classical"
    assert parsed["objective"] == -3.5
    assert parsed["assignment"] == [0.0, 1.0, 1.0]
