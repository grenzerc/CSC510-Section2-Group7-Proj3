#!/usr/bin/env bash
# Runs every Project 1 pytest file in sequence and writes one combined log.
#
# This is the script to record for the demo video -- it prints straight to the
# terminal as well as to test-output/, so the marker sees real output scroll by
# rather than a screenshot.
#
#   proj1/tests/run_all_tests.sh
#
# Needs the backend on :8080 (and the frontend if you are demoing the UI too).
set -u

# Override if python3 is not the interpreter you want:
#   PYTHON=/usr/bin/python3 proj1/tests/<script>.sh
PYTHON="${PYTHON:-python3}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ1_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="$PROJ1_DIR/test-output"
TIMESTAMP="$(date +"%Y%m%d-%H%M%S")"
OUTPUT_FILE="$OUTPUT_DIR/all-tests-$TIMESTAMP.txt"

mkdir -p "$OUTPUT_DIR"

{
  echo "======================================================================"
  echo " FoodSeer -- Project 1a full test run"
  echo " Started: $(date)"
  echo " API_BASE_URL: ${API_BASE_URL:-http://localhost:8080}"
  echo "======================================================================"
  echo ""
} | tee "$OUTPUT_FILE"

FAILED_FILES=()

for test_file in "$SCRIPT_DIR"/test_*_pytest.py; do
  name="$(basename "$test_file")"

  {
    echo ""
    echo "----------------------------------------------------------------------"
    echo " $name"
    echo "----------------------------------------------------------------------"
  } | tee -a "$OUTPUT_FILE"

  "$PYTHON" -m pytest -vv "$test_file" 2>&1 | tee -a "$OUTPUT_FILE"

  if [[ "${PIPESTATUS[0]}" -ne 0 ]]; then
    FAILED_FILES+=("$name")
  fi
done

{
  echo ""
  echo "======================================================================"
  echo " Finished: $(date)"
  if [[ "${#FAILED_FILES[@]}" -eq 0 ]]; then
    echo " Every file passed."
  else
    echo " Files with failing tests (${#FAILED_FILES[@]}):"
    for name in "${FAILED_FILES[@]}"; do
      echo "   - $name"
    done
    echo ""
    echo " Failures are expected here -- see proj1/test-plan.md for which ones"
    echo " are real defects in FoodSeer rather than problems with the tests."
  fi
  echo " Full log: $OUTPUT_FILE"
  echo "======================================================================"
} | tee -a "$OUTPUT_FILE"

exit 0
