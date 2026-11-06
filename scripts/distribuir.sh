#!/usr/bin/env bash
# Gera um pacote reproduzível de distribuição do ecossistema.
#
# Uso:
#   ./scripts/distribuir.sh [versao] [--completo]
#
#   versao      padrão: git describe --tags --always
#   --completo  inclui toda a mídia/dados rastreados (~780 MB comprimido).
#               Sem a flag, gera o pacote leve (~160 MB), sem podcasts,
#               binários de evidência e apresentações.
#
# Saída:
#   release/<versao>/
#   ├── opencode-ecosystem-core-<versao>.tar.gz
#   ├── entregaveis/                    (PDF, DOCX, MP4, SRT)
#   ├── opencode-ecosystem-core-<versao>-entregaveis.zip
#   ├── MANIFEST.md
#   └── SHA256SUMS.txt
set -euo pipefail

cd "$(dirname "$0")/.."

VERSAO=""
MODO="leve"
for arg in "$@"; do
  case "$arg" in
    --completo) MODO="completo" ;;
    -*) echo "Opção desconhecida: $arg" >&2; exit 2 ;;
    *) VERSAO="$arg" ;;
  esac
done
VERSAO="${VERSAO:-$(git describe --tags --always --dirty)}"
DEST="release/${VERSAO}"
ARQ="opencode-ecosystem-core-${VERSAO}"

if [ -n "$(git status --porcelain)" ]; then
  echo "AVISO: há alterações não commitadas; o tarball usa apenas o HEAD." >&2
fi

rm -rf "$DEST"
mkdir -p "$DEST/entregaveis"

echo "==> Lista de arquivos (modo: ${MODO})"
LISTA="$(mktemp)"
python3 - "$MODO" > "$LISTA" <<'PY'
import fnmatch
import os
import subprocess
import sys

modo = sys.argv[1]
arquivos = [
    f.decode() for f in subprocess.run(
        ["git", "ls-files", "-z"], capture_output=True
    ).stdout.split(b"\0") if f
]

# Mídia e dados pesados: ficam fora do pacote leve, mas seguem no repositório.
PREFIXOS = (
    "livro-core/output/",
    "odonto/preservado/",
    "odonto/submission_package",
    "docs/evidence/",
    "validacao_externa/",
    ".backups/",
    "manuscrito_porescrito799_R522/",
    "templates/projects/",
)
GLOBS = (
    "*.m4a", "*.mp3", "*.mp4", "*.wav", "*.xdv", "*.pptx", "*.msi", "*.zip",
)

for f in arquivos:
    if modo == "leve":
        if any(f.startswith(p) for p in PREFIXOS):
            continue
        if any(fnmatch.fnmatch(f, g) for g in GLOBS):
            continue
    sys.stdout.buffer.write(f.encode() + b"\0")
PY

echo "==> Fonte (tar dos arquivos rastreados no HEAD)"
tar --null -czf "${DEST}/${ARQ}.tar.gz" \
  -C "$PWD" --transform "s,^,${ARQ}/," -T "$LISTA"
rm -f "$LISTA"

echo "==> Entregáveis"
ENTREGAS=(
  "artigos/TCC_MARCELO_AUTISMO_AH_SD/TCC_MARCELO_AUTISMO_AH_SD.pdf"
  "artigos/TCC_MARCELO_AUTISMO_AH_SD/TCC_MARCELO_AUTISMO_AH_SD.docx"
  "artigos/TCC_MARCELO_AUTISMO_AH_SD/video_banca/Dupla_Excepcionalidade_Banca.mp4"
  "artigos/TCC_MARCELO_AUTISMO_AH_SD/video_banca/legendas.srt"
  "artigos/ARTIGO_MARIA_SOCORRO_TEA/01_ARTIGO_CORRIGIDO_ABNT.pdf"
  "artigos/ARTIGO_MARIA_SOCORRO_TEA/02_ARTIGO_QUALIS_A1.pdf"
  "artigos/ARTIGO_MARIA_SOCORRO_TEA/TCC/TCC_MARIA_SOCORRO.pdf"
)
for f in "${ENTREGAS[@]}"; do
  if [ ! -f "$f" ]; then
    echo "FALTANDO: $f" >&2
    exit 1
  fi
  cp "$f" "$DEST/entregaveis/"
done

echo "==> Manifesto"
{
  echo "# Manifesto de distribuição"
  echo
  echo "- **Versão:** \`${VERSAO}\`"
  echo "- **Commit:** \`$(git rev-parse HEAD)\`"
  echo "- **Data (UTC):** $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "- **Modo:** \`${MODO}\`"
  echo "- **Fonte:** \`${ARQ}.tar.gz\` (somente arquivos rastreados no HEAD)"
  if [ "$MODO" = "leve" ]; then
    echo "  - Exclui podcasts, vídeos antigos, binários de evidência, apresentações"
    echo "    e pacotes compactados. Use \`--completo\` para incluir tudo."
  fi
  echo
  echo "## Entregáveis"
  echo
  echo "| Arquivo | Tamanho |"
  echo "|---|---:|"
  for f in "$DEST"/entregaveis/*; do
    printf "| %s | %s |\n" "$(basename "$f")" "$(du -h "$f" | cut -f1)"
  done
  echo
  echo "## Verificação"
  echo
  echo '```bash'
  echo 'sha256sum -c SHA256SUMS.txt'
  echo '```'
} > "$DEST/MANIFEST.md"

echo "==> Pacote ZIP dos entregáveis"
if command -v zip >/dev/null 2>&1; then
  ( cd "$DEST" && zip -qr "${ARQ}-entregaveis.zip" entregaveis MANIFEST.md )
else
  ( cd "$DEST" && python3 -m zipfile -c "${ARQ}-entregaveis.zip" entregaveis MANIFEST.md )
fi

echo "==> SHA-256"
( cd "$DEST" && find . -type f ! -name SHA256SUMS.txt -print0 \
    | sort -z | xargs -0 sha256sum > SHA256SUMS.txt )

echo
echo "OK: $DEST"
du -sh "$DEST"/* 2>/dev/null | sort -hr | sed 's/^/    /'
