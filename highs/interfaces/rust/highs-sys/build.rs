//! Build script for `highs-sys`.
//!
//! Responsibilities:
//!   1. Locate (or build) the HiGHS C++ library and the generated `HConfig.h`.
//!   2. Emit the cargo link directives.
//!   3. Generate Rust FFI bindings with bindgen (unless `run-bindgen` is off,
//!      in which case the checked-in `src/bindings_pregenerated.rs` is used).
//!
//! Library discovery order (first match wins):
//!
//! - `HIGHS_DIR`: a build/install tree containing `lib/` and `HConfig.h` (e.g.
//!   this repo's `build_on/`). Always honored.
//! - feature `bundled`: compile libhighs from source via the `cmake` crate.
//! - feature `pkg-config`: discover a system install via its `highs` module.
//! - auto-detect: a sibling `build_on`/`build_off` in the repo root.

use std::env;
use std::path::{Path, PathBuf};

/// What we resolved: where to link from, where `HConfig.h` lives, and whether
/// we are linking a static archive or a shared object.
struct Located {
    lib_dir: PathBuf,
    // Only consumed by bindgen; unused when the `run-bindgen` feature is off.
    #[cfg_attr(not(feature = "run-bindgen"), allow(dead_code))]
    hconfig_dir: PathBuf,
    static_link: bool,
}

fn repo_root() -> PathBuf {
    // Crate dir: <repo>/highs/interfaces/rust/highs-sys -> repo root is 4 up.
    let manifest = PathBuf::from(env::var("CARGO_MANIFEST_DIR").unwrap());
    manifest
        .join("..")
        .join("..")
        .join("..")
        .join("..")
        .canonicalize()
        .expect("failed to canonicalize repo root from CARGO_MANIFEST_DIR")
}

/// Treat `dir` as a build/install tree: lib in `dir/lib` (or `dir`), and
/// `HConfig.h` at `dir/HConfig.h` (build tree) or `dir/include/.../HConfig.h`.
fn locate_in_tree(dir: &Path) -> Option<Located> {
    let lib_dir = if dir.join("lib").is_dir() {
        dir.join("lib")
    } else {
        dir.to_path_buf()
    };
    let has_lib = lib_dir.join("libhighs.so").exists()
        || lib_dir.join("libhighs.a").exists()
        || lib_dir.join("libhighs.dylib").exists();
    if !has_lib {
        return None;
    }
    let static_link = lib_dir.join("libhighs.a").exists()
        && !lib_dir.join("libhighs.so").exists()
        && !lib_dir.join("libhighs.dylib").exists();

    let hconfig_dir = [
        dir.to_path_buf(),
        dir.join("include").join("highs"),
        dir.join("include"),
    ]
    .into_iter()
    .find(|p| p.join("HConfig.h").exists())?;

    Some(Located {
        lib_dir,
        hconfig_dir,
        static_link,
    })
}

fn locate(repo: &Path) -> Located {
    // 1. Explicit HIGHS_DIR always wins (fast path for development/CI).
    if let Some(dir) = env::var_os("HIGHS_DIR") {
        let dir = PathBuf::from(dir);
        return locate_in_tree(&dir)
            .unwrap_or_else(|| panic!("HIGHS_DIR={} has no libhighs/HConfig.h", dir.display()));
    }

    // 2. Build from source via CMake.
    #[cfg(feature = "bundled")]
    {
        return build_with_cmake(repo);
    }

    // 3. pkg-config.
    #[cfg(feature = "pkg-config")]
    {
        let lib = pkg_config::Config::new()
            .probe("highs")
            .expect("pkg-config could not find the `highs` module");
        let hconfig_dir = lib
            .include_paths
            .iter()
            .find(|p| p.join("HConfig.h").exists())
            .cloned()
            .or_else(|| lib.include_paths.first().cloned())
            .expect("pkg-config returned no include paths for highs");
        // pkg-config already emitted link directives; record lib_dir for bindgen only.
        return Located {
            lib_dir: lib
                .link_paths
                .first()
                .cloned()
                .unwrap_or_else(|| repo.join("lib")),
            hconfig_dir,
            static_link: false,
        };
    }

    // 4. Convenience auto-detect of an existing build tree in the repo.
    #[allow(unreachable_code)]
    {
        for cand in ["build_on", "build_off", "build"] {
            if let Some(found) = locate_in_tree(&repo.join(cand)) {
                return found;
            }
        }
        panic!(
            "could not locate HiGHS. Set HIGHS_DIR, enable the `bundled` feature, \
             or build the repo (e.g. `cmake -S . -B build_on && cmake --build build_on`)."
        );
    }
}

