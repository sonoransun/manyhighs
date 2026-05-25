/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
/*                                                                       */
/*    This file is part of the HiGHS linear optimization suite           */
/*                                                                       */
/*    Available as open-source under the MIT License                     */
/*                                                                       */
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
#ifndef QUANTUM_HIGHS_QUBO_H_
#define QUANTUM_HIGHS_QUBO_H_

#ifdef QUANTUM

#include <string>
#include <vector>

#include "util/HighsInt.h"

class HighsMipSolverData;

namespace highs_quantum {

enum class QuboReason {
  kOk,
  kModelHasContinuous,   // continuous variables present; not QUBO-able
  kModelHasGeneralInt,   // integer vars with non-{0,1} bounds
  kModelTooLarge,        // exceeds the configured var-count budget
  kModelEmpty,
};

// What we ship to the Python side. This is the (presolved) MIP description
// stripped down to the binary subproblem the quantum backend will work on.
// Python is responsible for the actual QUBO reformulation (penalty method on
// the constraints) because the right penalty scheme depends on the backend.
//
// Variables here are renumbered [0, num_vars); `original_indices[i]` maps
// QUBO-var i back to the parent HighsLp column index. `seed_full_solution`
// is a full-dimensional primal seed (LP relaxation or current incumbent)
// that decode() overlays the returned assignment onto, so the result can be
// passed straight to HighsMipSolverData::trySolution().
struct QuboSubproblem {
  HighsInt num_vars = 0;
  HighsInt num_rows = 0;
  // +1 if the parent MIP is minimization, -1 if maximization. The Python
  // side always solves a minimization; C++ flips signs on decode if needed.
  double sense_multiplier = 1.0;
  // Constant added to the QUBO objective on the Python side (e.g. the LP's
  // offset_, plus any contribution from variables fixed during extraction).
  double constant_offset = 0.0;

  // Per-variable arrays (size = num_vars). Bounds are always 0/1 here — we
  // only emit binary vars — but we keep them explicit so the JSON schema
  // generalizes cleanly when Sprint 4 adds general-integer reformulation.
  std::vector<double> linear;       // objective coefficients
  std::vector<double> lower;        // always 0 for Sprint 0
  std::vector<double> upper;        // always 1 for Sprint 0
  std::vector<HighsInt> original_indices;

  // CSR-ish constraint matrix: row_start has size num_rows + 1.
  std::vector<HighsInt> row_start;
  std::vector<HighsInt> col_index;
  std::vector<double> coef_value;
  std::vector<double> row_lower;
  std::vector<double> row_upper;

  // Full-dimensional primal vector (size = parent_lp.num_col_) seeded from
  // the LP relaxation or the current incumbent. decode() overlays the QUBO
  // assignment onto this.
  std::vector<double> seed_full_solution;

  // Tag set by Python-side structure detectors and surfaced in logs.
  std::string structure_tag;
};

// Sprint-0 extraction. Returns an empty QuboSubproblem and sets `reason` if
// the model isn't suitable. Suitable means: every variable is binary
// (kInteger with bounds [0, 1]), and the variable count is at most max_vars.
// Constraints are forwarded as-is; the Python side handles penalty
// reformulation. Sprint 4 will widen this to RINS neighborhoods and to
// detection of structured problems.
QuboSubproblem extractFromMip(const HighsMipSolverData& mipdata,
                              HighsInt max_vars, QuboReason& reason);

// RINS-style extraction. Inspects the current LP relaxation against the
// incumbent solution: binary columns whose LP value is within
// `match_tolerance` of the incumbent are fixed at the incumbent's value; the
// remaining "free" binary columns form the QUBO subproblem.
//
// For each row, the fixed-column contributions are folded into adjusted
// row bounds, so the subproblem the Python backend sees is over the free
// columns only with corrected RHS. `seed_full_solution` is the incumbent
// so decode() lifts back to a complete primal vector.
//
// Returns an empty QuboSubproblem with reason set if:
// - no incumbent is available (kModelEmpty)
// - any non-binary integer variable exists (kModelHasGeneralInt)
// - any continuous variable exists (kModelHasContinuous)
// - the free-variable count exceeds max_vars (kModelTooLarge)
QuboSubproblem extractRinsNeighborhood(const HighsMipSolverData& mipdata,
                                       HighsInt max_vars,
                                       double match_tolerance,
                                       QuboReason& reason);

// Hand-written JSON emitter — pulling in a dependency just for this would be
// the biggest dep change in HiGHS in years. Schema is documented in
// highspy_quantum/protocol.py.
std::string toJson(const QuboSubproblem& qubo, int protocol_version);

struct QuboResult {
  bool ok = false;
  std::string backend;
  double objective = 0.0;       // QUBO objective on `assignment`
  double wall_time = 0.0;       // backend wall time, seconds
  std::vector<double> assignment;  // full-dimensional primal vector
  std::string error;            // populated when ok = false
};

// Parse the JSON written by the Python subprocess and lift the QUBO sample
// into a full-dimensional primal vector by overlaying `qubo.seed_full_solution`.
QuboResult parseResult(const std::string& json_text,
                       const QuboSubproblem& qubo);

}  // namespace highs_quantum

#endif  // QUANTUM
#endif  // QUANTUM_HIGHS_QUBO_H_
