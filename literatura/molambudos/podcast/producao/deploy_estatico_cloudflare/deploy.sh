#!/usr/bin/env bash
# Deploy do site estático do podcast Molambudos no Cloudflare (R2 + Worker).
# Prerequisito: conta gratuita Cloudflare (https://dash.cloudflare.com/sign-up)
# Uso (na raiz do repo):
#   bash research/producao_real/deploy_estatico_cloudflare/deploy.sh
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACOTE="$REPO/research/producao_real/pacote_editorial_podcast_molambudos"
BUCKET="molambudos-podcast"
WRANGLER="npx --yes wrangler@latest"

cd "$DIR"
echo "REPO=$REPO"
echo "PACOTE=$PACOTE"
echo "BUCKET=$BUCKET"

echo
echo "=== 1/4 login no Cloudflare (abrindo navegador ou URL de autorização) ==="
$WRANGLER login

echo
echo "=== 2/4 criar bucket R2 (se já existir, segue) ==="
$WRANGLER r2 bucket create "$BUCKET" || true

echo
echo "=== 3/4 upload de todos os arquivos do pacote para o R2 ==="
cd "$PACOTE"
TOTAL=$(find . -type f | wc -l)
N=0
FAILED=0
while IFS= read -r f; do
  N=$((N + 1))
  key="${f#./}"
  printf "  [%s/%s] %s\n" "$N" "$TOTAL" "$key"
  if ! $WRANGLER r2 object put "$BUCKET/$key" --file "$f"; then
    FAILED=$((FAILED + 1))
    echo "    !! FALHOU: $key"
  fi
done < <(find . -type f | sort)
echo "uploads: $((N - FAILED))/$N ok ($FAILED falhas)"

echo
echo "=== 4/4 deploy do Worker (site) ==="
cd "$DIR"
$WRANGLER deploy

echo
echo "=== Pronto! A URL final do site está acima, terminando em .workers.dev ==="