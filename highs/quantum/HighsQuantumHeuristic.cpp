/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
/*                                                                       */
/*    This file is part of the HiGHS linear optimization suite           */
/*                                                                       */
/*    Available as open-source under the MIT License                     */
/*                                                                       */
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
#ifdef QUANTUM

#include "quantum/HighsQuantumHeuristic.h"

#include <unistd.h>

#include <algorithm>
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <sstream>
#include <string>
#include <utility>

#include "io/HighsIO.h"
#include "lp_data/HConst.h"
#include "lp_data/HighsLp.h"
#include "lp_data/HighsOptions.h"
#include "mip/HighsMipSolver.h"
#include "mip/HighsMipSolverData.h"
#include "quantum/HighsQuantumOptions.h"

namespace highs_quantum {

namespace {

std::string defaultTmpDir() {
  const char* override_dir = std::getenv(kTmpDirEnv);
  if (override_dir && *override_dir) return override_dir;
  const char* tmp = std::getenv("TMPDIR");
  if (tmp && *tmp) return tmp;
  return "/tmp";
}

std::string shellQuote(const std::string& s) {
  std::string out;
  out.reserve(s.size() + 2);
  out.push_back('\'');
  for (char c : s) {
    if (c == '\'') {
      out += "'\\''";
    } else {
      out.push_back(c);
    }
  }
  out.push_back('\'');
  return out;
}

bool writeFile(const std::string& path, const std::string& contents) {
  std::ofstream f(path);
  if (!f) return false;
  f << contents;
  return static_cast<bool>(f);
}

bool readFile(const std::string& path, std::string& out) {
  std::ifstream f(path);
  if (!f) return false;
  std::stringstream ss;
  ss << f.rdbuf();
  out = ss.str();
  return true;
}

// Worker body. Runs in its own std::thread; must not touch HiGHS state.
// Communicates back via the atomic flag on PendingCall.
void workerBody(PendingCall* call, InvocationConfig cfg) {
  char timeout_buf[32];
  std::snprintf(timeout_buf, sizeof(timeout_buf), "%g",
                cfg.time_limit_seconds);

  std::string cmd;
  cmd += shellQuote(cfg.python_executable);
  cmd += " -m ";
  cmd += kPythonModule;
  cmd += " solve --backend ";
  cmd += shellQuote(cfg.backend);
  cmd += " --in ";
  cmd += shellQuote(call->in_path);
  cmd += " --out ";
  cmd += shellQuote(call->out_path);
  cmd += " --timeout ";
  cmd += timeout_buf;
  if (!cfg.extra_args.empty()) {
    cmd += " ";
    cmd += cfg.extra_args;
  }

  int rc = std::system(cmd.c_str());
  if (rc != 0) {
    char err[128];
    std::snprintf(err, sizeof(err),
                  "subprocess exited with status %d (backend=%s)", rc,
                  cfg.backend.c_str());
    call->result.ok = false;
    call->result.error = err;
    call->result.backend = cfg.backend;
  } else {
    std::string out_json;
    if (!readFile(call->out_path, out_json)) {
      call->result.ok = false;
      call->result.error = "failed to read result JSON";
      call->result.backend = cfg.backend;
    } else {
      call->result = parseResult(out_json, call->qubo);
    }
  }

  std::remove(call->in_path.c_str());
  std::remove(call->out_path.c_str());

  // Publish completion last so harvest sees a fully-populated result.
  call->done.store(true, std::memory_order_release);
}

}  // namespace

HighsQuantumHeuristic::~HighsQuantumHeuristic() {
  // Block until every worker thread has terminated. Workers are I/O-bound on
  // the subprocess; the Python side respects --timeout so this is bounded.
  for (auto& call : pending_) {
    if (call && call->worker.joinable()) {
      call->worker.join();
    }
  }
}

bool HighsQuantumHeuristic::dispatch(QuboSubproblem qubo,
                                     const InvocationConfig& cfg,
                                     const HighsLogOptions& log_options) {
  ++total_dispatches_;

  const std::string tmpdir = defaultTmpDir();
  static std::atomic<long long> seq{0};
  long long n = ++seq;
  char base[256];
  std::snprintf(base, sizeof(base), "%s/highs_qubo_%lld_%lld", tmpdir.c_str(),
                static_cast<long long>(getpid()), n);

  std::unique_ptr<PendingCall> call(new PendingCall());
  call->in_path = std::string(base) + ".in.json";
  call->out_path = std::string(base) + ".out.json";
  call->backend = cfg.backend;
  call->qubo = std::move(qubo);

  std::string in_json = toJson(call->qubo, kProtocolVersion);
  if (!writeFile(call->in_path, in_json)) {
    highsLogUser(log_options, HighsLogType::kWarning,
                 "Quantum heuristic: failed to write %s\n",
                 call->in_path.c_str());
    return false;
  }

  highsLogUser(log_options, HighsLogType::kVerbose,
               "Quantum heuristic: dispatching %s (vars=%d, rows=%d, "
               "in_flight=%d)\n",
               cfg.backend.c_str(), int(call->qubo.num_vars),
               int(call->qubo.num_rows), int(pending_.size() + 1));

  // Capture raw pointer + a copy of cfg. The PendingCall outlives the
  // thread because the heuristic owns it and joins on destruction.
  PendingCall* raw = call.get();
  InvocationConfig cfg_copy = cfg;
  call->worker = std::thread([raw, cfg_copy]() { workerBody(raw, cfg_copy); });
  pending_.push_back(std::move(call));
  return true;
}

int HighsQuantumHeuristic::harvest(HighsMipSolverData& mipdata) {
  const HighsLogOptions& log_options = mipdata.mipsolver.options_mip_->log_options;
  int accepted = 0;
  for (auto& call : pending_) {
    if (!call) continue;
    if (!call->done.load(std::memory_order_acquire)) continue;
    if (call->joined.exchange(true)) continue;
    if (call->worker.joinable()) call->worker.join();

    const QuboResult& r = call->result;
    if (r.ok && !r.assignment.empty()) {
      const bool ok = mipdata.trySolution(r.assignment, kSolutionSourceQuantum);
      highsLogUser(log_options, HighsLogType::kInfo,
                   "Quantum heuristic: backend=%s objective=%.6g "
                   "wall_time=%.3gs accepted=%s\n",
                   r.backend.c_str(), r.objective, r.wall_time,
                   ok ? "yes" : "no");
      if (ok) {
        ++accepted;
        ++total_accepted_;
      }
    } else if (!r.error.empty()) {
      highsLogUser(log_options, HighsLogType::kWarning,
                   "Quantum heuristic: backend=%s no incumbent (%s)\n",
                   r.backend.c_str(), r.error.c_str());
    }
  }
  // Drop completed entries so we don't grow unboundedly.
  pending_.erase(
      std::remove_if(pending_.begin(), pending_.end(),
                     [](const std::unique_ptr<PendingCall>& c) {
                       return c && c->joined.load();
                     }),
      pending_.end());
  return accepted;
}

bool HighsQuantumHeuristic::hasPending() const {
  for (const auto& call : pending_) {
    if (call && !call->done.load()) return true;
  }
  return false;
}

}  // namespace highs_quantum

