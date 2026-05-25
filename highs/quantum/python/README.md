# highspy-quantum

Python package for quantum-assisted MIP heuristics in HiGHS. Two roles:

1. **Standalone CLI** — `highs-quantum solve|benchmark`.
2. **Subprocess backend** — called by the C++ heuristic when HiGHS is
   built with `-DQUANTUM=ON`.

## Install

```
pip install -e .                              # classical + exact (no vendor SDK)
pip install -e '.[dwave]'                     # adds dwave-ocean-sdk
pip install -e '.[qiskit]'                    # adds qiskit + qiskit-aer
pip install -e '.[rigetti]'                   # adds pyquil
pip install -e '.[braket]'                    # adds amazon-braket-sdk
pip install -e '.[dwave,qiskit,rigetti,braket]'   # all four vendors
```

## Documentation

Full documentation, diagrams, and animated examples live at
[`highs/quantum/docs/`](../docs/index.md) in the source tree:

- [`installation`](../docs/installation.md) — pip + cmake setup, env vars
- [`cli`](../docs/cli.md) — `highs-quantum` reference
- [`hooked-into-highs`](../docs/hooked-into-highs.md) — `-DQUANTUM=ON`, options, MIP log
- [`backends`](../docs/backends.md) — per-vendor coverage
- [`architecture`](../docs/architecture.md) — internals + SVG diagrams
- [`extending`](../docs/extending.md) — adding a backend or detector
- [`theory`](../docs/theory.md) — QUBO, repair, RINS (with GIFs)
- [`troubleshooting`](../docs/troubleshooting.md) — common errors

## Tests

```
pytest tests/
```

Vendor-dependent tests skip themselves when the SDK isn't installed.
