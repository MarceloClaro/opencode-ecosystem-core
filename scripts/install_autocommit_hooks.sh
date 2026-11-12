#!/usr/bin/env bash
# Instala o hook post-commit que envia cada commit ao remoto configurado.
set -euo pipefail

REPO_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
HOOK="$REPO_ROOT/.git/hooks/post-commit"

if [ ! -d "$REPO_ROOT/.git" ]; then
  echo "ERRO: $REPO_ROOT não é um repositório Git." >&2
  exit 1
fi

cat >"$HOOK" <<'EOF'
#!/usr/bin/env bash
# R1109: todo commit local tenta push imediato; falha é registrada, não bloqueia.
set -u
repo=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
script="$repo/scripts/autocommit_push.sh"
[ -x "$script" ] || exit 0
"$script" --push-only >/dev/null 2>&1 || true
EOF
chmod 700 "$HOOK"
echo "hook instalado: $HOOK"
