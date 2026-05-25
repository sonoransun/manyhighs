use highs::{Highs, ModelStatus, VarType};

/// max x + y  s.t.  x + 2y <= 4,  3x + 2y <= 6,  x,y integer in [0,10].
/// LP relaxation optimum is 2.5 at (1, 1.5); the integer optimum is 2.
#[test]
fn solves_mip_via_builder() {
    let mut h = Highs::new().silenced();
    let x = h.add_integer(0.0, 10.0).unwrap();
    let y = h.add_integer(0.0, 10.0).unwrap();
    h.add_constr((x + 2.0 * y).le(4.0)).unwrap();
    h.add_constr((3.0 * x + 2.0 * y).le(6.0)).unwrap();
    h.maximize(x + y).unwrap();

    assert_eq!(h.run().unwrap(), ModelStatus::Optimal);
    assert!((h.objective_value() - 2.0).abs() < 1e-6);

    let sol = h.solution().unwrap();
    for (i, &v) in sol.col_value.iter().enumerate() {
        assert!((v - v.round()).abs() < 1e-6, "col {i} = {v} not integral");
    }
    // node count info is queryable for a MIP
    assert!(h.info_i64("mip_node_count").unwrap() >= 0);
}

/// Same model loaded through the low-level `pass_mip` path.
#[test]
fn solves_mip_via_pass_mip() {
    use highs::{LpProblem, MatrixFormat, MipProblem, ObjSense, Sparse};
    let lp = LpProblem {
        sense: ObjSense::Maximize,
        offset: 0.0,
        col_cost: vec![1.0, 1.0],
        col_lower: vec![0.0, 0.0],
        col_upper: vec![10.0, 10.0],
        row_lower: vec![-1.0e30, -1.0e30],
        row_upper: vec![4.0, 6.0],
        matrix: Sparse {
            format: MatrixFormat::RowWise,
            start: vec![0, 2],
            index: vec![0, 1, 0, 1],
            value: vec![1.0, 2.0, 3.0, 2.0],
        },
    };
    let mip = MipProblem {
        lp,
        integrality: vec![VarType::Integer, VarType::Integer],
    };
    let mut h = Highs::new().silenced();
    h.pass_mip(&mip).unwrap();
    assert_eq!(h.run().unwrap(), ModelStatus::Optimal);
    assert!((h.objective_value() - 2.0).abs() < 1e-6);
}
