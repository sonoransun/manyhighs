# Quantum-assisted MIP heuristic (POC)

A research-grade primal-heuristic plug-in that dispatches binary-MIP
subproblems from HiGHS's branch-and-bound search to **quantum or
quantum-inspired backends** — D-Wave annealing, IBM Qiskit QAOA,
Rigetti pyQuil, AWS Braket — and lifts feasible results back as
incumbents via `trySolution`.

This page is an overview; the full documentation, including all diagrams
and animations, lives at
[`highs/quantum/docs/`](https://github.com/ERGO-Code/HiGHS/tree/master/highs/quantum/docs)
in the source tree.

## High-level architecture

```
┌─────────────────────────────────────────────────────────┐
│ HiGHS C++ MIP solver (built with -DQUANTUM=ON)          │
│   HighsMipSolverData::quantumHeuristic()                │
│     ├─ extract subproblem (whole MIP or RINS sub-MIP)   │
│     ├─ dispatch async — std::thread → subprocess        │
│     └─ harvest non-blocking — trySolution() on done     │
└───────────────────────────┬─────────────────────────────┘
                            │  subprocess + JSON files
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Python: python -m highspy_quantum solve                 │
│   structure detect → BQM build → backend.solve → repair │
│   classical | exact | dwave | qiskit | rigetti | braket │
└─────────────────────────────────────────────────────────┘
```

The C++ side blocks on **nothing** — each dispatch spawns a worker
`std::thread` that owns the subprocess, and the search thread polls
completion via atomic flags during the dive loop.

## Build flags

The integration is **opt-in at build time** and bit-identical to a
stock HiGHS build when off:

```shell
cmake -S . -B build -DQUANTUM=ON -DFAST_BUILD=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
```

`-DQUANTUM=OFF` (the default) produces a `highs` binary indistinguishable
from a stock build: no new dependencies, no extra symbols, identical
library size.

## Runtime options

When the heuristic is built in, six options gate its behavior. Set them
via `--options_file q.txt`:

| Option | Default | Description |
|---|---|---|
| `mip_quantum_heuristic` | `off` | Backend name or `off`. |
| `quantum_time_limit` | `30.0` | Per-call wall-time budget (seconds). |
| `quantum_python_executable` | `python3` | Interpreter used for the subprocess. |
| `quantum_extra_args` | (empty) | Verbatim args passed to the Python CLI. |
| `mip_quantum_node_frequency` | `0` | Dispatch every N dive cycles (0 = every time `moreHeuristicsAllowed`). |
| `mip_quantum_heuristic_mode` | `whole` | `whole` ships the whole MIP; `rins` extracts a sub-MIP around the LP relaxation + incumbent. |

## Status and caveats

- **Research POC** — not a recommended replacement for the existing
  primal heuristics (RENS, RINS, feasibility jump) on production
  workloads. The classical heuristics are faster and more reliable on
  the problem sizes today's quantum hardware can handle.
- **Cloud latency dominates** for QPU backends — a D-Wave Leap call
  takes 1–3s, IBM Runtime can take 30s+. Best suited for problems where
  the MIP would otherwise spend at least that long stuck on the primal
  bound.
- **Penalty reformulation is brittle.** The compact, structure-aware
  reformulations (`set_partitioning`, `max_cut`) work well; the generic
  penalty path is at best modestly effective.

## Where to go next

- [`installation.md`](https://github.com/ERGO-Code/HiGHS/blob/master/highs/quantum/docs/installation.md) —
  pip + cmake setup, vendor extras, env vars.
- [`hooked-into-highs.md`](https://github.com/ERGO-Code/HiGHS/blob/master/highs/quantum/docs/hooked-into-highs.md) —
  how to enable, how to read the MIP log.
- [`backends.md`](https://github.com/ERGO-Code/HiGHS/blob/master/highs/quantum/docs/backends.md) —
  what each backend actually does, sizing, credentials.
- [`architecture.md`](https://github.com/ERGO-Code/HiGHS/blob/master/highs/quantum/docs/architecture.md) —
  full architecture deep-dive with 5 SVG diagrams.
- [`theory.md`](https://github.com/ERGO-Code/HiGHS/blob/master/highs/quantum/docs/theory.md) —
  QUBO, penalty method, repair, RINS — with animated GIFs of each.
- [`troubleshooting.md`](https://github.com/ERGO-Code/HiGHS/blob/master/highs/quantum/docs/troubleshooting.md) —
  common failure modes and the actual fix for each.

## Citing this work

If you use this quantum heuristic in academic work, please cite HiGHS
proper (see the [About](index.md) page) plus this POC by repository
URL — there is no separate paper today.
