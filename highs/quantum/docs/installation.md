# Installation

## Standalone Python CLI (no HiGHS build required)

```
pip install -e highs/quantum/python
```

That installs the `highs-quantum` script + the `highspy_quantum` Python
package with only the classical and exact backends (numpy is the sole
runtime dep). For vendor backends, pick the extras you need:

```
pip install -e 'highs/quantum/python[dwave]'      # adds dwave-ocean-sdk
pip install -e 'highs/quantum/python[qiskit]'     # qiskit + qiskit-optimization + qiskit-aer
pip install -e 'highs/quantum/python[rigetti]'    # pyquil
pip install -e 'highs/quantum/python[braket]'     # amazon-braket-sdk
pip install -e 'highs/quantum/python[dwave,qiskit,rigetti,braket]'   # all four
```

Verify:
```
highs-quantum --protocol-version       # prints "1"
highs-quantum solve sample_qubo.json --backend exact
```

## C++ heuristic (requires HiGHS build with `-DQUANTUM=ON`)

```
cmake -S . -B build -DQUANTUM=ON -DFAST_BUILD=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
```

`-DFAST_BUILD=ON` is required (HiGHS will hard-fail at configure time
otherwise — see [hooked-into-highs](hooked-into-highs.md)).

Verify the build picked up the heuristic:
```
./build/bin/highs --help | grep quantum    # prints nothing (options not in --help)
./build/bin/highs <(echo "ROWS\nN  COST\nENDATA") --options_file <(echo "mip_quantum_heuristic=classical")
# expect: "Set option mip_quantum_heuristic to \"classical\""
```

## Per-backend credentials

Credentials are read from standard vendor env vars; the heuristic never
stores them.

| Backend  | Env var(s)                            | What it enables                          |
|----------|---------------------------------------|------------------------------------------|
| `dwave`  | `DWAVE_API_TOKEN`                     | LeapHybridSampler / direct QPU embedding |
|          | (unset) → falls back to `neal` SA     | local simulated annealing                |
| `qiskit` | `IBMQ_TOKEN` + `--qiskit-backend=…`   | IBM Runtime job submission               |
|          | (unset) → defaults to qiskit-aer      | local state-vector QAOA simulation       |
| `rigetti`| `QCS_SETTINGS` + `--rigetti-qpu=…`    | Rigetti QPU via QCS                      |
|          | (unset) → defaults to local sim       | pyQuil WavefunctionSimulator             |
| `braket` | AWS creds + `--braket-device=arn:…`   | submit to IonQ / Quantinuum / Pasqal     |
|          | (unset) → defaults to LocalSimulator  | in-process QAOA simulation               |

Extras for backends not listed above (`--qiskit-backend=…`, etc.) go
into the `quantum_extra_args` HiGHS option or `--timeout`-style flags
on the CLI.

## Optional: development install

For running the test suite, building docs, regenerating diagrams:

```
pip install -e 'highs/quantum/python[dev]'   # adds pytest
.venv/bin/pip install termtosvg matplotlib   # for asset regeneration

cd highs/quantum/docs/assets
./build_assets.sh                            # regenerate every diagram + GIF + screencast
```
