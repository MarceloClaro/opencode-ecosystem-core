#!/usr/bin/env bash
#
# build.sh — compila o manual técnico RAG/Recamán para PDF.
#
# Uso:  ./build.sh            -> compila e deixa o PDF em docs/r456_manual_tecnico_rag/
#       ./build.sh clean      -> remove artefatos de compilação (.aux, .log, etc.)
#
# Requisitos: pdflatex, bibtex, makeindex, latexmk (TeX Live).
# Usa a classe abntex2 local do repositório (publishing/templates/abntex2).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ABNTEX_DIR="../../publishing/templates/abntex2"
SRC="manual_rag_recaman"

clean() {
  rm -f *.aux *.log *.out *.toc *.bbl *.blg *.lof *.lot *.synctex.gz \
        *.fls *.fdb_latexmk *.run.xml *.bcf *.nav *.snm *.vrb *.idx *.ilg *.ind
  echo "[build] artefatos de compilação removidos."
}

if [ "${1:-}" = "clean" ]; then
  clean
  exit 0
fi

# Garante que a classe abntex2 local seja encontrada.
export TEXINPUTS=".:${ABNTEX_DIR}/:${TEXINPUTS:-}"
export BSTINPUTS=".:${ABNTEX_DIR}/:${BSTINPUTS:-}"
export BIBINPUTS=".:${ABNTEX_DIR}/:${BIBINPUTS:-}"

echo "[build] 1/3 pdflatex (passada 1)..."
pdflatex -interaction=nonstopmode -halt-on-error "$SRC" >/dev/null

echo "[build] 2/3 bibtex + makeindex..."
bibtex "$SRC" >/dev/null 2>&1 || true
makeindex -q "$SRC" >/dev/null 2>&1 || true

echo "[build] 3/3 pdflatex (passadas finais)..."
pdflatex -interaction=nonstopmode -halt-on-error "$SRC" >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error "$SRC" >/dev/null

if [ -f "${SRC}.pdf" ]; then
  echo "[build] OK -> ${SCRIPT_DIR}/${SRC}.pdf"
else
  echo "[build] ERRO: PDF não gerado. Rode 'pdflatex ${SRC}.tex' manualmente para ver o log." >&2
  exit 1
fi
