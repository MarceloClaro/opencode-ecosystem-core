#!/usr/bin/env bash
# R1151 — reprodução delimitada para revisor independente.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
mkdir -p /tmp/opencode

bash scripts/local_ci.sh "$@"

python3 -m pytest \
  tests/test_r1146_complex_proof_gate.py \
  tests/test_r1147_correlation_gate.py \
  tests/test_r1147_correlation_layout.py \
  -q --tb=short

python3 integrations/catalog_audit.py \
  --output /tmp/opencode/catalog_audit_external.json \
  >/tmp/opencode/catalog_audit_external_summary.json

sha256sum \
  lean/quantum-cb/ComplexProofs.lean \
  lean/quantum-cb/CorrelationCounterproof.lean \
  harnesses/quantum-error-mitigation/resultados/r1146_complex_proofs/certificate.json \
  harnesses/quantum-error-mitigation/resultados/r1147_correlation_layout/certificate.json \
  reports/r1150/catalog_audit.json \
  > /tmp/opencode/external_r1151_hashes.txt

echo "Reprodução concluída. Hashes em /tmp/opencode/external_r1151_hashes.txt"
