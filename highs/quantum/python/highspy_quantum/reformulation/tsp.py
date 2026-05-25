"""TSP QUBO formulation — stub.

The Lucas-2014 formulation packs a TSP instance into n² binary variables
plus O(n) penalty terms. Implementation is substantial (~150 lines) and
needs care around subtour-elimination constraints. For Sprint 4 we ship
the detector + a stub builder that falls through to the generic penalty
path. Real implementation lives in a follow-up.
"""
from __future__ import annotations

from ..model import Bqm, MipSubproblem, build_bqm_from_subproblem


def build(sub: MipSubproblem) -> Bqm:
    return build_bqm_from_subproblem(sub)
