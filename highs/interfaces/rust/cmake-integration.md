# Optional: building the Rust interface from CMake

The Rust crates build standalone with `cargo`, and `highs-sys`'s build script
already drives CMake for the `bundled` path. If you instead want a top-level
CMake build to *also* produce the Rust artifacts (parity with the C#/Fortran
interfaces), wire it as an **opt-in** target that reuses the library CMake just
built — rather than letting cargo rebuild HiGHS, which would cause a
CMake → cargo → CMake recursion.

The core `CMakeLists.txt` is intentionally left untouched (the upstream project
does not accept changes to it). Add the snippet below to your *own* top-level
file, or `include()` it, guarded by an option:

```cmake
option(RUST "Build the Rust interface" OFF)

if(RUST)
  find_program(CARGO cargo REQUIRED)

  # Reuse the libhighs that this CMake build produces/installs. Point the crate
  # at it via HIGHS_DIR + the `pkg-config`/system path so cargo links it instead
  # of rebuilding from source.
  add_custom_target(rust_highs ALL
    COMMAND ${CMAKE_COMMAND} -E env
            HIGHS_DIR=${CMAKE_BINARY_DIR}
            ${CARGO} build --release
            --manifest-path ${CMAKE_SOURCE_DIR}/highs/interfaces/rust/Cargo.toml
            --no-default-features
    DEPENDS highs
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/highs/interfaces/rust
    COMMENT "Building HiGHS Rust interface (linking the just-built libhighs)"
    VERBATIM)
endif()
```

`HIGHS_DIR=${CMAKE_BINARY_DIR}` makes `highs-sys` discover the freshly built
`lib/libhighs.*` and the generated `HConfig.h` in the CMake binary tree, and
`--no-default-features` disables the crate's own `bundled` CMake invocation.
