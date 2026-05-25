use highs::{CallbackAction, CallbackType, Highs, ModelStatus};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

/// A deterministic 0/1 knapsack with enough items to require branch-and-bound.
fn knapsack(h: &mut Highs, n: usize) {
    let value: Vec<f64> = (0..n).map(|i| ((i * 7 % 13) + 1) as f64).collect();
    let weight: Vec<f64> = (0..n).map(|i| ((i * 5 % 11) + 1) as f64).collect();
    let capacity: f64 = weight.iter().sum::<f64>() / 2.0;

    let xs: Vec<_> = (0..n).map(|_| h.add_binary().unwrap()).collect();
    let cap = highs::qsum(xs.iter().zip(&weight).map(|(&x, &w)| w * x));
    h.add_constr(cap.le(capacity)).unwrap();
    h.maximize(highs::qsum(xs.iter().zip(&value).map(|(&x, &v)| v * x)))
        .unwrap();
}

#[test]
fn mip_improving_solution_callback_fires() {
    let mut h = Highs::new().silenced();
    knapsack(&mut h, 12);

    let count = Arc::new(AtomicUsize::new(0));
    let seen_obj = Arc::new(AtomicUsize::new(0));
    let c = count.clone();
    let s = seen_obj.clone();
    h.set_callback(move |ctx| {
        c.fetch_add(1, Ordering::SeqCst);
        if ctx.objective().is_finite() {
            s.fetch_add(1, Ordering::SeqCst);
        }
        CallbackAction::Continue
    })
    .unwrap();
    h.start_callback(CallbackType::MipImprovingSolution).unwrap();

    assert_eq!(h.run().unwrap(), ModelStatus::Optimal);
    assert!(count.load(Ordering::SeqCst) >= 1, "callback never fired");
    assert!(seen_obj.load(Ordering::SeqCst) >= 1, "objective not readable");
}

#[test]
fn interrupt_stops_mip() {
    let mut h = Highs::new().silenced();
    knapsack(&mut h, 40);

    let fired = Arc::new(AtomicUsize::new(0));
    let f = fired.clone();
    h.set_callback(move |_ctx| {
        f.fetch_add(1, Ordering::SeqCst);
        CallbackAction::Interrupt
    })
    .unwrap();
    h.start_callback(CallbackType::MipInterrupt).unwrap();

    let status = h.run().unwrap();
    assert!(fired.load(Ordering::SeqCst) >= 1, "interrupt callback never fired");
    assert_eq!(status, ModelStatus::Interrupt);
}

#[test]
fn panic_in_callback_is_caught_and_reraised() {
    let mut h = Highs::new().silenced();
    knapsack(&mut h, 12);

    h.set_callback(move |_ctx| {
        panic!("boom from inside the callback");
    })
    .unwrap();
    h.start_callback(CallbackType::MipImprovingSolution).unwrap();

    // The panic is caught at the FFI boundary (no process abort) and re-raised
    // from run(); catch it here and confirm we survived.
    let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| h.run()));
    assert!(result.is_err(), "panic should propagate out of run()");

    // The process is still alive: a fresh solve works.
    let mut h2 = Highs::new().silenced();
    knapsack(&mut h2, 8);
    assert_eq!(h2.run().unwrap(), ModelStatus::Optimal);
}
