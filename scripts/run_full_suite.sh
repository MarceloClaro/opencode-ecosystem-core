#!/usr/bin/env bash
# =============================================================================
# run_full_suite.sh — Executa suite completa de testes e qualidade
# =============================================================================
# Uso: ./scripts/run_full_suite.sh [--ci]
#
# Flags:
#   --ci     Modo CI: para no primeiro erro (set -e)
#   --json   Gera relatorio JSON
# =============================================================================

set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
cd "$REPO_DIR" || exit 1

CI_MODE=false
JSON_FLAG=""

for arg in "$@"; do
    case "$arg" in
        --ci) CI_MODE=true ;;
        --json) JSON_FLAG="--json" ;;
    esac
done

if $CI_MODE; then
    set -e
    echo "[CI] MODE: parando no primeiro erro"
fi

echo "========================================"
echo "  FULL TEST SUITE - OpenCode Ecosystem"
echo "========================================"
echo "  Started: $(date)"
echo "  Python:  $(python3 --version)"
echo "  Dir:     $REPO_DIR"
echo "========================================"
echo ""

# ---- 1. Quality Report ----
echo "[Step 1] Quality Report"
python3 scripts/quality_report.py $JSON_FLAG
echo ""

# ---- 2. Full Test Suite ----
echo "[Step 2] Full Test Suite"
python3 -m pytest tests/ -v --tb=short --timeout=120 2>&1 | tail -20
echo ""

# ---- 3. Quality Gate ----
echo "[Step 3] Quality Gate"
python3 scripts/check_coverage.py --threshold 80 --verbose
GATE_EXIT=$?
echo ""

# ---- 4. Summary ----
echo "========================================"
if [ $GATE_EXIT -eq 0 ]; then
    echo "  [PASS] ALL CHECKS PASSED"
else
    echo "  [FAIL] GATE FAILED (exit code: $GATE_EXIT)"
fi
echo "  Finished: $(date)"
echo "========================================"

exit $GATE_EXIT
