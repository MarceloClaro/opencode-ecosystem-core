#!/usr/bin/env bash
# ============================================================================
# credential_guard.sh — Hook pre-commit (gate de credencial + identidade)
# ----------------------------------------------------------------------------
# Valida que a credencial GitHub está parseável SEM imprimir o token e injeta
# a identidade do autor em repos externos (sem -c por chamada).
# Resposta: GRANTED | DENIED (fail-closed). Exit 0 = ok, 1 = bloqueado.
#
# Uso:
#   credential_guard.sh [REPO_DIR]
#     REPO_DIR opcional — pasta de repo git externo para injetar identidade.
# ============================================================================
set -u
REPO_DIR="${1:-}"

# --- instrumentação de eficiência (SPEC-975) --------------------------------
T0=$(date +%s%N)
RECORD_OP="credential"
trap '__RC=$?; if [ "${OP_TIMING:-1}" = "1" ]; then _D=$(python3 -c "print(($(date +%s%N) - ${T0}) / 1e9)" 2>/dev/null || echo 0); python3 -m integrations.op_timing record "${RECORD_OP}" "${_D}" "$([ ${__RC} -eq 0 ] && echo ok || echo fail)" >/dev/null 2>&1 || true; fi' EXIT

GRANTED=0

# --- 1. token parseável? (SPLIT seguro; token nunca é exibido) ---------------
CRED_FILE="${HOME}/.git-credentials"
TOKEN_LEN=0
if [ -r "${CRED_FILE}" ]; then
  LINE="$(grep -m1 'github.com' "${CRED_FILE}" 2>/dev/null || true)"
  if [ -n "${LINE}" ]; then
    AFTER_AT="${LINE#*@}"                    # remove "https://user:"
    USERPORTION="${LINE#https://}"
    USER="${USERPORTION%%:*}"
    TOKEN="${AFTER_AT%@github.com}"          # remove sufixo host
    # ~/.git-credentials é "https://user:token@github.com"
    TOKEN="${USERPORTION#*:}"                # parte após 'user:'
    TOKEN_LEN="${#TOKEN}"
    if [ "${TOKEN_LEN}" -ge 20 ] && [ "${TOKEN}" != "${USERPORTION}" ]; then
      GRANTED=1
    fi
  fi
fi

# --- 2. identidade em repo externo -------------------------------------------
IDENTITY_OK=1
if [ -n "${REPO_DIR}" ] && [ -d "${REPO_DIR}/.git" ]; then
  git -C "${REPO_DIR}" config user.name  "MarceloClaro" >/dev/null 2>&1 || IDENTITY_OK=0
  git -C "${REPO_DIR}" config user.email "marceloclarof@poli-integrada.com" >/dev/null 2>&1 || IDENTITY_OK=0
else
  IDENTITY_OK=0  # repo obrigatório ausente => não sumir silenciosamente
fi

if [ "${GRANTED}" -eq 1 ] && [ "${IDENTITY_OK}" -eq 1 ]; then
  echo "credential_guard: GRANTED (token len=${TOKEN_LEN}, identidade ok em ${REPO_DIR:-<n/a>})"
  exit 0
fi
echo "credential_guard: DENIED (token_len=${TOKEN_LEN}, identidade_ok=${IDENTITY_OK})" >&2
exit 1