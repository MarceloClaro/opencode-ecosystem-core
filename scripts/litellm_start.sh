#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${LITELLM_ENV_FILE:-$ROOT/.env.litellm}"
if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  set +a
fi
: "${LITELLM_MASTER_KEY:?defina LITELLM_MASTER_KEY em .env.litellm}"
exec "$HOME/.cache/opencode-pilot/venvs/litellm/bin/litellm" \
  --config "$ROOT/config/litellm.yaml" \
  --host 127.0.0.1 --port "${LITELLM_PORT:-4000}"
