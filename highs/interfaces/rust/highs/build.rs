//! Re-emit an rpath to the HiGHS shared library so this crate's test, example,
//! and benchmark binaries can locate `libhighs.so` at runtime without
//! `LD_LIBRARY_PATH`. The directory is published by `highs-sys` (which has
//! `links = "highs"`) as the `DEP_HIGHS_LIB_DIR` metadata variable.
//!
//! When HiGHS is linked statically (the `bundled` default), there is no shared
//! object to find and this rpath is simply inert.

use std::env;

fn main() {
    println!("cargo:rerun-if-changed=build.rs");
    if let Ok(dir) = env::var("DEP_HIGHS_LIB_DIR") {
        let target = env::var("TARGET").unwrap_or_default();
        if !target.contains("msvc") {
            println!("cargo:rustc-link-arg=-Wl,-rpath,{dir}");
        }
    }
}
