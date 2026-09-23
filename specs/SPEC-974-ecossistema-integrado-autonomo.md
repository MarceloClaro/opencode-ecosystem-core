# SPEC-974 — Ecossistema Integrado, Autônomo e Metacognitivamente Robusto

**Status:** Aprovado (gate SDD aplicado)
**Ciclos de referência:** R569–R580 (375–425) — lições da sessão Molambudos/GitHub Pages
**Ciclo desta frente:** R581+ (426+)
**Responsável:** orquestrador `marceloclaro`

## 1. Contexto e justificativa

A sessão de publicação do site do podcast Molambudos (SPEC-973) expôs 12 falhas reais,
repetíveis e *não capturadas* por nenhum guard do ecossistema. Entre elas:

1. Extração incorreta de token do `~/.git-credentials` → 401 (R574).
2. Identidade git ausente em repo externo → falha de commit (R571/R574).
3. `HEAD` falha no GitHub Pages para `podcast_R550.m4a` enquanto `GET` funciona (R571).
4. Raiz `/` é redirect meta-refresh de 769 bytes — verificação enganosa de conteúdo (R573).
5. Build Pages demora 80–317 s — poll ingênuo confunde pasta antiga com nova (R570/R571).
6. `node --check` passa mas `querySelector('num')` retorna null e os 26 episódios somem (R580).
7. Falta do `.` (seletor) → TypeError em runtime não detectado por checagem sintática (R580).
8. ffmpeg morto por timeout no meio da escrita → arquivo corrompido; mv atômico ausente (R569).
9. `xargs` com `/dev/stdin` tratou args como nomes de arquivo (R569).
10. Uso de `cd`/`$PWD` em vez de caminho absoluto com `GIT_DIR`/`GIT_WORK_TREE` (R571+).
11. Olhos do orquestrador não enxergam imagem (design validado por filenames/luminância).
12. `semantic_lessons` do MetaBus **vazia** — reflexões episódicas não viraram lições pesquisáveis.

**Objetivo:** fechar essas crateras com hooks, skills, MCPs e plugins — integração,
automação e metacognição real, medidos por testes (TDD) e prova física.

## 2. Escopo (entregas)

| ID | Entrega | Critério de aceitação |
|---|---|---|
| E1 | Lições semânticas R569–R580 no MetaBus | `semantic` no `shared_memory.json` com ≥12 lições; consultáveis por tópico |
| E2 | Hook `credential-guard` | script bash + plugin gate; verifica `~/.git-credentials` (sem imprimir segredo), injeta identidade em repo externo; retorna 0/1 testável |
| E3 | Hook `js-smoke` (DOM stub Node) | script bash + plugin gate; extrai `<script>` de `.html` e roda stub DOM; falha detecta bug da classe R580 |
| E4 | Hook `budget-guard` | calcula peso de árvore (excl. `.git`), lista maiores arquivos, bloqueia >1 GB e >25 MiB/arquivo |
| E5 | Skill `deploy-estatico-github-pages` | SKILL.md com receita validada R569–R580 (api, token, verificação de conteúdo real) |
| E6 | Skill `smoke-test-dom-js` | SKILL.md com stub DOM reproduzível (bug `'num'` vs `'.num'`) |
| E7 | MCP `web-deploy-mcp` | servidor stdio (padrão litert); tools: `pages_status`, `probe_url` (GET+Range, nunca HEAD), `site_weight`, `validate_feed`, `assert_gone`; testes hermético |
| E8 | Config regenerada | `opencode.json` com `web-deploy-mcp`; `skills.paths` preservado; `plugins/` auto-descobertos |
| E9 | Registro de evolução | ciclo R581 (426) registrado com score e lições |

## 3. Regras de não-regressão

- Nenhuma entrega sem teste pythônico em `tests/` (quando aplicável) ou prova física do script.
- MCP `fail-closed`: erro de rede/credencial → resposta `isError` explícita, nunca `None` silencioso.
- Segredos: token nunca é impresso; guard imprime apenas `GRANTED`/`DENIED` + motivo.
- O `web-deploy-mcp` herda o padrão SPEC-970/971/972 (runner injetável, fail-closed, recibo).

## 4. Verificação final (gate)

```bash
python3 -m pytest tests/test_r581_web_deploy_mcp.py -q        # testes novos
python3 -m marceloclaro.cli doctor                             # saúde geral
.opencode/hooks/js_smoke_dom.sh <GH>/index_podcast.html        # smoke no HTML real
.opencode/hooks/budget_guard.sh <GH>                           # peso real
```

## 5. Lições esperadas

- Guard perto do erro (pre-commit/pre-edit) é mais barato que verificação pós-deploy.
- Stub de DOM converte bug de runtime em falha de CI (R580 vira teste).
- Metacognição exige lições semânticas consultáveis, não só reflexões episódicas.