// Implementation of the HighsMipSolverData hook. Now async: dispatch a fresh
// subproblem, harvest any previously-completed ones, and return. The actual
// trySolution() happens inside harvest().
HighsModelStatus HighsMipSolverData::quantumHeuristic() {
  const HighsOptions* opts = mipsolver.options_mip_;
  const HighsLogOptions& log_options = opts->log_options;

  if (opts->mip_quantum_heuristic.empty() ||
      opts->mip_quantum_heuristic == "off") {
    return HighsModelStatus::kNotset;
  }

  if (!quantum_heuristic_) {
    quantum_heuristic_.reset(new highs_quantum::HighsQuantumHeuristic());
  }

  // Harvest first — pick up anything ready before we dispatch the next one.
  quantum_heuristic_->harvest(*this);

  highs_quantum::InvocationConfig cfg;
  cfg.python_executable = opts->quantum_python_executable.empty()
                              ? "python3"
                              : opts->quantum_python_executable;
  cfg.backend = opts->mip_quantum_heuristic;
  cfg.time_limit_seconds =
      opts->quantum_time_limit > 0 ? opts->quantum_time_limit : 30.0;
  cfg.extra_args = opts->quantum_extra_args;

  highs_quantum::QuboReason reason;
  highs_quantum::QuboSubproblem qubo;
  const std::string& mode = opts->mip_quantum_heuristic_mode;
  if (mode == "rins" && !incumbent.empty()) {
    // RINS-style extraction: fix vars matching their LP value to the incumbent,
    // ship just the free binary subproblem to the backend.
    qubo = highs_quantum::extractRinsNeighborhood(
        *this, cfg.max_vars, opts->mip_feasibility_tolerance, reason);
    // Fall back to whole-model extraction if RINS isn't applicable (no
    // incumbent yet, no LP relaxation, all variables matched, etc.).
    if (reason != highs_quantum::QuboReason::kOk) {
      qubo = highs_quantum::extractFromMip(*this, cfg.max_vars, reason);
    }
  } else {
    qubo = highs_quantum::extractFromMip(*this, cfg.max_vars, reason);
  }
  if (reason != highs_quantum::QuboReason::kOk) {
    const char* why = "unknown";
    switch (reason) {
      case highs_quantum::QuboReason::kModelHasContinuous:
        why = "model has continuous variables";
        break;
      case highs_quantum::QuboReason::kModelHasGeneralInt:
        why = "model has non-binary integer variables";
        break;
      case highs_quantum::QuboReason::kModelTooLarge:
        why = "model exceeds quantum heuristic var budget";
        break;
      case highs_quantum::QuboReason::kModelEmpty:
        why = "model is empty";
        break;
      default:
        break;
    }
    highsLogUser(log_options, HighsLogType::kInfo,
                 "Quantum heuristic: skipped (%s)\n", why);
    return HighsModelStatus::kNotset;
  }

  (void)quantum_heuristic_->dispatch(std::move(qubo), cfg, log_options);
  return HighsModelStatus::kNotset;
}

// Harvest-only path. Called from the dive loop after each potential heuristic
// fire; collects any results that arrived between dispatches.
void HighsMipSolverData::harvestQuantumResults() {
  if (quantum_heuristic_) {
    (void)quantum_heuristic_->harvest(*this);
  }
}

#endif  // QUANTUM
