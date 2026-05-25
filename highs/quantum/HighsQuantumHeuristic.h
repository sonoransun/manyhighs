/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
/*                                                                       */
/*    This file is part of the HiGHS linear optimization suite           */
/*                                                                       */
/*    Available as open-source under the MIT License                     */
/*                                                                       */
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
#ifndef QUANTUM_HIGHS_QUANTUM_HEURISTIC_H_
#define QUANTUM_HIGHS_QUANTUM_HEURISTIC_H_

#ifdef QUANTUM

#include <atomic>
#include <memory>
#include <string>
#include <thread>
#include <vector>

#include "quantum/HighsQubo.h"
#include "util/HighsInt.h"

class HighsLogOptions;
class HighsMipSolverData;

namespace highs_quantum {

struct InvocationConfig {
  std::string python_executable;
  std::string backend;
  double time_limit_seconds = 30.0;
  std::string extra_args;
  HighsInt max_vars = 2048;
};

// One in-flight subprocess call. Lives in HighsQuantumHeuristic::pending_.
// The worker thread writes `result` and sets `done` on completion; the
// search thread polls `done` from harvest().
struct PendingCall {
  std::atomic<bool> done{false};
  std::atomic<bool> joined{false};
  std::string in_path;
  std::string out_path;
  std::string backend;
  QuboSubproblem qubo;       // kept for the lift-onto-seed step in parseResult
  QuboResult result;
  std::thread worker;
};

// Owns in-flight quantum subprocess calls. One instance per HiGHS solve;
// the destructor joins every still-running worker so threads never outlive
// the parent.
class HighsQuantumHeuristic {
 public:
  HighsQuantumHeuristic() = default;
  HighsQuantumHeuristic(const HighsQuantumHeuristic&) = delete;
  HighsQuantumHeuristic& operator=(const HighsQuantumHeuristic&) = delete;
  ~HighsQuantumHeuristic();

  // Fire-and-forget: serialize `qubo`, spawn a worker thread that runs the
  // Python subprocess and stores the parsed result back on the PendingCall.
  // Returns false if the subproblem couldn't be written to disk.
  bool dispatch(QuboSubproblem qubo, const InvocationConfig& cfg,
                const HighsLogOptions& log_options);

  // Non-blocking check for completed calls. For each done worker: parse the
  // result, call mipdata.trySolution(), log, then drop the PendingCall.
  // Returns the count of accepted incumbent solutions.
  int harvest(HighsMipSolverData& mipdata);

  // True if at least one PendingCall is still in flight.
  bool hasPending() const;

  // How many dispatches the search has triggered (for telemetry / node-freq
  // gating in HighsMipSolver.cpp).
  HighsInt totalDispatches() const { return total_dispatches_; }
  HighsInt totalAccepted() const { return total_accepted_; }

 private:
  std::vector<std::unique_ptr<PendingCall>> pending_;
  HighsInt total_dispatches_ = 0;
  HighsInt total_accepted_ = 0;
};

}  // namespace highs_quantum

#endif  // QUANTUM
#endif  // QUANTUM_HIGHS_QUANTUM_HEURISTIC_H_
