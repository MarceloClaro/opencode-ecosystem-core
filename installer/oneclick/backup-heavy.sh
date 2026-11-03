#!/usr/bin/env bash
# Backup dos artefatos que ficam fora do Git (mídia, modelos, biblioteca local).
# Uso: ./installer/oneclick/backup-heavy.sh /caminho/externo [--dry-run]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEST="${1:-}"
MODE="${2:-}"
if [[ -z "$DEST" ]]; then
  echo "Uso: $0 /caminho/externo [--dry-run]" >&2
  exit 2
fi
case "$DEST" in
  "$ROOT"|"$ROOT"/*) echo "Destino não pode estar dentro do repositório." >&2; exit 2 ;;
esac
DIRS=(pilots "Panoramica_AI_OdontoCA_2_0_SDD_TDD_CASE117" editor-workspace "biblioteca ai")
echo "Raiz: $ROOT"
for d in "${DIRS[@]}"; do
  [[ -e "$ROOT/$d" ]] && du -sh "$ROOT/$d"
done
if [[ "$MODE" == "--dry-run" ]]; then
  echo "Dry-run: nenhum arquivo criado."
  exit 0
fi
mkdir -p "$DEST"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$DEST/opencode-heavy-$STAMP.tar.zst"
command -v zstd >/dev/null 2>&1 || { echo "zstd ausente; instale zstd ou use tar -czf." >&2; exit 2; }
tar --zstd --exclude='*/node_modules' --exclude='*.tmp' \
  -cf "$OUT" -C "$ROOT" "${DIRS[@]}"
sha256sum "$OUT" | tee "$OUT.sha256"
echo "Backup: $OUT"
