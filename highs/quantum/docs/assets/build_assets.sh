#!/usr/bin/env bash
# Regenerate every diagram, animation, and screencast under highs/quantum/docs/assets/.
# Pre-requisites: graphviz (dot), ffmpeg, the Python venv with matplotlib + termtosvg,
# and a built `highs` binary at build_on/bin/highs (for the screencasts).
#
# Idempotent: re-running produces byte-identical outputs given the same inputs.
# CI runs this and asserts `git diff --exit-code` to catch drift.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
HERE="${REPO_ROOT}/highs/quantum/docs/assets"
VENV_PY="${REPO_ROOT}/highs/quantum/python/.venv/bin/python"
VENV_BIN="${REPO_ROOT}/highs/quantum/python/.venv/bin"

cd "${HERE}"

echo "[1/3] Rendering DOT diagrams → SVG"
cd diagrams
for f in *.dot; do
  dot -Tsvg "$f" -o "${f%.dot}.svg"
  echo "  ok: $f → ${f%.dot}.svg"
done

echo "[2/3] Rendering matplotlib animations → GIF + MP4"
cd "${HERE}/animations"
for f in sa_bit_flipping.py qaoa_landscape.py rins_fixing.py penalty_escalation.py; do
  echo "  running: $f"
  "${VENV_PY}" "$f"
done

echo "[3/3] Capturing CLI screencast output → .txt (and optionally .svg)"
cd "${HERE}/screencasts"
export PATH="${VENV_BIN}:${PATH}"
export HIGHS_BIN="${HIGHS_BIN:-${REPO_ROOT}/build_on/bin/highs}"
if [[ ! -x "${HIGHS_BIN}" ]]; then
  echo "  WARNING: ${HIGHS_BIN} not built — skipping highs_with_quantum.sh."
  echo "           Build with: cmake -B build_on -DQUANTUM=ON && cmake --build build_on"
fi
# Plain-text captures: deterministic, CI-friendly, embeddable in Markdown.
for f in solve_qubo.sh benchmark.sh highs_with_quantum.sh; do
  if [[ ! -x "$f" ]]; then continue; fi
  if [[ "$f" == "highs_with_quantum.sh" && ! -x "${HIGHS_BIN}" ]]; then
    continue
  fi
  echo "  capturing: $f → ${f%.sh}.txt"
  bash "$f" > "${f%.sh}.txt" 2>&1
done

# Animated SVG via termtosvg requires a real TTY. Skip in non-interactive runs
# (CI / scripted invocations). To regenerate animated SVGs run interactively:
#   termtosvg --command "bash <script>.sh" --screen-geometry 100x24 <script>.svg
if [[ -t 0 && -t 1 ]] && command -v termtosvg >/dev/null; then
  for f in solve_qubo.sh benchmark.sh highs_with_quantum.sh; do
    if [[ ! -x "$f" ]]; then continue; fi
    echo "  recording animated SVG: $f → ${f%.sh}.svg"
    termtosvg --command "bash ${f}" --screen-geometry 100x24 "${f%.sh}.svg" || true
  done
else
  echo "  (skipping animated SVG: not running in an interactive TTY)"
fi

echo "All assets regenerated under ${HERE}"
