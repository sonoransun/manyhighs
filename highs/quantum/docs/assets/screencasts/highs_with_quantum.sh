#!/usr/bin/env bash
# Drive a HiGHS solve with the quantum heuristic enabled, then surface the
# key log lines (option-set lines, every Quantum log, status, bounds).
set -e
HIGHS="${HIGHS_BIN:-/root/cdev/manyhighs/build_on/bin/highs}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MPS="${HERE}/../../../../../../tmp/maxcut5.mps"
OPTS="/tmp/highs_screencast.opts"

if [[ ! -f "${MPS}" ]]; then
  MPS="/tmp/maxcut5.mps"
fi

cat > "${OPTS}" <<EOF
mip_quantum_heuristic = classical
quantum_python_executable = /root/cdev/manyhighs/highs/quantum/python/.venv/bin/python
quantum_time_limit = 1.0
EOF

echo "# HiGHS solve with the quantum heuristic enabled"
echo
echo '$ cat q.txt'
cat "${OPTS}"
echo
echo "$ highs maxcut5.mps --options_file q.txt"
"${HIGHS}" "${MPS}" --options_file "${OPTS}" 2>&1 | \
  grep -E "Set option mip_quantum|Quantum heuristic|^  Status|Primal bound|Dual bound|Q =>"
