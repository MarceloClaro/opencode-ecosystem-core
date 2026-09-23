---
name: deploy-estatico-github-pages
description: Deploy e verificação de sites estáticos no GitHub Pages com prova física e anti-overclaim. Use quando publicar/atualizar site estático no GitHub Pages (molambudos, SPEC-973, index_podcast.html), checar status de build, extrair token do ~/.git-credentials, injetar identidade git, sondar URLs (probe GET+Range), verificar 404 de arquivos removidos ou conferir orçamento de peso. Não use para deploy em outra plataforma ou para código de aplicação.
---

# Deploy Estático — GitHub Pages (receita validada R569–R580)

Receita compilada de 12 ciclos reais (375–425) de publicação do site do podcast Molambudos.
Todo passo tem **prova física**: status HTTP, bytes, hash, exit code — nada de "parece que publicou".

## 1. Estrutura do repo do site (não é o repo do ecossistema)

```bash
SITE=/caminho/do/pacote_editorial_gh   # repo git próprio, branch main
git -C "$SITE" remote -v               # origin=https://github.com/USER/REPO.git
```

- O GitHub Pages **exige `index.html` na raiz** — sem ele, 404 (bug real R570/R571).
- Conteúdo real pode viver em outro caminho (`index_podcast.html`) e a raiz ser um redirect meta-refresh de ~770 bytes — **sondar sempre o caminho real**; `curl -L` não segue meta-refresh.

## 2. Token da API (NUNCA imprimir o token)

```bash
LINE="$(grep -m1 github.com ~/.git-credentials)"
CRED="${LINE#https://}"            # remove prefixo
TOKEN="${CRED#*:}"                 # parte após user:
TOKEN="${TOKEN%@github.com}"       # remove sufixo
# valida: ${#TOKEN} >= 20
```

Pull/status do build:
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  https://api.github.com/repos/USER/REPO/pages/builds/latest
# campos: status, duration, error — status "built" = pronto
```

## 3. Identidade git em repo externo

Commits falham com "Author identity unknown" se o repo externo não tem identidade:
```bash
git -C "$SITE" config user.name  "Seu Nome"
git -C "$SITE" config user.email "seu@email"
```
Garantia por chamada (se não quiser config persistente):
```bash
git -c user.name="Seu Nome" -c user.email="seu@email" -c core.hooksPath=/dev/null -C "$SITE" commit -am "msg"
```

## 4. Prova física de sondagem (nunca HEAD)

O GitHub Pages **falha HEAD** em m4a (só `GET` funciona, com Range 206):
```bash
curl -s -o /dev/null -w '%{http_code}' -r 0-1023 "$URL"        # GET+Range → 206 = ok
curl -s -o /dev/null -w '%{http_code}' "$URL"                  # 200 = ok
curl -s -o /dev/null -w '%{http_code}' "$URL_REMOVIDO"         # 404 = removido de verdade
```
**GET+Range, nunca HEAD.**

## 5. Verificação de conteúdo (não só status)

Build Pages demora 80–317 s. Poll deve esperar **marcador de conteúdo**, não só 200:
```bash
curl -s "$URL_INDEX_PODCAST" | grep -q "FLAG_NOVO"   # marcador único da nova versão
```
Arquivos removidos devem virar **404** antes de declarar sucesso.

## 6. Orçamento

```bash
.opencode/hooks/budget_guard.sh "$SITE"          # limite 1000 MiB (Pages), 25 MiB/arquivo
```
Rodar antes de push (gate fail-closed).

## 7. Guards já disponíveis (hooks desta frente SPEC-974)

```bash
.opencode/hooks/credential_guard.sh "$SITE"      # GRANTED/DENIED, token nunca impresso
.opencode/hooks/js_smoke_dom.sh --dir "$SITE"    # smoke DOM dos .html antes de publicar
.opencode/hooks/budget_guard.sh "$SITE"
```

## 8. Verificação final (checklist anti-overclaim)

- [ ] `git log --oneline -3` no site → commits com identidade correta
- [ ] Poll API: `status == "built"` E sem `error`
- [ ] GET+Range: áudios 206, páginas 200, removidos 404
- [ ] Marcador de conteúdo novo presente no servido
- [ ] Hash file local == hash do servido (se tamanho permitir)
- [ ] Registrar ciclo no EvolutionRegistry com as provas (URL, status, bytes)