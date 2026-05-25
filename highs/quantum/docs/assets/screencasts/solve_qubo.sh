#!/usr/bin/env bash
# Solve the sample QUBO with two backends and a verbose result.
set -e
HQ="/root/cdev/manyhighs/highs/quantum/python/.venv/bin/highs-quantum"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "# Solve a 6-var QUBO with two backends"
sleep 1
echo
echo "$ highs-quantum solve sample_qubo.json --backend classical --time-limit 2"
sleep 1
"${HQ}" solve "${HERE}/sample_qubo.json" --backend classical --time-limit 2
sleep 1
echo
echo "$ highs-quantum solve sample_qubo.json --backend exact"
sleep 1
"${HQ}" solve "${HERE}/sample_qubo.json" --backend exact
sleep 1
