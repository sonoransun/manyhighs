# Backends

Six backends ship today. Each implements a `Backend.solve(bqm, time_limit_s)`
method that returns one or more candidate samples; see
[architecture](architecture.md) for the interface.

## `classical` — simulated annealing

Pure-numpy. No vendor SDK. Multi-start SA with linear-in-time cooling.
Good for sanity-checking the integration end-to-end and as a baseline to
beat. Single-thread; bounded by `time_limit_s`.

## `exact` — brute force

Pure-numpy. Enumerates all 2ⁿ binary assignments. Refuses to run on more
than 24 vars (16 M evaluations is already several seconds in pure Python).
Used as ground truth in the test suite.

## `dwave` — D-Wave Leap / Ocean

| Mode | When | What it uses |
|---|---|---|
| Cloud, hybrid | `DWAVE_API_TOKEN` set AND `num_vars >= 200` (or `HIGHS_QUANTUM_DWAVE_LEAP_THRESHOLD`) | `LeapHybridSampler` |
| Cloud, direct QPU | token set, smaller problem | `EmbeddingComposite(DWaveSampler())` |
| Local fallback | no token, or cloud import fails | `neal.SimulatedAnnealingSampler` |

The Bqm→dimod conversion is `Bqm.to_dimod()` in `model.py`.

Extra args (via HiGHS option `quantum_extra_args` or CLI flag forwarding):
- `--num-reads=N` (QPU path; default 1000)
- `--chain-strength=F` (QPU path)

Threshold above which we prefer Leap can be overridden via the
`HIGHS_QUANTUM_DWAVE_LEAP_THRESHOLD` env var.

## `qiskit` — IBM Qiskit Optimization (QAOA)

| Mode | When | What it uses |
|---|---|---|
| Local Aer simulator | (default) | `qiskit_aer.primitives.Sampler` + QAOA(reps) |
| IBM Runtime hardware | `IBMQ_TOKEN` set AND `--qiskit-backend=ibm_…` in extra-args | `qiskit_ibm_runtime.Sampler` |

QAOA reps scale with the time budget: `reps = min(5, 1 + int(time_limit / 5))`.

Size caps:
- Aer: 20 vars (state vector grows as 2ⁿ). Override via `HIGHS_QUANTUM_QISKIT_MAX_AER_VARS`.
- Runtime: 50 vars (queue latency makes larger problems impractical).

## `rigetti` — pyQuil QAOA

Hand-rolled QAOA over Pauli-Z cost terms (pyQuil has no `MinimumEigenOptimizer`-style wrapper).
Cost Hamiltonian from the BQM, mixer = sum-of-X, classical optimizer =
`scipy.optimize.minimize(method="COBYLA")`.

| Mode | When | What it uses |
|---|---|---|
| Local | (default) | `pyquil.api.WavefunctionSimulator` |
| QCS hardware | `--rigetti-qpu=Aspen-M-3` (or similar) in extra-args | `pyquil.api.get_qc(...)` |

Size cap on local: 16 vars (state vector × parameter sweep gets slow).

## `braket` — AWS Braket

Same QAOA shape as Rigetti, but written against Braket's `Circuit` API.

| Mode | When | What it uses |
|---|---|---|
| Local | (default) | `braket.devices.LocalSimulator` |
| Cloud device | `--braket-device=arn:aws:braket:...` in extra-args + AWS creds in env | `braket.aws.AwsDevice` |

Cloud devices include IonQ, Quantinuum, Rigetti, Pasqal — pick via ARN.
**These cost money per shot**; the backend logs a warning before
submitting jobs.

Size cap on local: 22 vars.

## Choosing a backend

| If you want… | Pick |
|---|---|
| To validate the integration end-to-end with no creds | `classical` or `exact` |
| Ground truth on small problems | `exact` (≤24 vars) |
| Largest problem size today | `dwave` Leap hybrid (up to ~1M vars) |
| Vendor-neutral cross-comparison | `highs-quantum benchmark` across all four |
| Real noisy-hardware results | `dwave` direct QPU (small), or `braket` with IonQ ARN |
| Free local gate-based simulation | `qiskit` (Aer) or `braket` (LocalSimulator) |

For research, see also [theory](theory.md) — penalty reformulation
quality often matters more than backend choice on real-world MIPs.
