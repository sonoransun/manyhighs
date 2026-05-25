"""Per-structure specialized BQM builders.

Each module exposes ``build(sub) -> Bqm`` that bypasses the generic penalty
method in ``model.build_bqm_from_subproblem``. The specialized formulations
are well-known compact QUBOs (Glover/Kochenberger, Lucas 2014 surveys); they
avoid the penalty-weight tuning failure mode that plagues the generic path.
"""
