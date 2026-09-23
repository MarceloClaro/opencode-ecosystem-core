#!/usr/bin/env bash
# ============================================================================
# budget_guard.sh — Gate de orçamento (pre-push / guarda de tamanho)
# ----------------------------------------------------------------------------
# Calcula peso total de uma árvore EXCLUINDO .git, lista os N maiores arquivos
# e bloqueia se total > LIMIT_MB (padrão 1000 MB — GitHub Pages) ou se algum
# arquivo > MAX_FILE_MB (padrão 25 MiB — limite por entry em CDNs comuns).
# Exit 0 = ok, 1 = orçamento estourado (fail-closed).
#
# Uso: budget_guard.sh DIR [LIMIT_MB] [MAX_FILE_MB]
# ============================================================================
set -u
DIR="${1:?uso: budget_guard.sh DIR [LIMIT_MB] [MAX_FILE_MB]}"
LIMIT_MB="${2:-1000}"
MAX_FILE_MB="${3:-25}"

# --- instrumentação de eficiência (SPEC-975) --------------------------------
T0=$(date +%s%N)
RECORD_OP="budget"
trap '__RC=$?; if [ "${OP_TIMING:-1}" = "1" ]; then _D=$(python3 -c "print(($(date +%s%N) - ${T0}) / 1e9)" 2>/dev/null || echo 0); python3 -m integrations.op_timing record "${RECORD_OP}" "${_D}" "$([ ${__RC} -eq 0 ] && echo ok || echo fail)" >/dev/null 2>&1 || true; fi' EXIT
[ -d "${DIR}" ] || { echo "budget_guard: DENIED (dir não existe: ${DIR})" >&2; exit 1; }

TOTAL_BYTES="$(du -sb "${DIR}" 2>/dev/null | awk '{print $1}' || true)"
# descontar .git se existir
GIT_BYTES=0
[ -d "${DIR}/.git" ] && GIT_BYTES="$(du -sb "${DIR}/.git" 2>/dev/null | awk '{print $1}' || echo 0)"
TOTAL_BYTES=$((TOTAL_BYTES - GIT_BYTES))
[ "${TOTAL_BYTES}" -lt 0 ] && TOTAL_BYTES=0
TOTAL_MB=$(( TOTAL_BYTES / 1024 / 1024 ))

BIGGEST="$(find "${DIR}" -type f -not -path '*/.git/*' -printf '%s %p\n' 2>/dev/null \
  | sort -rn | head -5 | awk '{printf "  %.1f MiB  %s\n", $1/1048576, $2}')"
oversize="$(find "${DIR}" -type f -not -path '*/.git/*' -size +"${MAX_FILE_MB}M" 2>/dev/null | head -5)"

HAS_OVERSIZE=0
[ -n "${oversize}" ] && HAS_OVERSIZE=1

OVER_TOTAL=0
[ "${TOTAL_MB}" -gt "${LIMIT_MB}" ] && OVER_TOTAL=1

echo "budget_guard: total=${TOTAL_MB} MiB (limite ${LIMIT_MB} MiB), por-arquivo: ${HAS_OVERSIZE}"
[ -n "${BIGGEST}" ] && echo "maiores arquivos:" && echo "${BIGGEST}"

if [ "${OVER_TOTAL}" -eq 0 ] && [ "${HAS_OVERSIZE}" -eq 0 ]; then
  echo "budget_guard: GRANTED"
  exit 0
fi
echo "budget_guard: DENIED (total_ok=${OVER_TOTAL}, oversize=${HAS_OVERSIZE})" >&2
exit 1