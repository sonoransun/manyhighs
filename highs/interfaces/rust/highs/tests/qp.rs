use highs::{Highs, HessianFormat, LpProblem, MatrixFormat, ModelStatus, ObjSense, QpProblem, Sparse};

/// min (x-1)² + (y-2)²  over x,y in [0,10].
/// As ½xᵀQx + cᵀx + k: Q = diag(2,2), c = (-2,-4), k = 5. Optimum (1,2), obj 0.
#[test]
fn solves_qp() {
    let lp = LpProblem {
        sense: ObjSense::Minimize,
        offset: 5.0,
        col_cost: vec![-2.0, -4.0],
        col_lower: vec![0.0, 0.0],
        col_upper: vec![10.0, 10.0],
        row_lower: vec![],
        row_upper: vec![],
        matrix: Sparse {
            format: MatrixFormat::ColWise,
            start: vec![0, 0], // two columns, no constraint nonzeros
            index: vec![],
            value: vec![],
        },
    };
    let qp = QpProblem {
        lp,
        hessian_format: HessianFormat::Triangular,
        hessian: Sparse {
            format: MatrixFormat::ColWise, // unused for the Hessian, but keep consistent
            start: vec![0, 1],
            index: vec![0, 1],
            value: vec![2.0, 2.0],
        },
    };

    let mut h = Highs::new().silenced();
    h.pass_qp(&qp).unwrap();
    assert_eq!(h.run().unwrap(), ModelStatus::Optimal);
    assert!(h.objective_value().abs() < 1e-5, "obj = {}", h.objective_value());

    let sol = h.solution().unwrap();
    assert!((sol.col_value[0] - 1.0).abs() < 1e-4, "x = {}", sol.col_value[0]);
    assert!((sol.col_value[1] - 2.0).abs() < 1e-4, "y = {}", sol.col_value[1]);
}
