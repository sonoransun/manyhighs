# Hooking the quantum heuristic into HiGHS

The C++ heuristic runs as a primal-heuristic plug-in inside HiGHS's
branch-and-bound dive loop. When enabled it fires alongside RENS / RINS /
feasibility-jump (it competes for the same `mip_heuristic_effort` budget).

## Build

Requires `-DFAST_BUILD=ON` (modern target layout) and `-DQUANTUM=ON`:

```
cmake -S . -B build -DQUANTUM=ON -DFAST_BUILD=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
```

If you forget `FAST_BUILD=ON`, CMake hard-fails:

> `FATAL_ERROR: QUANTUM heuristic is only available with FAST_BUILD=ON.`

The `-DQUANTUM=ON` define propagates as a **PUBLIC** target compile
definition — both the library and any consumer linking against it see
the same `HighsOptions` struct layout. This was the cause of a Sprint-0
segfault; see [architecture](architecture.md#build-system-pitfalls).

![build flag propagation](assets/diagrams/build-flags.svg)

## Options reference

All six options live under `#ifdef QUANTUM` in `HighsOptions.h`. None
are surfaced in `highs --help` (they're advanced); set them via an
options file:

```
mip_quantum_heuristic = classical
quantum_time_limit = 5.0
quantum_python_executable = python3
quantum_extra_args =
mip_quantum_node_frequency = 0
mip_quantum_heuristic_mode = whole
```

| Option | Default | Description |
|---|---|---|
| `mip_quantum_heuristic` | `off` | Backend name (`classical`, `exact`, `dwave`, `qiskit`, `rigetti`, `braket`) or `off`. |
| `quantum_time_limit` | `30.0` | Per-call wall-time budget, seconds. |
| `quantum_python_executable` | `python3` | Interpreter used to invoke `python -m highspy_quantum solve`. |
| `quantum_extra_args` | (empty) | Verbatim args appended to the Python CLI invocation. |
| `mip_quantum_node_frequency` | `0` | Dispatch every N dive cycles. `0` ⇒ every time `moreHeuristicsAllowed()` allows. |
| `mip_quantum_heuristic_mode` | `whole` | `whole` ⇒ ship the whole MIP per call. `rins` ⇒ extract a sub-MIP around the LP relaxation + current incumbent. See [theory](theory.md#rins-extraction). |

Run:

```
./build/bin/highs problem.mps --options_file q.txt
```

## Reading the MIP log

Two log lines are emitted per dispatch + harvest. Watch for them:

```
Quantum heuristic: dispatching classical (vars=15, rows=40, in_flight=1)
Quantum heuristic: backend=classical objective=-6.000000 wall_time=0.082s accepted=yes
```

If a sample is accepted, the `Q` source character appears in the MIP
display line's leftmost column:

```
Src  Proc. InQueue |  Leaves   Expl. | BestBound       BestSol  ...
 Q       0       0         0   0.00%   -6              -6        ...
```

The legend at the top of every solve includes `Q => Quantum` once the
heuristic is enabled (in fact it's always in the legend now — the
character is unconditionally defined).

## When the heuristic doesn't fire

The dispatch log line says "skipped" with one of these reasons:

| Reason | Meaning | Fix |
|---|---|---|
| `model has continuous variables` | A column has `kContinuous` integrality. | Current scope is binary-only. Use a different heuristic or relax to LP. |
| `model has non-binary integer variables` | An integer var has bounds outside `[0, 1]`. | Future Sprint extends to general-integer; for now, reformulate to binary. |
| `model exceeds quantum heuristic var budget` | More than 2048 vars (default). | Raise `quantum_extra_args=--max-vars=N` (TODO future option) or use `mip_quantum_heuristic_mode=rins`. |
| `model is empty` | Presolve reduced the model to zero columns. | Working as intended — nothing for the heuristic to do. |

See [troubleshooting](troubleshooting.md) for a deeper list including
"the heuristic fires but Q never appears in the display."

## Performance guidance

The hybrid heuristic is **a primal heuristic** — it can only improve the
incumbent, never worsen it. But it costs wall-clock time:

- **Local backends** (`classical`, `exact`, Aer simulators) add ~100ms
  startup per call. Reasonable to fire frequently.
- **Cloud backends** (`dwave` Leap, `qiskit` Runtime, `braket` real
  devices) add seconds to minutes per call. Use a higher
  `mip_quantum_node_frequency` to throttle.

For most MIPs HiGHS solves in seconds, the overhead dominates. The
heuristic's value lies in:
- Hard MIPs where finding *any* incumbent is the bottleneck.
- Problems with detected QUBO structure ([backends](backends.md), [theory](theory.md)).
- Benchmarking / research, where the quantum signal matters more than
  the wall-clock cost.
