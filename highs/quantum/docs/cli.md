# `highs-quantum` CLI reference

Two subcommands: `solve` (one backend on one model) and `benchmark`
(multiple backends on one model, tabular comparison).

## `highs-quantum solve`

Two modes share the same subcommand.

### Standalone mode

Read an MPS / LP / `.json` subproblem, run one backend, print the result.

```
highs-quantum solve PROBLEM.mps --backend NAME [--time-limit T] [--output OUT.json]
```

| Flag | Required | Description |
|---|---|---|
| `PROBLEM` (positional) | yes | Path to `.mps`, `.lp`, or `.json` subproblem. MPS/LP files are parsed via `highspy` (must be installed). |
| `--backend NAME` | yes | One of: `classical`, `exact`, `dwave`, `qiskit`, `rigetti`, `braket`. |
| `--time-limit T` (or `--timeout T`) | no, default 30 | Wall-time budget in seconds. |
| `--output OUT.json` | no | Write the result JSON to this path in addition to printing. |

Standalone mode only accepts pure-binary MIPs today
(`integrality_[i] == kInteger` and bounds `[0, 1]` for every column).
Non-binary input exits 1 with a clear error.

### Subprocess mode (called by the C++ heuristic)

```
highs-quantum solve --backend NAME --in IN.json --out OUT.json --timeout T
```

Reads the subproblem the C++ side wrote to `IN.json`, writes the result
to `OUT.json`. Always exits 0; the `ok` field in `OUT.json` carries the
status. Not normally invoked by humans.

## `highs-quantum benchmark`

Run several backends on the same subproblem; print a Markdown table of
objective + wall time.

```
highs-quantum benchmark PROBLEM.mps --backends CSV [--time-limit T]
```

| Flag | Required | Description |
|---|---|---|
| `PROBLEM` (positional) | yes | Same as `solve`. |
| `--backends a,b,c` | no, default `classical,exact` | Comma-separated list. |
| `--time-limit T` | no, default 10 | Per-backend wall-time budget. |

Example output:

```
| backend   | ok | objective | wall_time | error |
|---|---|---|---|---|
| classical | ✓  | -6        | 0.082s    |       |
| exact     | ✓  | -6        | 0.014s    |       |
| dwave     | ✓  | -6        | 1.7s      |       |
```

## Result JSON schema

```json
{
  "ok":          bool,                  // false ⇒ no usable sample
  "backend":     "classical",           // echo of the chosen backend
  "objective":   -6.0,                  // original-problem objective on `assignment`
  "wall_time":   0.082,                 // backend wall time, seconds
  "assignment":  [0.0, 1.0, 1.0, ...],  // full-dimensional primal vector
  "error":       ""                     // populated when ok=false
}
```

`assignment` is always full-dimensional (lifted onto the seed solution
the C++ side passed in). When `ok=false`, `assignment` may still contain
the best infeasible candidate — the C++ side rejects it via
`trySolution` but the field is populated so callers can inspect what
the backend tried.

## Exit codes

| Code | Standalone | Subprocess |
|---|---|---|
| 0    | feasible sample returned | always 0 (read `ok` from JSON) |
| 1    | infeasible / unknown backend / file error | — |

## See also

- [installation](installation.md) — getting the binary on PATH
- [backends](backends.md) — what each `--backend NAME` actually does
- [troubleshooting](troubleshooting.md) — common errors
