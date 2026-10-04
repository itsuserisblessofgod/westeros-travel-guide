#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

status=0
out=$(python3 -m unittest discover -s tests -v 2>&1) || status=$?
echo "$out"

# unittest ends with "Ran N tests" and "OK" or "FAILED (failures=a, errors=b)"
total=$(echo "$out" | sed -n 's/^Ran \([0-9]*\) test.*/\1/p')
total=${total:-0}
failed=$(echo "$out" | sed -n 's/^FAILED (\(.*\))$/\1/p' | grep -oE '[0-9]+' | paste -sd+ - || true)
failed=$(( ${failed:-0} ))
echo "TESTS: $(( total - failed ))/${total}"
exit "$status"
