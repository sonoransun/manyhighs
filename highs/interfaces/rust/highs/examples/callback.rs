//! Observe MIP progress through a callback.
//!
//!     cargo run --example callback --no-default-features

use highs::{qsum, CallbackAction, CallbackType, Highs, ModelStatus};

fn main() {
    let n = 30;
    let value: Vec<f64> = (0..n).map(|i| ((i * 7 % 13) + 1) as f64).collect();
    let weight: Vec<f64> = (0..n).map(|i| ((i * 5 % 11) + 1) as f64).collect();
    let capacity: f64 = weight.iter().sum::<f64>() * 0.5;

    let mut h = Highs::new().silenced();
    let xs: Vec<_> = (0..n).map(|_| h.add_binary().unwrap()).collect();
    let used = qsum(xs.iter().zip(&weight).map(|(&x, &w)| w * x));
    h.add_constr(used.le(capacity)).unwrap();
    h.maximize(qsum(xs.iter().zip(&value).map(|(&x, &v)| v * x)))
        .unwrap();

    h.set_callback(|ctx| {
        println!(
            "  incumbent: obj = {:.1}  (nodes = {}, gap = {:.3}, t = {:.3}s)",
            ctx.objective(),
            ctx.mip_node_count(),
            ctx.mip_gap(),
            ctx.running_time(),
        );
        CallbackAction::Continue
    })
    .unwrap();
    h.start_callback(CallbackType::MipImprovingSolution).unwrap();

    assert_eq!(h.run().unwrap(), ModelStatus::Optimal);
    println!("optimal value: {:.1}", h.objective_value());
}
