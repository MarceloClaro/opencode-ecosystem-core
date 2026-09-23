#!/usr/bin/env bash
# ============================================================================
# js_smoke_dom.sh — Hook post-edit: smoke test de JS inline com stub de DOM
# ----------------------------------------------------------------------------
# Usa smoke_dom_stub.js (Node) para extrair <script> de um .html e executar
# com DOM mínimo. Falha (exit 1) se houver erro de runtime — a classe de bug
# R580 ('num' vs '.num') que node --check não detecta.
#
# Uso:
#   js_smoke_dom.sh ARQUIVO.html [--assert-count N]
#   js_smoke_dom.sh --dir DIR [--assert-count N]   # prova todos os *.html
# ============================================================================
set -u
HOOKS_DIR="$(cd "$(dirname "$0")" && pwd)"
STUB="${HOOKS_DIR}/smoke_dom_stub.js"

# --- instrumentação de eficiência (SPEC-975) --------------------------------
T0=$(date +%s%N)
RECORD_OP="smoke"
trap '__RC=$?; if [ "${OP_TIMING:-1}" = "1" ]; then _D=$(python3 -c "print(($(date +%s%N) - ${T0}) / 1e9)" 2>/dev/null || echo 0); python3 -m integrations.op_timing record "${RECORD_OP}" "${_D}" "$([ ${__RC} -eq 0 ] && echo ok || echo fail)" >/dev/null 2>&1 || true; fi' EXIT

[ -f "${STUB}" ] || { echo "js_smoke_dom: DENIED (stub ausente)" >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "js_smoke_dom: DENIED (node ausente)" >&2; exit 1; }

if [ "${1:-}" = "--dir" ]; then
  DIR="${2:?uso: js_smoke_dom.sh --dir DIR [--assert-count N]}"
  shift 2
  FAILS=0
  FILES=0
  while IFS= read -r f; do
    FILES=$((FILES + 1))
    if ! node "${STUB}" "$f" "$@"; then FAILS=$((FAILS + 1)); fi
  done < <(find "${DIR}" -maxdepth 2 -name '*.html' -not -path '*/.git/*' 2>/dev/null)
  echo "js_smoke_dom: ${FILES} arquivos, ${FAILS} falhas"
  [ "${FAILS}" -eq 0 ]
  exit $?
fi

TARGET="${1:?uso: js_smoke_dom.sh ARQUIVO.html [--assert-count N]}"
shift
if ! node "${STUB}" "${TARGET}" "$@"; then
  exit 1
fi
echo "js_smoke_dom: GRANTED"
exit 0