# HOSPEDAGEM ESTÁTICA GRATUITA — Cloudflare (R2 + Worker)

## Resposta curta

**Sim, é possível ter um site estático 100% gratuito e permanente** para o pacote
Molambudos (1.004MB, incluindo 26 áudios de 31–39MB) — usando **Cloudflare R2 +
Worker**:

- **10GB de armazenamento gratuito** (usaremos ~1GB)
- **Egress (transferência) gratuito** — quem ouvir não consome nada
- Arquivos individuais de dezenas de MB: suportados (R2 aceita até 5GB/objeto)
- Endereço fixo `*.workers.dev` **sem comprar domínio**
- Arquivo **permanente** enquanto a conta existir

## Por que as opções "óbvias" NÃO servem neste caso (limites oficiais 2026)

| Plataforma | Limite oficial | Resultado |
|---|---|---|
| Cloudflare Pages | 25 MiB por arquivo (qualquer plano) | ❌ 26 áudios de 31–39MB |
| GitHub Pages | site publicado ≤ 1GB | ❌ 1.004GB |
| Netlify Free | arquivos >10MB travam deploy (drop); Large Media é pago | ❌ |

Fontes: developers.cloudflare.com/pages/platform/limits/ · docs.github.com/en/pages/.../github-pages-limits · docs.netlify.com (Netlify Drop / Large Media).

## Como publicar (3 passos, ~5 minutos)

1. **Crie uma conta gratuita** (se ainda não tiver):
   https://dash.cloudflare.com/sign-up
   (e-mail + senha; o plano Free inclui Workers e R2.)

2. **Rode o deploy** na raiz do repo:
   ```bash
   bash research/producao_real/deploy_estatico_cloudflare/deploy.sh
   ```
   O script faz tudo:
   - `wrangler login` (autoriza no navegador / mostra URL de login)
   - cria o bucket R2 `molambudos-podcast`
   - sobe os 68 arquivos do pacote (HTML, players, infográficos, PDF, áudios…)
   - publica o Worker e imprime a **URL final** (`*.workers.dev`)

3. **Copie a URL final** e compartilhe (é ela que vai nos grupos / METADADOS).

## Como funciona o Worker

`src/index.js` — roteia a URL para o objeto R2 equivalente:

- `/` → `index_podcast.html`
- Tipos MIME corretos (m4a → `audio/mp4`, mp4 → `video/mp4`, svg, xml…)
- Suporte a **Range/206** (barra de seek dos players funciona)
- Suporte a HEAD
- Cache de 1 hora (`Cache-Control: public, max-age=3600`)

## Atualizações futuras

Para publicar uma versão nova do site (ex.: novo infográfico):

```bash
npx wrangler r2 object put molambudos-podcast/<arquivo> --file <arquivo-local>
npx wrangler deploy   # só se mudou src/index.js ou wrangler.toml
```

## Limites honestos

- **Conta gratuita obrigatória** (é o preço de host permanente de verdade; não existe host permanente gratuito sem conta).
- Workers Free: 100.000 requisições/dia — folga enorme para divulgação de podcast.
- R2 Free: 10GB storage + egress gratuito — usamos ~1GB.
- Se quiser domínio próprio depois: `wrangler.toml` aceita `routes` sem custo extra de conta Free (o domínio em si é pago).

## Relação com o túnel temporário

O link `*.trycloudflare.com` atual é uma **solução temporária** (muda a cada
reinício). Este R2+Worker é a **solução definitiva**. Depois do deploy,
atualizar `METADADOS_PODCAST.json`, `README_PODCAST.md`, `DIVULGACAO_REDES.md`
e `INSTRUCOES_UPLOAD.md` com a URL nova (a antiga pode ser mantida como
espelho).