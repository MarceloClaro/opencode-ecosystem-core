#!/usr/bin/env bash
# R1109 — checkpoint automático do OpenCode Ecosystem Core.
#
# Modos:
#   scripts/autocommit_push.sh              # commit do que houver + push
#   scripts/autocommit_push.sh --push-only  # somente push (usado pelo hook)
#
# Regras:
# - respeita .gitignore; nunca usa `git add -f`;
# - recusa arquivos acima de 50 MB, para não repetir o incidente do pacote de 177 MB;
# - não grava o token em argv nem no log; usa GIT_ASKPASS temporário;
# - remote local/file:// dispensa token (usado nos testes);
# - log fica fora do repositório, em ~/.local/state/opencode/autocommit-push.log.

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
cd "$REPO_ROOT"

MODE="commit-push"
if [ "${1:-}" = "--push-only" ]; then
  MODE="push-only"
fi

BRANCH="${AUTOCOMMIT_BRANCH:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)}"
TOKEN_FILE="${OPENCODE_GITHUB_PAT_FILE:-$HOME/.config/opencode/github-pat}"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/opencode"
LOG="$STATE_DIR/autocommit-push.log"
MAX_BYTES=$((50 * 1024 * 1024))

mkdir -p "$STATE_DIR"

log() {
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >>"$LOG"
}

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  log "skip: $REPO_ROOT não é repositório Git"
  exit 0
fi

# Evita duas execuções concorrentes (timer + hook).
if command -v flock >/dev/null 2>&1; then
  exec 9>"$STATE_DIR/autocommit.lock"
  if ! flock -n 9; then
    log "skip: lock ocupado"
    exit 0
  fi
fi

if [ "$MODE" = "commit-push" ]; then
  if [ -z "$(git status --porcelain)" ]; then
    log "sem mudanças"
  else
    git add --sparse -A

    if git diff --cached --quiet; then
      log "sem mudanças rastreáveis"
    else
      too_big=""
      while IFS= read -r -d '' path; do
        [ -f "$path" ] || continue
        size=$(stat -c %s -- "$path" 2>/dev/null || echo 0)
        if [ "$size" -gt "$MAX_BYTES" ]; then
          too_big="${too_big}${path} (${size} bytes)\n"
        fi
      done < <(git diff --cached --name-only -z)

      if [ -n "$too_big" ]; then
        log "skip: arquivo acima de 50 MB: $too_big"
        exit 0
      fi

      if git commit -m "chore(auto): checkpoint $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$LOG" 2>&1; then
        log "commit $(git rev-parse --short HEAD) em $BRANCH"
      else
        log "erro: commit falhou"
        exit 1
      fi
    fi
  fi
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  log "skip push: sem remote origin"
  exit 0
fi

if ! git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
  if git show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
    git branch --set-upstream-to="origin/$BRANCH" "$BRANCH" >/dev/null 2>&1 || true
  else
    log "skip push: sem upstream para $BRANCH"
    exit 0
  fi
fi

remote_url=$(git remote get-url origin)

push_local() {
  if GIT_TERMINAL_PROMPT=0 git push origin "$BRANCH" >>"$LOG" 2>&1; then
    log "push ok (remote local)"
  else
    log "push falhou (remote local)"
    exit 1
  fi
}

push_with_askpass() {
  local username="$1"
  local password_source="$2"
  local askpass
  askpass=$(mktemp)
  # shellcheck disable=SC2064
  trap "rm -f -- '$askpass'" EXIT
  cat >"$askpass" <<EOF
#!/bin/sh
case "\$1" in
  *Username*) printf '%s\n' '$username' ;;
  *Password*) $password_source ;;
esac
EOF
  chmod 700 "$askpass"
  if GIT_ASKPASS="$askpass" GIT_TERMINAL_PROMPT=0 git push origin "$BRANCH" >>"$LOG" 2>&1; then
    log "push ok"
  else
    log "push falhou"
    exit 1
  fi
}

case "$remote_url" in
  /*|file://*)
    push_local
    ;;
  *)
    if [ -s "$TOKEN_FILE" ]; then
      push_with_askpass "${GIT_USERNAME:-MarceloClaro}" "cat '$TOKEN_FILE'"
    elif [ -n "${GITHUB_TOKEN:-}" ]; then
      push_with_askpass "${GIT_USERNAME:-x-access-token}" "printf '%s\\n' \"\$GITHUB_TOKEN\""
    else
      log "push pendente: token ausente em $TOKEN_FILE"
      exit 0
    fi
    ;;
esac
