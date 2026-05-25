//! Demonstrates the GIL-free scaling win: solve a fixed corpus of independent
//! MIPs serially versus across an OS-thread pool (each instance pinned to one
//! internal thread), and report the speedup.
//!
//! Run with:
//!     cargo run --release --example par_scaling --no-default-features
//! (or with default features to build HiGHS from source).

use highs::parallel::{available_parallelism, solve_many, SolveOptions};
use highs::Highs;
use std::time::Instant;

fn build_knapsack(h: &mut Highs, n: usize, seed: usize) {
    // Correlated knapsack: value ~ weight makes the LP bound weak, so
    // branch-and-bound does real work (a meaningful per-solve cost).
    let weight: Vec<f64> = (0..n).map(|i| (((i * 5 + seed) % 23) + 5) as f64).collect();
    let value: Vec<f64> = weight.iter().map(|&w| w + 1.0).collect();
    let capacity: f64 = weight.iter().sum::<f64>() * 0.5;

    let xs: Vec<_> = (0..n).map(|_| h.add_binary().unwrap()).collect();
    let used = highs::qsum(xs.iter().zip(&weight).map(|(&x, &w)| w * x));
    h.add_constr(used.le(capacity)).unwrap();
    h.maximize(highs::qsum(xs.iter().zip(&value).map(|(&x, &v)| v * x)))
        .unwrap();
}

fn main() {
    let n_problems = 64usize;
    let items = 28usize;
    let cores = available_parallelism();
    println!(
        "HiGHS {} — solving {n_problems} knapsacks ({items} items) on {cores} logical CPUs\n",
        highs::version()
    );

    // Serial baseline (one reused instance, threads = 1).
    let t = Instant::now();
    let mut serial_objs = Vec::with_capacity(n_problems);
    {
        let mut h = Highs::new().silenced();
        h.set_threads(1).unwrap();
        for seed in 0..n_problems {
            h.clear_model().unwrap();
            build_knapsack(&mut h, items, seed);
            h.run().unwrap();
            serial_objs.push(h.objective_value());
        }
    }
    let serial = t.elapsed();
    println!("serial (1 thread): {:>8.3?}", serial);

    for &pool in &[2usize, 4, 8, cores.max(1)] {
        let builders: Vec<_> = (0..n_problems)
            .map(|seed| move |h: &mut Highs| {
                build_knapsack(h, items, seed);
                Ok(())
            })
            .collect();
        let t = Instant::now();
        let results = solve_many(
            builders,
            SolveOptions {
                inner_threads: 1,
                pool_threads: pool,
            },
        );
        let dt = t.elapsed();

        // sanity: parallel objectives match the serial baseline
        for (i, r) in results.iter().enumerate() {
            let o = r.as_ref().unwrap().objective;
            assert!((o - serial_objs[i]).abs() < 1e-6, "mismatch at {i}");
        }
        println!(
            "solve_many({pool:>2} threads): {:>8.3?}   speedup {:>4.2}x",
            dt,
            serial.as_secs_f64() / dt.as_secs_f64()
        );
    }
}
