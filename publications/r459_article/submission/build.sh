#!/usr/bin/env bash
# =====================================================================
# Build reprodutível do LaTeX de SUBMISSÃO e geração do PDF.
#
# Uso:
#   bash build.sh            # gera submission.pdf (3 passagens + bibtex)
#
# Requisitos: pdflatex, bibtex (TeX Live). Saída: submission.pdf.
# O PDF é um artefato gerado (gitignored); apenas as fontes são versionadas.
# =====================================================================
set -euo pipefail
cd "$(dirname "$0")"

echo "[build] passagem 1 (pdflatex)"
pdflatex -interaction=nonstopmode submission.tex >/dev/null

echo "[build] bibtex"
bibtex submission >/dev/null

echo "[build] passagem 2 (pdflatex)"
pdflatex -interaction=nonstopmode submission.tex >/dev/null

echo "[build] passagem 3 (pdflatex)"
pdflatex -interaction=nonstopmode submission.tex >/dev/null

echo "[build] OK → submission.pdf"
ls -la submission.pdf
