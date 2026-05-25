//! A small 0/1 knapsack, built incrementally with binary variables.
//!
//!     cargo run --example mip --no-default-features

use highs::{qsum, Highs, ModelStatus};

fn main() {
    let value = [60.0, 100.0, 120.0, 80.0, 40.0];
    let weight = [10.0, 20.0, 30.0, 15.0, 5.0];
    let capacity = 50.0;

    let mut h = Highs::new().silenced();
    let items: Vec<_> = (0..value.len()).map(|_| h.add_binary().unwrap()).collect();

    let used = qsum(items.iter().zip(&weight).map(|(&x, &w)| w * x));
    h.add_constr(used.le(capacity)).unwrap();
    h.maximize(qsum(items.iter().zip(&value).map(|(&x, &v)| v * x)))
        .unwrap();

    assert_eq!(h.run().unwrap(), ModelStatus::Optimal);
    let sol = h.solution().unwrap();
    println!("best value: {:.0}", h.objective_value());
    print!("chosen items:");
    for (i, &v) in sol.col_value.iter().enumerate() {
        if v > 0.5 {
            print!(" {i}");
        }
    }
    println!();
}
