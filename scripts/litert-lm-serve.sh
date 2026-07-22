#!/usr/bin/env bash
# ============================================================================
# litert-lm-serve.sh — Wrapper do servidor LiteRT-LM com contexto grande
# ============================================================================
# Uso: ./scripts/litert-lm-serve.sh [--port PORT] [--max-tokens TOKENS] [--verbose]
#
# Exemplo:
#   ./scripts/litert-lm-serve.sh                     # porta 9379, 16384 tokens
#   LITERT_LM_MAX_TOKENS=32768 ./scripts/litert-lm-serve.sh  # 32768 tokens
# ============================================================================

set -euo pipefail

PORT="${1:-9379}"
MAX_TOKENS="${LITERT_LM_MAX_TOKENS:-20480}"
VERBOSE=""

# Processar argumentos
while [[ $# -gt 0 ]]; do
  case "$1" in
    --port) PORT="$2"; shift 2 ;;
    --max-tokens) MAX_TOKENS="$2"; shift 2 ;;
    --verbose) VERBOSE="--verbose"; shift ;;
    -h|--help)
      sed -n 's/^# \?//p' "$0" | head -20
      exit 0
      ;;
    *) shift ;;
  esac
done

echo "[litert-lm-serve] Starting server with MAX_TOKENS=${MAX_TOKENS} on port ${PORT}..."
echo "[litert-lm-serve] Cold start pode levar 2-5 min na primeira inicialização."
echo "[litert-lm-serve] Requests subsequentes: ~2-3s."

export LITERT_LM_MAX_TOKENS="${MAX_TOKENS}"
exec litert-lm serve --host 127.0.0.1 --port "${PORT}" ${VERBOSE}
