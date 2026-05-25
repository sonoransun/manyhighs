use highs::{
    solve_lp, Highs, LpProblem, MatrixFormat, ModelStatus, ObjSense, OptionType, Sparse, VarType,
};

fn sample_lp() -> LpProblem {
    LpProblem {
        sense: ObjSense::Maximize,
        offset: 0.0,
        col_cost: vec![2.0, 3.0],
        col_lower: vec![0.0, 0.0],
        col_upper: vec![1.0e30, 1.0e30],
        row_lower: vec![-1.0e30, -1.0e30],
        row_upper: vec![4.0, 6.0],
        matrix: Sparse {
            format: MatrixFormat::RowWise,
            start: vec![0, 2],
            index: vec![0, 1, 0, 1],
            value: vec![1.0, 1.0, 1.0, 3.0],
        },
    }
}

#[test]
fn one_shot_solve_lp() {
    let out = solve_lp(&sample_lp()).unwrap();
    assert_eq!(out.status, ModelStatus::Optimal);
    assert!((out.objective - 9.0).abs() < 1e-7);
    assert_eq!(out.solution.col_value.len(), 2);
}

#[test]
fn write_then_read_model_roundtrips() {
    let dir = std::env::temp_dir();
    let path = dir.join(format!("highs_rs_test_{}.mps", std::process::id()));
    let path = path.to_str().unwrap();

    let mut h = Highs::new().silenced();
    h.pass_lp(&sample_lp()).unwrap();
    h.write_model(path).unwrap();

    let mut h2 = Highs::new().silenced();
    h2.read_model(path).unwrap();
    assert_eq!(h2.num_col(), 2);
    assert_eq!(h2.num_row(), 2);
    assert_eq!(h2.run().unwrap(), ModelStatus::Optimal);
    assert!((h2.objective_value() - 9.0).abs() < 1e-7);

    let _ = std::fs::remove_file(path);
}

#[test]
fn introspection() {
    let mut h = Highs::new().silenced();
    let x = h.add_var(0.0, 10.0).unwrap();
    let _y = h.add_integer(0.0, 5.0).unwrap();
    h.maximize(x).unwrap();

    assert_eq!(h.objective_sense(), ObjSense::Maximize);
    assert_eq!(h.col_integrality(x).unwrap(), VarType::Continuous);
    assert_eq!(
        h.col_integrality(highs::Col(1)).unwrap(),
        VarType::Integer
    );
    assert_eq!(h.option_type("threads").unwrap(), OptionType::Int);
    assert_eq!(h.option_type("time_limit").unwrap(), OptionType::Double);
    assert_eq!(h.option_type("solver").unwrap(), OptionType::String);
    assert_eq!(h.option_type("output_flag").unwrap(), OptionType::Bool);
}
