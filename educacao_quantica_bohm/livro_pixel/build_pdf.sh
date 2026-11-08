#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIVRO="$ROOT/educacao_quantica_bohm/livro_pixel"

for cmd in python3 pandoc weasyprint; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Requisito ausente: $cmd" >&2
    exit 1
  fi
done

if [ ! -x "$ROOT/.venv-pdf/bin/python" ]; then
  python3 -m venv --system-site-packages "$ROOT/.venv-pdf"
fi

"$ROOT/.venv-pdf/bin/python" -m pip install --quiet --ignore-installed \
  -r "$LIVRO/requirements-pdf.txt"

cd "$LIVRO"
python3 build_pixel_fast.py
