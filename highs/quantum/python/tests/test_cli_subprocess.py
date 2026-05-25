"""End-to-end test of the C++ subprocess path: build an input JSON the way
HighsQubo::toJson would, invoke the CLI via Python, parse the result.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

from highspy_quantum import PROTOCOL_VERSION
from highspy_quantum.cli import _cmd_subprocess


def _write_input(path: pathlib.Path) -> None:
    payload = {
        "protocol_version": PROTOCOL_VERSION,
        "num_vars": 3,
        "num_rows": 0,
        "sense_multiplier": 1.0,
        "constant_offset": 0.0,
        # min -x0 -2x1 -3x2 → optimal (1,1,1) → -6
        "linear": [-1.0, -2.0, -3.0],
        "lower": [0.0, 0.0, 0.0],
        "upper": [1.0, 1.0, 1.0],
        "original_indices": [0, 1, 2],
        "row_start": [0],
        "col_index": [],
        "coef_value": [],
        "row_lower": [],
        "row_upper": [],
        "seed_full_solution": [0.0, 0.0, 0.0],
        "structure_tag": "",
    }
    path.write_text(json.dumps(payload))


def test_subprocess_classical(tmp_path: pathlib.Path):
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    _write_input(in_path)

    rc = _cmd_subprocess("classical", in_path, out_path, timeout=1.0)
    assert rc == 0
    result = json.loads(out_path.read_text())
    assert result["ok"] is True
    assert result["backend"] == "classical"
    assert result["assignment"] == [1.0, 1.0, 1.0]
    assert result["objective"] == -6.0


def test_subprocess_exact(tmp_path: pathlib.Path):
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    _write_input(in_path)

    rc = _cmd_subprocess("exact", in_path, out_path, timeout=5.0)
    assert rc == 0
    result = json.loads(out_path.read_text())
    assert result["ok"] is True
    assert result["backend"] == "exact"
    assert result["assignment"] == [1.0, 1.0, 1.0]


def test_subprocess_unknown_backend(tmp_path: pathlib.Path):
    in_path = tmp_path / "in.json"
    out_path = tmp_path / "out.json"
    _write_input(in_path)
    rc = _cmd_subprocess("doesnotexist", in_path, out_path, timeout=1.0)
    assert rc == 0  # subprocess always exits 0; status carried in JSON
    result = json.loads(out_path.read_text())
    assert result["ok"] is False
    assert "unknown" in result["error"].lower()
