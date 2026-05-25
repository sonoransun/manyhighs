"""``highs-quantum`` CLI and the C++ subprocess entry point.

Two modes:

``highs-quantum solve --backend NAME --in IN.json --out OUT.json --timeout T``
    Subprocess mode, invoked by the C++ heuristic. Reads the JSON the C++
    side wrote, runs the named backend, writes the result JSON.

``highs-quantum solve PROBLEM.mps --backend NAME [--time-limit T]``
    Standalone mode. Reads an MPS/LP/QUBO file (via ``highspy``), reformulates
    it, and prints the chosen backend's solution.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import sys
import time
from typing import Optional

import numpy as np

from .backends import BackendUnavailable, get_backend
from .model import MipSubproblem, build_bqm_from_subproblem
from .protocol import PROTOCOL_VERSION, decode_input, encode_result
from .repair import repair as repair_sample
from . import structure


# Adaptive-penalty escalation: if the best sample is infeasible, double the
# penalty and try again, up to this many doublings. Bounded so the per-call
# wall-time budget still matters.
_MAX_PENALTY_DOUBLINGS = 4
_REPAIR_TIME_FRACTION = 0.1  # cap repair pass at 10% of the per-call budget


def _single_pass(
    backend,
    sub: MipSubproblem,
    time_limit_s: float,
    penalty: float | None,
) -> tuple[bool, np.ndarray, float, str]:
    """One solve + repair pass at the given penalty. Returns (feasible, x, obj, error)."""
    # Try a structure-aware builder first; fall through to the generic
    # penalty method for unrecognized shapes.
    tag = structure.detect(sub)
    bqm = structure.build_for(tag, sub) if tag else None
    if bqm is None:
        bqm = build_bqm_from_subproblem(sub, penalty=penalty)
    try:
        samples = backend.solve(bqm, time_limit_s=time_limit_s)
    except Exception as e:  # noqa: BLE001 — backends must never crash the caller
        return (False, np.zeros(0), 0.0, f"backend raised: {type(e).__name__}: {e}")
    if not samples:
        return (False, np.zeros(0), 0.0, "backend returned no samples")

    # Pick best by (feasibility, original-problem objective). Repair first —
    # cheap pass might turn an infeasible best into a feasible one without
    # needing a penalty escalation.
    repair_budget = max(0.05, time_limit_s * _REPAIR_TIME_FRACTION)
    best: Optional[tuple[tuple[int, float], np.ndarray, bool]] = None
    for s in samples:
        x = s.assignment
        feasible = sub.is_feasible(x)
        if not feasible:
            x_repaired, repaired_ok, _ = repair_sample(
                sub, x, time_limit_s=repair_budget
            )
            if repaired_ok:
                x = x_repaired
                feasible = True
        obj = sub.evaluate(x) if feasible else float("inf")
        key = (0 if feasible else 1, obj if feasible else s.bqm_objective)
        if best is None or key < best[0]:
            best = (key, x, feasible)

    assert best is not None
    _, assignment, feasible = best
    obj = sub.evaluate(assignment)
    return (
        feasible,
        assignment,
        float(obj),
        "" if feasible else "best sample violated constraints",
    )


def _run_backend(
    backend_name: str,
    sub: MipSubproblem,
    time_limit_s: float,
) -> tuple[bool, str, float, float, np.ndarray, str]:
    """Run the named backend on `sub` with adaptive-penalty escalation.

    Returns the tuple ``encode_result`` consumes:
    ``(ok, backend, objective, wall_time, assignment, error)``.
    """
    started = time.monotonic()
    try:
        backend = get_backend(backend_name)
    except BackendUnavailable as e:
        return (False, backend_name, 0.0, 0.0, np.zeros(0), str(e))

    # Split the time budget across penalty doublings so each pass gets a
    # reasonable shot. The last pass gets whatever budget remains.
    deadline = started + time_limit_s
    penalty: float | None = None  # first pass uses _default_penalty()
    last_error = ""
    last_assignment = np.zeros(0)
    last_objective = 0.0

    for attempt in range(_MAX_PENALTY_DOUBLINGS + 1):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        # Allow at least a small per-pass budget; later passes get less.
        per_pass = max(0.1, remaining / max(1, _MAX_PENALTY_DOUBLINGS - attempt + 1))
        feasible, assignment, objective, error = _single_pass(
            backend, sub, per_pass, penalty
        )
        last_error = error
        if assignment.size > 0:
            last_assignment = assignment
            last_objective = objective
        if feasible or sub.num_rows == 0:
            return (
                True,
                backend_name,
                float(objective),
                time.monotonic() - started,
                assignment,
                "",
            )
        # Infeasible: escalate the penalty and retry.
        if penalty is None:
            # Pick up the default from build_bqm_from_subproblem and double it.
            bqm_default = build_bqm_from_subproblem(sub)
            # Approximate the default penalty as the max of any quadratic coef
            # (good enough for escalation; we just need monotone growth).
            penalty = max(1.0, max((abs(v) for v in bqm_default.quadratic.values()), default=1.0))
        penalty *= 2.0

    # Out of attempts. Return whatever we last had (infeasible) so the C++
    # side can log it; trySolution() will reject it cleanly.
    return (
        False,
        backend_name,
        last_objective,
        time.monotonic() - started,
        last_assignment,
        last_error or "exhausted penalty escalation budget",
    )


def _cmd_subprocess(
    backend_name: str,
    in_path: pathlib.Path,
    out_path: pathlib.Path,
    timeout: float,
) -> int:
    text = in_path.read_text()
    sub = decode_input(text)
    ok, backend, objective, wall_time, assignment, error = _run_backend(
        backend_name, sub, time_limit_s=timeout
    )
    out_path.write_text(
        encode_result(
            ok=ok,
            backend=backend,
            objective=objective,
            wall_time=wall_time,
            assignment=assignment,
            error=error,
        )
    )
    return 0  # Always 0; the C++ side reads `ok` from the JSON.


def _load_subproblem_from_file(
    path: pathlib.Path,
) -> MipSubproblem:
    """Read a model file. Uses ``highspy`` if available, falls back to JSON."""
    suffix = path.suffix.lower()
    if suffix == ".json":
        return decode_input(path.read_text())
    try:
        import highspy  # type: ignore
    except ImportError as e:
        raise SystemExit(
            f"Reading {suffix!r} files requires the `highspy` package "
            "(`pip install highspy`). Or supply a .json subproblem directly."
        ) from e
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    status = h.readModel(str(path))
    if int(status) != 0:
        raise SystemExit(f"highspy failed to read {path}")
    lp = h.getLp()
    num_col = lp.num_col_
    num_row = lp.num_row_
    a_matrix = lp.a_matrix_

    # HiGHS stores the matrix column-wise; we need row-wise for our protocol.
    cols_start = np.asarray(a_matrix.start_, dtype=np.int64)
    cols_index = np.asarray(a_matrix.index_, dtype=np.int64)
    cols_value = np.asarray(a_matrix.value_, dtype=np.float64)
    # Build row CSR by counting nnz per row.
    counts = np.zeros(num_row + 1, dtype=np.int64)
    for c in range(num_col):
        for k in range(int(cols_start[c]), int(cols_start[c + 1])):
            counts[int(cols_index[k]) + 1] += 1
    row_start = np.cumsum(counts).astype(np.int64)
    nnz = int(row_start[num_row])
    col_index = np.zeros(nnz, dtype=np.int64)
    coef_value = np.zeros(nnz, dtype=np.float64)
    cursor = row_start.copy()
    cursor = cursor[:-1].copy()
    for c in range(num_col):
        for k in range(int(cols_start[c]), int(cols_start[c + 1])):
            r = int(cols_index[k])
            pos = int(cursor[r])
            col_index[pos] = c
            coef_value[pos] = cols_value[k]
            cursor[r] = pos + 1

    integrality = np.asarray(lp.integrality_, dtype=np.int64)
    # Only accept fully-binary models in standalone mode for the POC.
    for c in range(num_col):
        if integrality[c] != 1 or lp.col_lower_[c] != 0.0 or lp.col_upper_[c] != 1.0:
            raise SystemExit(
                f"Standalone mode currently requires a pure-binary MIP; "
                f"column {c} is not binary (integrality={integrality[c]}, "
                f"bounds=[{lp.col_lower_[c]}, {lp.col_upper_[c]}])."
            )

    return MipSubproblem(
        num_vars=num_col,
        num_rows=num_row,
        sense_multiplier=float(int(lp.sense_)),
        constant_offset=float(lp.offset_),
        linear=np.asarray(lp.col_cost_, dtype=np.float64),
        lower=np.asarray(lp.col_lower_, dtype=np.float64),
        upper=np.asarray(lp.col_upper_, dtype=np.float64),
        original_indices=np.arange(num_col, dtype=np.int64),
        row_start=row_start,
        col_index=col_index,
        coef_value=coef_value,
        row_lower=np.asarray(lp.row_lower_, dtype=np.float64),
        row_upper=np.asarray(lp.row_upper_, dtype=np.float64),
        seed_full_solution=np.zeros(num_col, dtype=np.float64),
        structure_tag="",
    )


def _cmd_benchmark(
    input_file: pathlib.Path,
    backends: list[str],
    time_limit_s: float,
) -> int:
    """Run multiple backends on the same subproblem; print a markdown comparison."""
    sub = _load_subproblem_from_file(input_file)
    rows: list[tuple[str, bool, float, float, str]] = []
    for backend_name in backends:
        ok, backend, objective, wall_time, _assignment, error = _run_backend(
            backend_name, sub, time_limit_s=time_limit_s
        )
        rows.append((backend, ok, objective, wall_time, error))
    print(f"| backend | ok | objective | wall_time | error |")
    print(f"|---|---|---|---|---|")
    for backend, ok, objective, wall_time, error in rows:
        ok_s = "✓" if ok else "✗"
        print(
            f"| {backend} | {ok_s} | {objective:.6g} | {wall_time:.3g}s | "
            f"{error[:60]} |"
        )
    return 0 if any(ok for _, ok, _, _, _ in rows) else 1


def _cmd_standalone(
    backend_name: str,
    input_file: pathlib.Path,
    output: pathlib.Path | None,
    time_limit_s: float,
) -> int:
    sub = _load_subproblem_from_file(input_file)
    ok, backend, objective, wall_time, assignment, error = _run_backend(
        backend_name, sub, time_limit_s=time_limit_s
    )
    if output is not None:
        output.write_text(
            encode_result(
                ok=ok,
                backend=backend,
                objective=objective,
                wall_time=wall_time,
                assignment=assignment,
                error=error,
            )
        )
    print(
        f"backend={backend} ok={ok} objective={objective:.6g} "
        f"wall_time={wall_time:.3g}s {'(' + error + ')' if error else ''}"
    )
    if ok:
        print("assignment:", " ".join(str(int(round(x))) for x in assignment))
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="highs-quantum",
        description="Quantum-assisted MIP heuristics for HiGHS (POC).",
    )
    parser.add_argument(
        "--protocol-version",
        action="store_true",
        help="Print the wire protocol version and exit.",
    )
    sub = parser.add_subparsers(dest="command")

    p_solve = sub.add_parser("solve", help="Run a backend.")
    p_solve.add_argument(
        "input", nargs="?", type=pathlib.Path,
        help="Model file (.mps/.lp/.json). Omit when using --in for subprocess mode.",
    )
    p_solve.add_argument(
        "--backend", required=True,
        help="Backend name: classical, exact, dwave, qiskit, rigetti, braket.",
    )
    p_solve.add_argument(
        "--in", dest="in_path", type=pathlib.Path, default=None,
        help="Subprocess input JSON (written by HiGHS C++).",
    )
    p_solve.add_argument(
        "--out", dest="out_path", type=pathlib.Path, default=None,
        help="Subprocess output JSON (read by HiGHS C++).",
    )
    p_solve.add_argument(
        "--timeout", "--time-limit", dest="timeout", type=float, default=30.0,
        help="Backend wall-time budget in seconds.",
    )

    p_bench = sub.add_parser(
        "benchmark", help="Run multiple backends and tabulate (markdown)."
    )
    p_bench.add_argument("input", type=pathlib.Path, help="Model file or .json subproblem.")
    p_bench.add_argument(
        "--backends", default="classical,exact",
        help="Comma-separated backend names.",
    )
    p_bench.add_argument(
        "--time-limit", "--timeout", dest="time_limit", type=float, default=10.0,
        help="Per-backend wall-time budget in seconds.",
    )

    args = parser.parse_args(argv)

    if args.protocol_version:
        print(PROTOCOL_VERSION)
        return 0

    if args.command == "solve":
        if args.in_path is not None and args.out_path is not None:
            return _cmd_subprocess(
                args.backend, args.in_path, args.out_path, args.timeout
            )
        if args.input is None:
            parser.error("provide either an input file or --in/--out paths")
        return _cmd_standalone(
            args.backend, args.input, args.out_path, args.timeout
        )

    if args.command == "benchmark":
        backends = [b.strip() for b in args.backends.split(",") if b.strip()]
        return _cmd_benchmark(args.input, backends, args.time_limit)

    parser.print_help()
    return 1
