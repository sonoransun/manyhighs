use highs::{qsum, Highs, LinearExpr, ModelStatus};

#[test]
fn expression_operators_and_qsum() {
    let mut h = Highs::new().silenced();
    let vars: Vec<_> = (0..3).map(|_| h.add_var(0.0, 1.0).unwrap()).collect();

    // sum of the three vars <= 2 via qsum
    h.add_constr(qsum(vars.iter().copied()).le(2.0)).unwrap();

    // objective: 3*v0 + 2*v1 + v2 + 0, built with mixed operators
    let obj = 3.0 * vars[0] + vars[1] * 2.0 + vars[2] + 0.0;
    h.maximize(obj).unwrap();

    assert_eq!(h.run().unwrap(), ModelStatus::Optimal);
    // pick v0=1, v1=1 (sum=2), v2=0 -> obj = 5
    assert!((h.objective_value() - 5.0).abs() < 1e-7);
}

#[test]
fn constant_folds_into_bounds() {
    // (x + 3) >= 5  is equivalent to  x >= 2
    let mut h = Highs::new().silenced();
    let x = h.add_var(0.0, 10.0).unwrap();
    let c: LinearExpr = x + 3.0;
    h.add_constr(c.ge(5.0)).unwrap();
    h.minimize(x).unwrap();
    assert_eq!(h.run().unwrap(), ModelStatus::Optimal);
    assert!((h.objective_value() - 2.0).abs() < 1e-7);
}

#[test]
fn subtraction_and_negation() {
    // maximize 10 - x  with x >= 3  -> x=3, obj=7
    let mut h = Highs::new().silenced();
    let x = h.add_var(0.0, 10.0).unwrap();
    h.add_constr(x.ge(3.0)).unwrap();
    h.maximize(10.0 - x).unwrap();
    assert_eq!(h.run().unwrap(), ModelStatus::Optimal);
    assert!((h.objective_value() - 7.0).abs() < 1e-7);
}