#[cfg(feature = "bundled")]
fn build_with_cmake(repo: &Path) -> Located {
    // Always build the solver optimized: a debug HiGHS is far slower and enables
    // internal asserts that are not about binding correctness. Overridable via
    // HIGHS_CMAKE_PROFILE (e.g. "Debug") for those who want the extra checks.
    let profile = env::var("HIGHS_CMAKE_PROFILE").unwrap_or_else(|_| "Release".to_string());
    // Build only libhighs as a static, position-independent library.
    let dst = cmake::Config::new(repo)
        .profile(&profile)
        .define("FAST_BUILD", "ON")
        .define("BUILD_SHARED_LIBS", "OFF")
        .define("BUILD_TESTING", "OFF")
        .define("BUILD_EXAMPLES", "OFF")
        .define("CSHARP", "OFF")
        .define("FORTRAN", "OFF")
        .define("PYTHON_BUILD_SETUP", "OFF")
        .define("ZLIB", "ON")
        .define("CMAKE_POSITION_INDEPENDENT_CODE", "ON")
        .build();

    // The cmake crate installs into `dst`; HConfig.h is generated in the build
    // tree at `dst/build/HConfig.h`. Prefer the build tree (guaranteed to match
    // the just-compiled lib), then the install tree.
    let lib_dir = if dst.join("lib").is_dir() {
        dst.join("lib")
    } else {
        dst.join("build").join("lib")
    };
    let hconfig_dir = [dst.join("build"), dst.join("include").join("highs"), dst.clone()]
        .into_iter()
        .find(|p| p.join("HConfig.h").exists())
        .expect("cmake build produced no HConfig.h");

    Located {
        lib_dir,
        hconfig_dir,
        static_link: true,
    }
}

/// Name of the C++ standard library to link (needed for static linking; harmless
/// otherwise). None on MSVC.
fn cxx_stdlib() -> Option<&'static str> {
    let target = env::var("TARGET").unwrap_or_default();
    if target.contains("msvc") {
        None
    } else if target.contains("apple") || target.contains("freebsd") {
        Some("c++")
    } else {
        Some("stdc++")
    }
}

/// Help clang-sys find libclang if the environment hasn't set LIBCLANG_PATH.
#[cfg(feature = "run-bindgen")]
fn ensure_libclang() {
    if env::var_os("LIBCLANG_PATH").is_some() {
        return;
    }
    for dir in [
        "/usr/lib/llvm-18/lib",
        "/usr/lib/llvm-17/lib",
        "/usr/lib/llvm-16/lib",
        "/usr/lib/x86_64-linux-gnu",
        "/usr/local/lib",
    ] {
        let p = Path::new(dir);
        if p.join("libclang.so").exists()
            || p.join("libclang.dylib").exists()
            || std::fs::read_dir(p)
                .map(|rd| {
                    rd.filter_map(|e| e.ok()).any(|e| {
                        e.file_name()
                            .to_string_lossy()
                            .starts_with("libclang.so")
                    })
                })
                .unwrap_or(false)
        {
            env::set_var("LIBCLANG_PATH", dir);
            return;
        }
    }
}

#[cfg(feature = "run-bindgen")]
fn generate_bindings(api_include: &Path, hconfig_dir: &Path) {
    ensure_libclang();
    let out = PathBuf::from(env::var("OUT_DIR").unwrap()).join("bindings.rs");
    let bindings = bindgen::Builder::default()
        .header("wrapper.h")
        .clang_arg("-xc++")
        .clang_arg("-std=c++11")
        .clang_arg(format!("-I{}", api_include.display()))
        .clang_arg(format!("-I{}", hconfig_dir.display()))
        .allowlist_function("Highs_.*")
        .allowlist_type("Highs.*")
        .allowlist_var("kHighs.*")
        .size_t_is_usize(true)
        .layout_tests(true)
        .generate_comments(false)
        .derive_default(true)
        .derive_debug(true)
        .generate()
        .expect("bindgen failed to generate HiGHS bindings");
    bindings
        .write_to_file(&out)
        .expect("failed to write bindings.rs");
}

fn main() {
    let repo = repo_root();
    let api_include = repo.join("highs"); // resolves interfaces/, lp_data/, util/
    let located = locate(&repo);

    println!("cargo:rerun-if-changed=wrapper.h");
    println!("cargo:rerun-if-changed=build.rs");
    println!("cargo:rerun-if-env-changed=HIGHS_DIR");
    println!("cargo:rerun-if-env-changed=LIBCLANG_PATH");
    // Export the include dir so the safe crate / downstream can reuse it.
    println!("cargo:include={}", api_include.display());
    println!("cargo:lib_dir={}", located.lib_dir.display());

    #[cfg(feature = "run-bindgen")]
    generate_bindings(&api_include, &located.hconfig_dir);

    // pkg-config already emits link directives; otherwise emit our own.
    let used_pkg_config = cfg!(feature = "pkg-config") && env::var_os("HIGHS_DIR").is_none();
    let used_pkg_config = used_pkg_config && !cfg!(feature = "bundled");
    if !used_pkg_config {
        println!(
            "cargo:rustc-link-search=native={}",
            located.lib_dir.display()
        );
        let kind = if located.static_link { "static" } else { "dylib" };
        println!("cargo:rustc-link-lib={}=highs", kind);

        // Transitive deps: needed when statically linking; harmless for dylib.
        if located.static_link {
            if let Some(cxx) = cxx_stdlib() {
                println!("cargo:rustc-link-lib={}", cxx);
            }
            println!("cargo:rustc-link-lib=z");
        } else {
            // Embed an rpath so binaries/tests find the shared object at runtime
            // without requiring LD_LIBRARY_PATH (ELF and Mach-O both accept this).
            let target = env::var("TARGET").unwrap_or_default();
            if !target.contains("msvc") {
                println!(
                    "cargo:rustc-link-arg=-Wl,-rpath,{}",
                    located.lib_dir.display()
                );
            }
        }
    }
}
