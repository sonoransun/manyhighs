use highs::parallel::{solve_many, CancelToken, HighsPool, SolveOptions};
use highs::{Highs, ModelStatus};
use std::sync::Arc;

/// Deterministic 0/1 knapsack parameterized by a seed (so different seeds give
/// genuinely different problems). With threads=1 HiGHS is deterministic.
fn build_knapsack(h: &mut Highs, n: usize, seed: usize) {
    let value: Vec<f64> = (0..n).map(|i| (((i * 7 + seed * 3) % 13) + 1) as f64).collect();
    let weight: Vec<f64> = (0..n).map(|i| (((i * 5 + seed) % 11) + 1) as f64).collect();
    let capacity: f64 = weight.iter().sum::<f64>() * 0.45 + (seed % 5) as f64;

    let xs: Vec<_> = (0..n).map(|_| h.add_binary().unwrap()).collect();
    let used = highs::qsum(xs.iter().zip(&weight).map(|(&x, &w)| w * x));
    h.add_constr(used.le(capacity)).unwrap();
    h.maximize(highs::qsum(xs.iter().zip(&value).map(|(&x, &v)| v * x)))
        .unwrap();
}

#[test]
fn parallel_matches_serial() {
    let n_problems = 24;
    let items = 14;

    // Serial reference: one reused instance.
    let mut serial = Vec::with_capacity(n_problems);
    {
        let mut h = Highs::new().silenced();
        h.set_threads(1).unwrap();
        for seed in 0..n_problems {
            h.clear_model().unwrap();
            build_knapsack(&mut h, items, seed);
            let status = h.run().unwrap();
            serial.push((status, h.objective_value()));
        }
    }

    // Parallel batch.
    let builders: Vec<_> = (0..n_problems)
        .map(|seed| move |h: &mut Highs| {
            build_knapsack(h, items, seed);
            Ok(())
        })
        .collect();
    let parallel = solve_many(builders, SolveOptions::default());

    assert_eq!(parallel.len(), n_problems);
    for (i, r) in parallel.iter().enumerate() {
        let out = r.as_ref().unwrap();
        assert_eq!(out.status, serial[i].0, "status mismatch at {i}");
        assert!(
            (out.objective - serial[i].1).abs() < 1e-6,
            "objective mismatch at {i}: {} vs {}",
            out.objective,
            serial[i].1
        );
        assert_eq!(out.status, ModelStatus::Optimal);
    }
}

#[test]
fn solve_many_preserves_order() {
    // spec k: minimize x with x >= k  -> objective k
    let builders: Vec<_> = (0..16usize)
        .map(|k| move |h: &mut Highs| {
            let x = h.add_var(0.0, 1.0e30)?;
            h.add_constr(x.ge(k as f64))?;
            h.minimize(x)
        })
        .collect();
    let results = solve_many(builders, SolveOptions::default());
    for (k, r) in results.iter().enumerate() {
        assert!((r.as_ref().unwrap().objective - k as f64).abs() < 1e-9);
    }
}

#[test]
fn pool_reuse_across_threads() {
    let pool = Arc::new(HighsPool::new(4, 1));
    let mut handles = Vec::new();
    for k in 0..8usize {
        let pool = pool.clone();
        handles.push(std::thread::spawn(move || {
            pool.with(|h| {
                let x = h.add_var(0.0, 1.0e30).unwrap();
                h.add_constr(x.ge(k as f64)).unwrap();
                h.minimize(x).unwrap();
                h.run().unwrap();
                h.objective_value()
            })
        }));
    }
    let mut objs: Vec<f64> = handles.into_iter().map(|h| h.join().unwrap()).collect();
    objs.sort_by(|a, b| a.partial_cmp(b).unwrap());
    for (k, o) in objs.iter().enumerate() {
        assert!((o - k as f64).abs() < 1e-9);
    }
}

#[test]
fn pre_cancelled_token_interrupts() {
    // Deterministic: cancel before running, so the first interrupt check stops it.
    let token = CancelToken::new();
    token.cancel();

    let mut h = Highs::new().silenced();
    build_knapsack(&mut h, 40, 1);
    h.set_cancel_token(token).unwrap();
    assert_eq!(h.run().unwrap(), ModelStatus::Interrupt);
}

#[cfg(feature = "rayon")]
#[test]
fn rayon_par_solve_many_matches_serial() {
    use highs::parallel::par_solve_many;
    let seeds: Vec<usize> = (0..20).collect();
    let results = par_solve_many(&seeds, |&seed, h| {
        build_knapsack(h, 14, seed);
        Ok(())
    });

    let mut h = Highs::new().silenced();
    h.set_threads(1).unwrap();
    for (i, &seed) in seeds.iter().enumerate() {
        h.clear_model().unwrap();
        build_knapsack(&mut h, 14, seed);
        h.run().unwrap();
        assert!((results[i].as_ref().unwrap().objective - h.objective_value()).abs() < 1e-6);
    }
}

#[test]
fn start_solve_roundtrip() {
    // Plumbing test (no timing dependence): a small solve via the async handle.
    let mut h = Highs::new().silenced();
    let x = h.add_var(0.0, 1.0e30).unwrap();
    h.add_constr(x.ge(3.0)).unwrap();
    h.minimize(x).unwrap();

    let running = h.start_solve();
    let (status, solved) = running.join().unwrap();
    assert_eq!(status, ModelStatus::Optimal);
    assert!((solved.objective_value() - 3.0).abs() < 1e-9);
}
