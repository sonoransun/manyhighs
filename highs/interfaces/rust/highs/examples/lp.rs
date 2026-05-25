//! A tiny LP, built with the expression DSL.
//!
//!     cargo run --example lp --no-default-features

use highs::{Highs, ModelStatus};

fn main() {
    // max 2x + 3y  s.t.  x + y <= 4,  x + 3y <= 6,  x,y >= 0
    let mut h = Highs::new().silenced();
    let x = h.add_var(0.0, f64::INFINITY).unwrap();
    let y = h.add_var(0.0, f64::INFINITY).unwrap();
    h.add_constr((x + y).le(4.0)).unwrap();
    h.add_constr((x + 3.0 * y).le(6.0)).unwrap();
    h.maximize(2.0 * x + 3.0 * y).unwrap();

    assert_eq!(h.run().unwrap(), ModelStatus::Optimal);
    let sol = h.solution().unwrap();
    println!("status   : {:?}", h.model_status());
    println!("objective: {:.3}", h.objective_value());
    println!("x = {:.3}, y = {:.3}", sol.col_value[0], sol.col_value[1]);
}
