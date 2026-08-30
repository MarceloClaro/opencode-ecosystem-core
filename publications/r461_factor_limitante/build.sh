#!/usr/bin/env bash
# Build reprodutível do artigo R461.
# Uso: bash build.sh  (a partir do diretório submission ou raiz do artigo)
set -euo pipefail
cd "$(dirname "$0")"

echo "[build] pdflatex (1/4)…"
pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null 2>&1 || true
echo "[build] biber (2/4)…"
biber main >/dev/null 2>&1 || true
echo "[build] pdflatex (3/4)…"
pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null 2>&1 || true
echo "[build] pdflatex (4/4)…"
pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null 2>&1 || true
echo "[build] OK → main.pdf"
