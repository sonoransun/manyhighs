use highs::{Highs, LpProblem, MatrixFormat, ModelStatus, ObjSense, Sparse};

/// max 2x + 3y  s.t.  x + y <= 4,  x + 3y <= 6,  x,y >= 0.
/// Optimum at x=3, y=1 with objective 9.
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
            // row 0: x + y ; row 1: x + 3y
            start: vec![0, 2],
            index: vec![0, 1, 0, 1],
            value: vec![1.0, 1.0, 1.0, 3.0],
        },
    }
}

#[test]
fn solves_lp_to_optimum() {
    let mut h = Highs::new().silenced();
    h.pass_lp(&sample_lp()).unwrap();
    assert_eq!(h.run().unwrap(), ModelStatus::Optimal);
    assert!((h.objective_value() - 9.0).abs() < 1e-7);

    let sol = h.solution().unwrap();
    assert!((sol.col_value[0] - 3.0).abs() < 1e-6, "x = {}", sol.col_value[0]);
    assert!((sol.col_value[1] - 1.0).abs() < 1e-6, "y = {}", sol.col_value[1]);
    // both constraints binding -> row activities at their upper bounds
    assert!((sol.row_value[0] - 4.0).abs() < 1e-6);
    assert!((sol.row_value[1] - 6.0).abs() < 1e-6);
}

#[test]
fn detects_dimensions() {
    let h = Highs::new().silenced();
    assert_eq!(h.num_col(), 0);
    assert_eq!(h.num_row(), 0);
    let mut h = h;
    h.pass_lp(&sample_lp()).unwrap();
    assert_eq!(h.num_col(), 2);
    assert_eq!(h.num_row(), 2);
}

#[test]
fn options_roundtrip() {
    let mut h = Highs::new().silenced();
    h.set_threads(1).unwrap();
    assert_eq!(h.get_int_option("threads").unwrap(), 1);
    h.set_time_limit(12.5).unwrap();
    assert!((h.get_double_option("time_limit").unwrap() - 12.5).abs() < 1e-12);
    h.set_solver("simplex").unwrap();
    assert_eq!(h.get_string_option("solver").unwrap(), "simplex");
    assert!(!h.get_bool_option("output_flag").unwrap());
}

#[test]
fn reports_iteration_info() {
    let mut h = Highs::new().silenced();
    h.pass_lp(&sample_lp()).unwrap();
    h.run().unwrap();
    // simplex should take at least one iteration on this problem
    assert!(h.info_i32("simplex_iteration_count").unwrap() >= 0);
}

#[test]
fn dimension_mismatch_is_reported() {
    let mut lp = sample_lp();
    lp.col_lower.pop(); // now length 1, expected 2
    let mut h = Highs::new().silenced();
    let err = h.pass_lp(&lp).unwrap_err();
    matches!(err, highs::HighsError::DimensionMismatch { .. });
}
