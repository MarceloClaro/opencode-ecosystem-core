#!/usr/bin/env bash
# ============================================================================
# Converte assets/icon.iconset/ (gerado por assets/generate_icon.py) em
# assets/icon.icns — PRECISA rodar em macOS real (usa `iconutil`, que não
# existe em Linux/Windows).
#
# Uso (num Mac, com o repo clonado):
#   bash installer/macos/build_icns.sh
# ============================================================================
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
ICONSET_DIR="$ROOT/assets/icon.iconset"
ICNS_OUT="$ROOT/assets/icon.icns"

if ! command -v iconutil >/dev/null 2>&1; then
    echo "[ERRO] iconutil não encontrado — este script só funciona em macOS." >&2
    exit 1
fi

if [ ! -d "$ICONSET_DIR" ]; then
    echo "[ERRO] $ICONSET_DIR não existe. Rode primeiro: python3 assets/generate_icon.py" >&2
    exit 1
fi

iconutil -c icns "$ICONSET_DIR" -o "$ICNS_OUT"
echo "[OK] Gerado: $ICNS_OUT"
