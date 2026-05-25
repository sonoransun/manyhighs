# Troubleshooting

Common failure modes and the actual fix for each.

## `best sample violated constraints`

The Python backend returned samples but none satisfied the problem
constraints; HiGHS rejected them all via `trySolution`.

**Why:** Penalty weight too small relative to the objective magnitude.
The backend optimized the penalty-augmented QUBO but the penalty didn't
dominate hard enough to enforce feasibility.

**Fixes (in order of effort):**

1. The CLI already retries with doubled penalty up to 4 times — if that
   didn't help, the problem may be structurally hard for the chosen
   backend.
2. If the problem is set-partitioning, max-cut, or a known structure,
   verify `structure.detect()` recognized it. The specialized
   reformulation bypasses penalty tuning entirely.
3. Increase `quantum_time_limit` so SA / QAOA gets more iterations.
4. Try a different backend — `dwave` Leap hybrid handles much larger /
   harder QUBOs than QAOA does.
5. Reduce the subproblem size with `mip_quantum_heuristic_mode=rins`.

## `subprocess exited with status N`

The Python subprocess crashed before writing a result JSON.

**Common causes:**

| Status | Likely cause | Fix |
|---|---|---|
| 1 | `BackendUnavailable` (SDK missing) | `pip install 'highspy-quantum[<backend>]'` |
| 1 | Auth failure | Check vendor env var (`DWAVE_API_TOKEN`, `IBMQ_TOKEN`, etc.) |
| 2 | Argument parsing | The CLI args don't match the version of `highspy_quantum` installed |
| 127 | Python interpreter not found | Set `quantum_python_executable` to the full path |
| Other | Stack trace in subprocess stderr (not captured today) | Run the same command standalone to see the exception |

Reproduce the call manually to see the traceback:
```
python3 -m highspy_quantum solve \
    --backend <name> \
    --in /tmp/highs_qubo_*.in.json \
    --out /tmp/test.out.json \
    --timeout 30
```

## `Q` never appears in the MIP source column

You set `mip_quantum_heuristic=classical` and see
`Quantum heuristic: dispatching` in the log, but the `Q` source
character never shows up.

**Possible reasons:**

1. **The MIP completed before any quantum dispatch returned.** Cloud
   backends are slow; for problems HiGHS solves in <1s the heuristic
   may never finish a call. Increase the problem size or pick a fast
   backend (`classical`, `exact`).
2. **Every quantum sample was rejected by `trySolution`.** This is the
   "best sample violated constraints" path above. The dispatch log line
   will say `accepted=no`.
3. **The MIP presolved to empty.** Look for "Presolve reduced model to
   empty" near the top of the log. The heuristic has nothing to do —
   working as intended. Use a model presolve can't reduce.
4. **Wrong build.** Run `./build/bin/highs` (not the system `highs`).
   The QUANTUM=OFF binary won't fire the heuristic regardless of
   options. Check with `nm build/lib/libhighs.so | grep -i quantum` —
   should show several `highs_quantum` symbols.

## `Quantum heuristic: skipped (model has continuous variables)`

The presolved model has at least one continuous column. Current scope is
binary-only.

**Workarounds:**
- Manually pre-fix continuous variables to their LP-relaxation values
  (changes the problem).
- Wait for a future sprint that extends to general-integer / continuous
  via decomposition.

## `model exceeds quantum heuristic var budget`

The model has more binary variables than the default 2048 cap.

**Fix:** Use `mip_quantum_heuristic_mode=rins` so only the free
variables (those whose LP relaxation differs from the incumbent) go to
the backend. For Sprint-4-era code there's no option to raise the cap;
either reduce the problem upstream or contribute a `quantum_max_vars`
option.

## "Presolve reduced model to empty"

```
Presolve reductions: rows 0(-1); columns 0(-3); nonzeros 0(-3) - Reduced to empty
Presolve: Optimal
```

HiGHS solved the model entirely in presolve. The quantum heuristic
never gets to run on this model.

**Fix:** Use a larger or less trivial problem. The smoke test in
`.github/workflows/quantum-tests.yml` adds a "guard row" with RHS large
enough that presolve can't remove it but doesn't actually constrain the
solution — useful trick for testing.

## Repeated `dispatch` log lines, no `harvest` ever

The worker thread is stuck on the subprocess. Most likely the
subprocess is hung (network timeout, vendor SDK deadlock, etc.).

**Diagnosis:**
1. `ps aux | grep highspy_quantum` to find the subprocess PID.
2. `py-spy dump --pid <PID>` to see what it's blocked on (install
   `py-spy` if needed).
3. Lower `quantum_time_limit` so future calls time out faster. The
   Python side respects `--timeout`; if the backend ignores it, file a
   bug.

## GIF files in docs are stale

`build_assets.sh` regenerates everything. CI will catch drift if you
forget to commit the regenerated files.

```
cd highs/quantum/docs/assets && ./build_assets.sh
git status   # should show changes if anything drifted
```

## The HiGHS Julia Documenter site doesn't show the quantum page

You added `docs/src/quantum.md` but the build doesn't link it.

**Fix:** Edit `docs/make.jl` and add `"quantum.md"` to the page list. The
exact key varies by Documenter version; look for the existing pages
listed alongside `solvers.md`, `installation.md`, etc.

## See also

- [installation](installation.md) — environment setup
- [architecture](architecture.md) — what's happening under the hood
- File an issue with the dispatch / harvest / accepted lines from your
  log; that's enough context to diagnose most issues.
