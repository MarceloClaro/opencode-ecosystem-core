# Evo-45 — R143: Reconciliação da árvore de trabalho (overlay stale descartado)

## Contexto

Após entregar o R142, a suíte na **árvore de trabalho** apresentava ~90
falhas (test_r131, test_r137, test_r125, etc.), enquanto o **HEAD** estava
verde (baseline 1411 passed) e o **estado do commit R142** também (1427
passed em worktree isolado). A divergência vinha inteiramente de mudanças
**não commitadas** na árvore de trabalho.

## Diagnóstico

As mudanças rastreadas não eram trabalho novo — eram um **snapshot antigo
(era ~R108–R112) sobreposto ao HEAD**. Evidências conclusivas:

- `README.md` exibia badges antigos: "1062 testes", "65 ciclos" (o HEAD
  está em ~1411 testes / 100 ciclos).
- `trust/trust_engine.py` **removia** o `GoalDriftDetector` (R112).
- `marceloclaro/cli.py` **removia** os menus Ajuda/Helpdesk/Pesquisa/MIRA
  (R116/R125/R128).
- `mci/mcp_server.py` **removia** o handshake `initialize` do MCP.
- `marceloclaro/orchestrator.py` perdia 603 linhas.
- `integrations/opencode_cli.py` revertia o slug-keying (R137) e os
  providers/comandos (R138); `marceloclaro/catalog_loader.py` revertia a
  extração de descrição.
- Diffstat total: **445 inserções / 3118 deleções** em 43 arquivos —
  direção esmagadora de remoção de features já commitadas.

## Ação

Descarte **recuperável** via `git stash` (não `git checkout` destrutivo):
o overlay stale ficou salvo em `stash@{0}` caso algo precise ser resgatado,
e a árvore rastreada voltou a ser idêntica ao HEAD (R142). O conteúdo do
usuário **não-rastreado** (projetos/, PDFs, `.env`) foi preservado — o
stash sem `-u` não toca em untracked.

## Verificação

- `opencode.json` reproduzível: regenerar = no-op (174 agentes).
- `test_r137` + `test_opencode_go_zen` (SPEC-108): 42 passed.
- Suíte completa na árvore principal: **1433 passed, 5 skipped, 0 falhas**.

## Recuperar o overlay (se algum dia necessário)

```bash
git stash list                 # localizar o stash R143
git stash show -p stash@{0}     # inspecionar o conteúdo
git stash apply stash@{0}       # reaplicar (NÃO recomendado — reverteria o HEAD)
```

Nada de valor foi perdido: o overlay só continha reversões de ciclos já
commitados. Registrado por transparência, não por necessidade.
