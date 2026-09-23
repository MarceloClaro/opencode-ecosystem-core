---
name: smoke-test-dom-js
description: Smoke test de JavaScript inline renderizado por DOM usando stub mínimo em Node. Use quando editar .html ou .js que manipula DOM (grids, cards, players, querySelector/appendChild), antes de declarar deploy ok. Detecta a classe de bug R580 ('num' sem ponto → querySelector null → TypeError que node --check NÃO pega). Não use para testar lógica pura sem DOM.
---

# Smoke Test DOM (stub em Node)

## Por que existe

Ciclo R580 (425): edição trocou `['.num','h3','.cap']` por `['num','h3','cap']` (sem ponto).
`node --check` passou — sintaxe válida. No browser `querySelector('num')` retorna null → TypeError → **os 26 episódios sumiram**. Só um stub de DOM com execução real pegou o bug.

## Como usar

```bash
.opencode/hooks/js_smoke_dom.sh ARQUIVO.html --assert-count 26
.opencode/hooks/js_smoke_dom.sh --dir DIR          # todos os *.html do repo
```

Exit 0 = `SMOKE_OK` (scripts executaram sem exceção de runtime).
Exit 1 = `SMOKE_FAIL` (exceção OU contagem de appendChild abaixo do esperado).

## O que o stub faz (ferramenta: `.opencode/hooks/smoke_dom_stub.js`)

1. Extrai blocos `<script>` sem `src` (regex).
2. **Espelha o DOM real**: ids/classes/tags presentes no HTML são resolvíveis; seletores
   inexistentes retornam **null** (como o browser).
3. Elementos `<audio>`/`<video>` expõem `paused/play/pause/volume/...`.
4. Conta `appendChild` no grid (detecta grid vazio).
5. Executa cada script com `vm.runInNewContext` (timeout 3 s; `fetch` bloqueado como no server).

## Detecção da classe R580

| Seletor real | HTML | stub retorna | resultado |
|---|---|---|---|
| `'.num'` (com ponto) | class="num" existe | elemento | OK |
| `'num'` (sem ponto) | tag `<num>` não existe | null | TypeError → FAIL |

## Boas práticas

- Rode **sempre** após editar JS inline de .html (post-edit), antes de push.
- Use `--assert-count N` quando o script povoar grid (N = nº esperado de cards).
- O hook `post-edit` do plugin `deploy-guards.ts` já dispara isso automaticamente em edições de .html/.js no ecossistema.
- Se o JS usa `fetch`, o stub retorna `{ok:false,status:599}` — código debe ter catch (fail-closed).