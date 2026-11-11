#!/usr/bin/env bash
# R1151 — gate local equivalente ao CI para a branch de trabalho.
# Uso: bash scripts/local_ci.sh [--lean]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PYTHON="${PYTHON:-python3}"
LEAN=0
for arg in "$@"; do
  case "$arg" in
    --lean) LEAN=1 ;;
    *) echo "argumento desconhecido: $arg" >&2; exit 2 ;;
  esac
done

mkdir -p /tmp/opencode

echo "[1/6] Camadas R1148 + auditoria R1150"
"$PYTHON" -m pytest \
  tests/test_r1148_ema.py \
  tests/test_r1148_n_of_1.py \
  tests/test_r1148_claims_graph.py \
  tests/test_r1148_trust_warrant.py \
  tests/test_r1148_runtime_contract.py \
  tests/test_r1148_integration.py \
  tests/test_r1150_n_of_1_consolidation.py \
  tests/test_r1150_catalog_audit.py \
  -q --tb=short

echo "[2/6] Regressão metacognitiva existente"
"$PYTHON" -m pytest \
  tests/test_r1050_metacognitive_gate.py \
  tests/test_r886_metacognitive_loop.py \
  -q --tb=short

echo "[3/6] Configuração OpenCode"
"$PYTHON" -m integrations.opencode_cli --check

echo "[4/6] Auditoria de catálogo"
"$PYTHON" integrations/catalog_audit.py \
  --output /tmp/opencode/catalog_audit.json \
  >/tmp/opencode/catalog_audit_summary.json
"$PYTHON" - <<'PY'
import json

with open('/tmp/opencode/catalog_audit.json', encoding='utf-8') as handle:
    report = json.load(handle)
duplicates = report['duplicates']
assert duplicates['metadata_id_mismatches'] == [], 'agent_id não resolvido'
assert report['near_duplicate_agents'] == [], 'quase-duplicata não revisada'
assert report['drift']['catalog_not_in_config'] == [], 'drift catálogo→config'
assert report['drift']['config_not_in_catalog'] == [], 'drift config→catálogo'
assert report['missing_artifacts_total'] == 0, 'spec/test ausente'
print('catalog audit ok:', report['counts'], 'sha256=', report['report_sha256'])
PY

echo "[5/6] Whitespace"
git diff --check

echo "[6/6] Lean 4 + Mathlib"
if [[ "$LEAN" -eq 1 ]]; then
  if ! command -v lake >/dev/null 2>&1; then
    echo "lake ausente; Lean não executado" >&2
    exit 3
  fi
  (
    cd livro-core/lean
    for name in ComplexProofs CorrelationCounterproof; do
      lake env lean "../../lean/quantum-cb/${name}.lean" 2>&1 | tee "/tmp/opencode/${name}.log"
      if grep -Eq "sorryAx|error:" "/tmp/opencode/${name}.log"; then
        echo "falha em ${name}" >&2
        exit 1
      fi
    done
    lake env lean ../../lean/quantum-cb/MathlibCounterproof.lean
  )
else
  echo "Lean não solicitado; use --lean para compilar os três arquivos."
fi

echo "GATE LOCAL OK"
