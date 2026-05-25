/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
/*                                                                       */
/*    This file is part of the HiGHS linear optimization suite           */
/*                                                                       */
/*    Available as open-source under the MIT License                     */
/*                                                                       */
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
#ifdef QUANTUM

#include "quantum/HighsQubo.h"

#include <cctype>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <sstream>
#include <string>

#include "lp_data/HConst.h"
#include "lp_data/HighsLp.h"
#include "mip/HighsMipSolver.h"
#include "mip/HighsMipSolverData.h"
#include "util/HighsSparseMatrix.h"

namespace highs_quantum {

namespace {

constexpr double kBoundEps = 1e-6;

bool isBinaryVariable(const HighsLp& lp, HighsInt col) {
  if (lp.integrality_[col] != HighsVarType::kInteger &&
      lp.integrality_[col] != HighsVarType::kImplicitInteger) {
    return false;
  }
  return std::fabs(lp.col_lower_[col]) < kBoundEps &&
         std::fabs(lp.col_upper_[col] - 1.0) < kBoundEps;
}

// Append a JSON-escaped string. Only handles ASCII + the escapes we emit;
// every string we serialize is a structure tag or an env-derived name.
void appendJsonString(std::string& out, const std::string& s) {
  out.push_back('"');
  for (char c : s) {
    switch (c) {
      case '"':  out += "\\\""; break;
      case '\\': out += "\\\\"; break;
      case '\n': out += "\\n";  break;
      case '\r': out += "\\r";  break;
      case '\t': out += "\\t";  break;
      default:
        if (static_cast<unsigned char>(c) < 0x20) {
          char buf[8];
          std::snprintf(buf, sizeof(buf), "\\u%04x", c);
          out += buf;
        } else {
          out.push_back(c);
        }
    }
  }
  out.push_back('"');
}

// Doubles are emitted with enough precision to round-trip. Infinity is
// rendered as a sentinel string (Python side decodes back to float('inf')).
void appendJsonNumber(std::string& out, double v) {
  if (!std::isfinite(v)) {
    if (std::isnan(v)) {
      out += "\"nan\"";
    } else if (v > 0) {
      out += "\"inf\"";
    } else {
      out += "\"-inf\"";
    }
    return;
  }
  char buf[32];
  std::snprintf(buf, sizeof(buf), "%.17g", v);
  out += buf;
}

template <typename Int>
void appendJsonInt(std::string& out, Int v) {
  char buf[32];
  std::snprintf(buf, sizeof(buf), "%lld", static_cast<long long>(v));
  out += buf;
}

void appendJsonDoubleArray(std::string& out, const std::vector<double>& v) {
  out.push_back('[');
  for (size_t i = 0; i < v.size(); ++i) {
    if (i) out.push_back(',');
    appendJsonNumber(out, v[i]);
  }
  out.push_back(']');
}

void appendJsonIntArray(std::string& out, const std::vector<HighsInt>& v) {
  out.push_back('[');
  for (size_t i = 0; i < v.size(); ++i) {
    if (i) out.push_back(',');
    appendJsonInt(out, v[i]);
  }
  out.push_back(']');
}

// Defensive bounds — the parser is only ever called on output we wrote
// ourselves, but a crashed/truncated Python subprocess could produce
// anything. These caps stop a pathological input from running unbounded.
constexpr size_t kMaxResultJsonBytes = 64 * 1024 * 1024;  // 64 MiB
constexpr size_t kMaxArrayLength = 16 * 1024 * 1024;      // 16M elements

// Minimal JSON value extractors. We only ever parse our own output, so the
// parser doesn't need to handle arbitrary input — just locate keys and read
// the next value. Returns the position after the parsed value (or npos on
// failure).

void skipWs(const std::string& s, size_t& i) {
  while (i < s.size() && std::isspace(static_cast<unsigned char>(s[i]))) ++i;
}

size_t findKey(const std::string& s, const char* key) {
  std::string needle = "\"";
  needle += key;
  needle += "\"";
  return s.find(needle);
}

// Position `i` to just after the `:` for the given key. Returns false if the
// key isn't present.
bool seekValue(const std::string& s, const char* key, size_t& i) {
  size_t k = findKey(s, key);
  if (k == std::string::npos) return false;
  i = k + 1;
  while (i < s.size() && s[i] != '"') ++i;  // closing quote of key
  if (i >= s.size()) return false;
  ++i;
  skipWs(s, i);
  if (i >= s.size() || s[i] != ':') return false;
  ++i;
  skipWs(s, i);
  return true;
}

bool parseBool(const std::string& s, size_t i, bool& out) {
  if (i + 4 <= s.size() && s.compare(i, 4, "true") == 0) {
    out = true;
    return true;
  }
  if (i + 5 <= s.size() && s.compare(i, 5, "false") == 0) {
    out = false;
    return true;
  }
  return false;
}

bool parseString(const std::string& s, size_t i, std::string& out) {
  if (i >= s.size() || s[i] != '"') return false;
  ++i;
  out.clear();
  while (i < s.size() && s[i] != '"') {
    if (s[i] == '\\' && i + 1 < s.size()) {
      char nx = s[i + 1];
      switch (nx) {
        case '"': out.push_back('"'); break;
        case '\\': out.push_back('\\'); break;
        case 'n': out.push_back('\n'); break;
        case 'r': out.push_back('\r'); break;
        case 't': out.push_back('\t'); break;
        default: out.push_back(nx); break;
      }
      i += 2;
    } else {
      out.push_back(s[i++]);
    }
  }
  return i < s.size();
}

bool parseNumber(const std::string& s, size_t i, double& out) {
  // Accept either a literal number or a sentinel string ("inf", "-inf", "nan").
  if (s[i] == '"') {
    std::string sv;
    if (!parseString(s, i, sv)) return false;
    if (sv == "inf") {
      out = kHighsInf;
      return true;
    }
    if (sv == "-inf") {
      out = -kHighsInf;
      return true;
    }
    if (sv == "nan") {
      out = std::nan("");
      return true;
    }
    return false;
  }
  char* end = nullptr;
  out = std::strtod(s.c_str() + i, &end);
  return end != s.c_str() + i;
}

bool parseDoubleArray(const std::string& s, size_t i,
                      std::vector<double>& out) {
  if (i >= s.size() || s[i] != '[') return false;
  ++i;
  skipWs(s, i);
  out.clear();
  if (i < s.size() && s[i] == ']') return true;
  while (i < s.size()) {
    if (out.size() >= kMaxArrayLength) return false;
    double v;
    if (!parseNumber(s, i, v)) return false;
    out.push_back(v);
    if (s[i] == '"') {
      while (i < s.size() && s[i] != '"') ++i;
      if (i < s.size()) ++i;
    } else {
      while (i < s.size() && (std::isdigit(static_cast<unsigned char>(s[i])) ||
                              s[i] == '.' || s[i] == 'e' || s[i] == 'E' ||
                              s[i] == '+' || s[i] == '-')) {
        ++i;
      }
    }
    skipWs(s, i);
    if (i < s.size() && s[i] == ',') {
      ++i;
      skipWs(s, i);
      continue;
    }
    if (i < s.size() && s[i] == ']') return true;
    return false;
  }
  return false;
}

}  // namespace

QuboSubproblem extractFromMip(const HighsMipSolverData& mipdata,
                              HighsInt max_vars, QuboReason& reason) {
  QuboSubproblem out;
  const HighsLp* model = mipdata.mipsolver.model_;
  if (model == nullptr || model->num_col_ == 0) {
    reason = QuboReason::kModelEmpty;
    return out;
  }

  // Sprint-0 gate: every variable must be binary.
  for (HighsInt c = 0; c < model->num_col_; ++c) {
    if (model->integrality_[c] == HighsVarType::kContinuous) {
      reason = QuboReason::kModelHasContinuous;
      return out;
    }
    if (!isBinaryVariable(*model, c)) {
      reason = QuboReason::kModelHasGeneralInt;
      return out;
    }
  }
  if (model->num_col_ > max_vars) {
    reason = QuboReason::kModelTooLarge;
    return out;
  }

  out.num_vars = model->num_col_;
  out.num_rows = model->num_row_;
  out.sense_multiplier = static_cast<double>(model->sense_);
  out.constant_offset = model->offset_;

  out.linear.assign(model->col_cost_.begin(), model->col_cost_.end());
  out.lower.assign(model->col_lower_.begin(), model->col_lower_.end());
  out.upper.assign(model->col_upper_.begin(), model->col_upper_.end());
  out.original_indices.resize(out.num_vars);
  for (HighsInt c = 0; c < out.num_vars; ++c) out.original_indices[c] = c;

  if (model->num_row_ > 0) {
    HighsSparseMatrix row_matrix;
    row_matrix.createRowwise(model->a_matrix_);
    out.row_start.assign(row_matrix.start_.begin(), row_matrix.start_.end());
    out.col_index.assign(row_matrix.index_.begin(), row_matrix.index_.end());
    out.coef_value.assign(row_matrix.value_.begin(), row_matrix.value_.end());
    out.row_lower.assign(model->row_lower_.begin(), model->row_lower_.end());
    out.row_upper.assign(model->row_upper_.begin(), model->row_upper_.end());
  } else {
    out.row_start = {0};
  }

  // Seed: prefer the current incumbent if any, otherwise zeros (a feasible
  // starting point for unconstrained binary problems).
  out.seed_full_solution.assign(out.num_vars, 0.0);
  if (!mipdata.incumbent.empty()) {
    for (HighsInt c = 0;
         c < out.num_vars && c < static_cast<HighsInt>(mipdata.incumbent.size());
         ++c) {
      double v = mipdata.incumbent[c];
      if (std::isfinite(v)) out.seed_full_solution[c] = v;
    }
  }

  reason = QuboReason::kOk;
  return out;
}

QuboSubproblem extractRinsNeighborhood(const HighsMipSolverData& mipdata,
                                       HighsInt max_vars,
                                       double match_tolerance,
                                       QuboReason& reason) {
  QuboSubproblem out;
  const HighsLp* model = mipdata.mipsolver.model_;
  if (model == nullptr || model->num_col_ == 0) {
    reason = QuboReason::kModelEmpty;
    return out;
  }
  if (mipdata.incumbent.empty()) {
    // No incumbent yet → no anchor for the neighborhood. Caller should fall
    // back to the whole-model extraction.
    reason = QuboReason::kModelEmpty;
    return out;
  }

  for (HighsInt c = 0; c < model->num_col_; ++c) {
    if (model->integrality_[c] == HighsVarType::kContinuous) {
      reason = QuboReason::kModelHasContinuous;
      return out;
    }
    if (!isBinaryVariable(*model, c)) {
      reason = QuboReason::kModelHasGeneralInt;
      return out;
    }
  }

  // Classify columns. A column is "fixed" if its LP relaxation value sits
  // within match_tolerance of the incumbent's integer value; otherwise it's
  // "free" and joins the subproblem.
  const std::vector<double>& lp_value =
      mipdata.lp.getLpSolver().getSolution().col_value;
  if (static_cast<HighsInt>(lp_value.size()) != model->num_col_) {
    // LP relaxation hasn't run yet — bail.
    reason = QuboReason::kModelEmpty;
    return out;
  }

  std::vector<HighsInt> free_cols;
  std::vector<double> fixed_value(model->num_col_, 0.0);
  std::vector<bool> is_fixed(model->num_col_, false);
  for (HighsInt c = 0; c < model->num_col_; ++c) {
    double inc = mipdata.incumbent[c];
    double lp = lp_value[c];
    if (std::isfinite(inc) && std::isfinite(lp) &&
        std::fabs(inc - lp) <= match_tolerance) {
      is_fixed[c] = true;
      fixed_value[c] = std::round(inc);
    } else {
      free_cols.push_back(c);
    }
  }

  if (free_cols.empty()) {
    // Nothing to optimize over.
    reason = QuboReason::kModelEmpty;
    return out;
  }
  if (static_cast<HighsInt>(free_cols.size()) > max_vars) {
    reason = QuboReason::kModelTooLarge;
    return out;
  }

  // Build the subproblem over the free columns. Variable indices are
  // renumbered [0, free_cols.size()); original_indices maps back.
  const HighsInt n = static_cast<HighsInt>(free_cols.size());
  std::vector<HighsInt> orig_to_local(model->num_col_, -1);
  for (HighsInt k = 0; k < n; ++k) orig_to_local[free_cols[k]] = k;

  out.num_vars = n;
  out.sense_multiplier = static_cast<double>(model->sense_);
  // Constant offset starts as the original LP offset plus the dot product
  // of fixed values against their objective coefficients.
  double constant = model->offset_;
  for (HighsInt c = 0; c < model->num_col_; ++c) {
    if (is_fixed[c]) constant += model->col_cost_[c] * fixed_value[c];
  }
  out.constant_offset = constant;

  out.linear.assign(n, 0.0);
  out.lower.assign(n, 0.0);
  out.upper.assign(n, 1.0);
  out.original_indices.assign(free_cols.begin(), free_cols.end());
  for (HighsInt k = 0; k < n; ++k) {
    out.linear[k] = model->col_cost_[free_cols[k]];
  }

  // Filter rows to the free-column subset; adjust RHS for fixed contributions.
  if (model->num_row_ > 0) {
    HighsSparseMatrix row_matrix;
    row_matrix.createRowwise(model->a_matrix_);

    std::vector<HighsInt> row_start;
    std::vector<HighsInt> col_index;
    std::vector<double> coef_value;
    std::vector<double> row_lower;
    std::vector<double> row_upper;
    row_start.push_back(0);

    for (HighsInt r = 0; r < model->num_row_; ++r) {
      HighsInt s = row_matrix.start_[r];
      HighsInt e = row_matrix.start_[r + 1];
      double fixed_contrib = 0.0;
      HighsInt local_nnz = 0;
      for (HighsInt k = s; k < e; ++k) {
        HighsInt col = row_matrix.index_[k];
        double val = row_matrix.value_[k];
        if (is_fixed[col]) {
          fixed_contrib += val * fixed_value[col];
        } else {
          col_index.push_back(orig_to_local[col]);
          coef_value.push_back(val);
          ++local_nnz;
        }
      }
      row_start.push_back(row_start.back() + local_nnz);
      double lo = model->row_lower_[r];
      double hi = model->row_upper_[r];
      row_lower.push_back(std::isfinite(lo) ? lo - fixed_contrib : lo);
      row_upper.push_back(std::isfinite(hi) ? hi - fixed_contrib : hi);
    }
    out.num_rows = model->num_row_;
    out.row_start = std::move(row_start);
    out.col_index = std::move(col_index);
    out.coef_value = std::move(coef_value);
    out.row_lower = std::move(row_lower);
    out.row_upper = std::move(row_upper);
  } else {
    out.num_rows = 0;
    out.row_start = {0};
  }

  // Seed = current incumbent. decode() overlays the QUBO assignment onto this.
  out.seed_full_solution.assign(model->num_col_, 0.0);
  for (HighsInt c = 0; c < model->num_col_; ++c) {
    if (std::isfinite(mipdata.incumbent[c])) {
      out.seed_full_solution[c] = mipdata.incumbent[c];
    }
  }

  out.structure_tag = "rins";
  reason = QuboReason::kOk;
  return out;
}

std::string toJson(const QuboSubproblem& qubo, int protocol_version) {
  std::string out;
  out.reserve(256 + 32 * qubo.num_vars + 16 * qubo.col_index.size());
  out += "{\"protocol_version\":";
  appendJsonInt(out, protocol_version);
  out += ",\"num_vars\":";
  appendJsonInt(out, qubo.num_vars);
  out += ",\"num_rows\":";
  appendJsonInt(out, qubo.num_rows);
  out += ",\"sense_multiplier\":";
  appendJsonNumber(out, qubo.sense_multiplier);
  out += ",\"constant_offset\":";
  appendJsonNumber(out, qubo.constant_offset);
  out += ",\"linear\":";
  appendJsonDoubleArray(out, qubo.linear);
  out += ",\"lower\":";
  appendJsonDoubleArray(out, qubo.lower);
  out += ",\"upper\":";
  appendJsonDoubleArray(out, qubo.upper);
  out += ",\"original_indices\":";
  appendJsonIntArray(out, qubo.original_indices);
  out += ",\"row_start\":";
  appendJsonIntArray(out, qubo.row_start);
  out += ",\"col_index\":";
  appendJsonIntArray(out, qubo.col_index);
  out += ",\"coef_value\":";
  appendJsonDoubleArray(out, qubo.coef_value);
  out += ",\"row_lower\":";
  appendJsonDoubleArray(out, qubo.row_lower);
  out += ",\"row_upper\":";
  appendJsonDoubleArray(out, qubo.row_upper);
  out += ",\"seed_full_solution\":";
  appendJsonDoubleArray(out, qubo.seed_full_solution);
  out += ",\"structure_tag\":";
  appendJsonString(out, qubo.structure_tag);
  out += "}";
  return out;
}

QuboResult parseResult(const std::string& json_text,
                       const QuboSubproblem& qubo) {
  QuboResult r;
  if (json_text.empty()) {
    r.error = "result JSON is empty";
    return r;
  }
  if (json_text.size() > kMaxResultJsonBytes) {
    r.error = "result JSON exceeds size cap";
    return r;
  }

  try {
    size_t pos = 0;

    bool ok = false;
    if (seekValue(json_text, "ok", pos) && parseBool(json_text, pos, ok)) {
      r.ok = ok;
    }

    std::string s;
    if (seekValue(json_text, "backend", pos) &&
        parseString(json_text, pos, s)) {
      r.backend = s;
    }
    if (seekValue(json_text, "error", pos) &&
        parseString(json_text, pos, s)) {
      r.error = s;
    }

    double d;
    if (seekValue(json_text, "objective", pos) &&
        parseNumber(json_text, pos, d)) {
      r.objective = d;
    }
    if (seekValue(json_text, "wall_time", pos) &&
        parseNumber(json_text, pos, d)) {
      r.wall_time = d;
    }

    std::vector<double> assignment_qubo;
    if (seekValue(json_text, "assignment", pos)) {
      parseDoubleArray(json_text, pos, assignment_qubo);
    }

    if (!r.ok || assignment_qubo.empty()) return r;

    r.assignment = qubo.seed_full_solution;
    for (HighsInt i = 0;
         i < static_cast<HighsInt>(assignment_qubo.size()) &&
         i < static_cast<HighsInt>(qubo.original_indices.size());
         ++i) {
      HighsInt orig = qubo.original_indices[i];
      if (orig >= 0 && orig < static_cast<HighsInt>(r.assignment.size())) {
        r.assignment[orig] = assignment_qubo[i];
      }
    }
  } catch (const std::exception& e) {
    r.ok = false;
    r.error = std::string("parser exception: ") + e.what();
    r.assignment.clear();
  } catch (...) {
    r.ok = false;
    r.error = "parser exception: unknown";
    r.assignment.clear();
  }
  return r;
}

}  // namespace highs_quantum

#endif  // QUANTUM
