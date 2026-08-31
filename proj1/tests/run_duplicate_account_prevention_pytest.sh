#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ1_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="$PROJ1_DIR/test-output"
TIMESTAMP="$(date +"%Y%m%d-%H%M%S")"
OUTPUT_FILE="$OUTPUT_DIR/duplicate-account-prevention-pytest-$TIMESTAMP.txt"

mkdir -p "$OUTPUT_DIR"

{
  echo "Use Case #2 pytest run: Duplicate account prevention"
  echo "Started: $(date)"
  echo "API_BASE_URL: ${API_BASE_URL:-http://localhost:8080}"
  echo ""
} | tee "$OUTPUT_FILE"

python3 -m pytest -vv "$SCRIPT_DIR/test_duplicate_account_prevention_pytest.py" 2>&1 | tee -a "$OUTPUT_FILE"
PYTEST_STATUS="${PIPESTATUS[0]}"

{
  echo ""
  echo "Finished: $(date)"
  echo "Exit status: $PYTEST_STATUS"
  echo "Output file: $OUTPUT_FILE"
} | tee -a "$OUTPUT_FILE"

exit "$PYTEST_STATUS"

