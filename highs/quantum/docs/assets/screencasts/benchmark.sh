#!/usr/bin/env bash
# Tabulated comparison across local backends.
set -e
HQ="/root/cdev/manyhighs/highs/quantum/python/.venv/bin/highs-quantum"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "# Cross-backend benchmark on the sample QUBO"
sleep 1
echo
echo "$ highs-quantum benchmark sample_qubo.json --backends classical,exact --time-limit 1"
sleep 1
"${HQ}" benchmark "${HERE}/sample_qubo.json" --backends classical,exact --time-limit 1
sleep 1
