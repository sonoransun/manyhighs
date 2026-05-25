# HiGHS Rust bindings

Safe, idiomatic Rust bindings to the [HiGHS](https://highs.dev) optimization
solver (LP, mixed-integer, convex QP), with a **GIL-free parallel runtime** for
solving many independent models concurrently across OS threads.

Two crates:

| Crate | What it is |
|-------|------------|
| [`highs-sys`](highs-sys) | Raw `bindgen` FFI over the C API (`highs/interfaces/highs_c_api.h`). Every `Highs_*` function and `kHighs*` constant of HiGHS 1.14. |
| [`highs`](highs) | Safe wrapper: typed enums, `Result` errors, an expression DSL, callbacks, one-shot solves, and the parallel runtime. Re-exports the raw layer as `highs::ffi`. |

## Quick start

```rust
use highs::{Highs, ModelStatus};

// max 2x + 3y  s.t.  x + y <= 4,  x + 3y <= 6,  x,y >= 0
let mut h = Highs::new().silenced();
let x = h.add_var(0.0, f64::INFINITY)?;
let y = h.add_var(0.0, f64::INFINITY)?;
h.add_constr((x + y).le(4.0))?;
h.add_constr((x + 3.0 * y).le(6.0))?;
h.maximize(2.0 * x + 3.0 * y)?;

assert_eq!(h.run()?, ModelStatus::Optimal);
println!("objective = {}", h.objective_value()); // 9
```

## The GIL-free parallel runtime

HiGHS's work-stealing scheduler lives in thread-local storage, and a `Highs`
instance is `Send`, so N instances solve concurrently on N threads with no
shared state — exactly what Python's GIL prevents. Pin each instance to one
internal thread (the default of every batch API here) to avoid oversubscription.

```rust
use highs::parallel::{solve_many, SolveOptions};

let builders: Vec<_> = (0..1000).map(|k| move |h: &mut highs::Highs| {
    // build model k ...
    let x = h.add_var(0.0, 1e30)?;
    h.add_constr(x.ge(k as f64))?;
    h.minimize(x)
}).collect();

let results = solve_many(builders, SolveOptions::default()); // one per core, in order
```

Also available: `parallel::par_solve_many` (rayon, feature `rayon`), a reusable
`parallel::HighsPool`, a cross-thread `parallel::CancelToken`, and
`Highs::start_solve` for cancellable async solves.

See [`examples/par_scaling.rs`](highs/examples/par_scaling.rs) for a scaling
demo (near-linear speedup up to the physical core count):

```
cargo run --release --example par_scaling --no-default-features
```

## Building / linking

By default the build compiles HiGHS from this repository's source via CMake
(producing a static `libhighs.a`) and generates bindings with bindgen:

```
cargo build           # bundled: builds libhighs from source, runs bindgen
```

Faster alternatives:

| How | Command |
|-----|---------|
| Link a prebuilt tree (has `lib/` + `HConfig.h`) | `HIGHS_DIR=/path/to/build cargo build` |
| System install via pkg-config | `cargo build --no-default-features --features pkg-config` |
| Skip bindgen (no libclang); use checked-in bindings | `cargo build -p highs-sys --no-default-features` |

`HIGHS_DIR` always wins over the `bundled` feature. With no env var and no
`bundled`/`pkg-config` feature, the build auto-detects a sibling
`build_on`/`build_off` tree in the repo root — so inside this checkout,
`cargo test --no-default-features` needs no configuration.

### Feature flags (`highs` crate)

- `bundled` *(default)* — build HiGHS from source + bindgen.
- `pkg-config` — discover a system HiGHS instead of building it.
- `rayon` — enable `parallel::par_solve_many`.

## Capability coverage

The safe API covers the high-value surface: LP/MIP/QP loading (`pass_lp`,
`pass_mip`, `pass_qp`), incremental building and the expression DSL, options
(typed + convenience), solution/dual/basis/info extraction, callbacks (with
panic-safe trampolines), one-shot `solve_lp`/`solve_mip`/`solve_qp`, file I/O,
and introspection. **Anything not yet wrapped is reachable** through
`highs::ffi`, which re-exports all ~175 raw `Highs_*` functions (e.g. ranging,
IIS, feasibility relaxation, basis-matrix solves).

## Testing

```
cargo test  --no-default-features          # fast: prebuilt lib + checked-in bindings
cargo clippy --no-default-features --all-targets
cargo test                                 # exercises the bundled CMake + bindgen path
```

## CMake integration (optional)

The crate is normally driven by `cargo`; its build script already invokes CMake
for the `bundled` path. To build the Rust interface *from* a top-level CMake
build without a CMake→cargo→CMake recursion, point cargo at the tree CMake just
installed and use the `pkg-config`/`HIGHS_DIR` path — see
[`cmake-integration.md`](cmake-integration.md). The core `CMakeLists.txt` is not
modified.
