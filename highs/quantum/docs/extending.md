# Extending the quantum heuristic

## Adding a new backend

Backends implement a tiny interface in
[`highspy_quantum/backends/base.py`](../python/highspy_quantum/backends/base.py):

```python
class Backend(Protocol):
    name: str
    def solve(self, bqm: Bqm, time_limit_s: float) -> list[Sample]: ...
```

A minimum-viable backend is ~30 lines. See `backends/classical.py` for a
fully-worked dependency-free example.

### Step-by-step

1. **Create the file** at `highspy_quantum/backends/<vendor>.py`.
2. **Probe the SDK** in `__init__`; raise `BackendUnavailable` with an
   actionable message if missing. This is how the integration stays
   importable when only some extras are installed.
3. **Implement `solve()`**. Convert the input `Bqm` to whatever the
   vendor SDK expects. `Bqm.to_dimod()` is already available if the
   vendor consumes `dimod.BinaryQuadraticModel` (D-Wave, some Qiskit
   paths).
4. **Wrap exceptions**: `solve()` must not propagate — return an empty
   list and let the caller log "backend returned no samples." The
   vendor SDK can throw network errors, auth failures, etc.; treating
   these as a soft failure keeps HiGHS's classical search unaffected.
5. **Add credentials check** if applicable. Read env vars; never store
   tokens in the package.
6. **Register the backend** in
   [`highspy_quantum/backends/__init__.py`](../python/highspy_quantum/backends/__init__.py)
   inside `get_backend()` — the only place that knows about the full
   vendor list. Use lazy imports so missing SDKs don't break package
   load for the other backends.
7. **Add a `[vendor]` extra** in `pyproject.toml` so users can
   `pip install 'highspy-quantum[vendor]'`.
8. **Tests** at `tests/test_<vendor>.py`:
   - `test_unavailable_when_sdk_missing` — monkeypatch `sys.modules` to
     drop the vendor module; expect `BackendUnavailable`.
   - `test_solve_round_trip` — gated by `@pytest.mark.skipif(not _HAS_SDK, …)`
     when the SDK isn't in CI.
   - `test_sampler_call_shape` — mock the sampler, call `solve()`,
     assert it received the expected BQM shape.

### What you DON'T need to do

- Touch the C++ side. Adding a backend never requires recompiling HiGHS;
  the C++ heuristic dispatches via the backend's **name string** in the
  HiGHS option `mip_quantum_heuristic = <name>`.
- Implement penalty reformulation. Generic penalty is in `model.py`;
  structure-specialized reformulations live in `reformulation/` and run
  before your backend sees the Bqm.
- Implement repair. `repair.py` runs on every infeasible sample
  automatically.

## Adding a structure detector

Structure detectors are pure Python; no C++ changes. A detector recognizes
a known problem class (set partitioning, max-cut, TSP, etc.) and routes it
to a compact specialized QUBO, sidestepping the brittle penalty-tuning
process for that class.

### Step-by-step

1. **Add a recognizer** to
   [`highspy_quantum/structure.py`](../python/highspy_quantum/structure.py):
   ```python
   def _detect_my_class(sub: MipSubproblem) -> bool:
       # cheap shape check on sub.linear, sub.row_*, sub.coef_value
       return ...
   ```
2. **Wire it into `detect()`** in `structure.py`, keeping the first-match
   order sensible (most specific detectors first).
3. **Author the specialized builder** at
   `highspy_quantum/reformulation/<tag>.py` exposing
   `build(sub: MipSubproblem) -> Bqm`. Use the literature formulation
   for your class. See `reformulation/set_partitioning.py` for the
   canonical pattern.
4. **Hook it into `build_for()`** in `structure.py`.
5. **Tests** at `tests/test_structure.py`:
   - Detector triggers on a hand-crafted instance.
   - Builder produces a BQM whose ground state matches the known optimum.
   - Detector does NOT trigger on instances that don't match.

### Structure detection that exists today

| Tag | Detector | Builder |
|---|---|---|
| `qubo` | binary + no constraints | falls through to generic (already optimal) |
| `set_partitioning` | binary + `Ax=1` + 0/1 coefficients | compact `(Σ-1)²` penalty |
| `max_cut` | binary + `4k` rows of size 3 (y-linearization) | recovers vertex-only QUBO |
| `tsp` | binary + `2n` rows + n² vars | stub (falls through; full Lucas-2014 not implemented) |

## Adding a C++ extraction mode

Sub-MIP extraction is the only place where C++ work is required. Add a
new function to `HighsQubo.{h,cpp}` mirroring the shape of
`extractFromMip` / `extractRinsNeighborhood`:

```cpp
QuboSubproblem extractMyNeighborhood(
    const HighsMipSolverData& mipdata,
    HighsInt max_vars,
    /* mode-specific args */,
    QuboReason& reason);
```

Then dispatch on a new `mip_quantum_heuristic_mode` value from
`HighsMipSolverData::quantumHeuristic()`.

## Contribution guide

- The fork policy: this lives in our private fork; nothing here goes
  upstream (HiGHS rejects AI-generated PRs and core-solver PRs per
  `CONTRIBUTING.md`).
- Branching: feature branches off `main`. Squash merge.
- Tests: pytest passes, plus `cmake --build` succeeds for both
  `QUANTUM=OFF` and `QUANTUM=ON`.
- Diagrams: regenerate via `highs/quantum/docs/assets/build_assets.sh`
  whenever the architecture changes. CI verifies no drift.
