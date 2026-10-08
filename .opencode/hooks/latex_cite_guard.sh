#!/usr/bin/env bash
# ============================================================================
# latex_cite_guard.sh — Hook pre-write: nega .tex com \cite sem entrada no .bib
# ----------------------------------------------------------------------------
# Fail-closed: sai 1 (DENIED) quando algum .tex do diretório referencia chaves
# \cite/\citeonline sem entrada @ correspondente em qualquer .bib do projeto.
# Evita a classe de bug "Citation undefined" ainda na edição, antes da compilação.
#
# Uso:
#   latex_cite_guard.sh DIR_DO_ARTIGO
# Registro no engine (core-hooks):
#   HookMatcher("Write", hooks=[latex_cite_guard])  # via hooks.engine
# ============================================================================
set -u
DIR="${1:-}"

[ -n "${DIR}" ] || { echo "latex_cite_guard: DENIED (diretório não informado)" >&2; exit 1; }
[ -d "${DIR}" ] || { echo "latex_cite_guard: DENIED (diretório inexistente: ${DIR})" >&2; exit 1; }

mapfile -t TEXS < <(find "${DIR}" -maxdepth 2 -name '*.tex' 2>/dev/null)
mapfile -t BIBS < <(find "${DIR}" -maxdepth 2 -name '*.bib' 2>/dev/null)

[ "${#TEXS[@]}" -gt 0 ] || { echo "latex_cite_guard: ALLOW (sem .tex no diretório)"; exit 0; }
[ "${#BIBS[@]}" -gt 0 ] || { echo "latex_cite_guard: DENIED (há .tex mas nenhum .bib em ${DIR})" >&2; exit 1; }

CITADAS="$(grep -rhoE '\\cite[a-z]*\{[^}]*\}' "${TEXS[@]}" 2>/dev/null \
  | grep -oE '\{[^}]*\}' | tr -d '{}' | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | sort -u)"
[ -n "${CITADAS}" ] || { echo "latex_cite_guard: ALLOW (nenhuma citação)"; exit 0; }

ENTRADAS="$(grep -rhoE '@[A-Za-z]+\{[A-Za-z0-9:_-]+' "${BIBS[@]}" 2>/dev/null \
  | grep -oE '\{[A-Za-z0-9:_-]+' | tr -d '{' | sort -u)"

FALTAM=0
while IFS= read -r chave; do
  [ -n "${chave}" ] || continue
  if ! printf '%s\n' "${ENTRADAS}" | grep -qxF "${chave}"; then
    echo "latex_cite_guard: DENIED (citação sem entrada no .bib: ${chave})" >&2
    FALTAM=1
  fi
done <<< "${CITADAS}"

[ "${FALTAM}" -eq 0 ] || exit 1
echo "latex_cite_guard: ALLOW (todas as citações possuem entrada no .bib)"
exit 0
