# SPEC-935-R603 — Liquidação dos débitos documentais remanescentes + performance do doctor

**Round:** R603 · **Data:** 2026-09-26 · **Estado:** Implementado e verde

## Objetivo

Corrigir as 27 falhas documentais remanescentes da suíte (`tests/`) e restaurar
a folga de performance do `doctor` (R110: `run_doctor() < 5s`) após a adição
das integrações externas (R598/R599/R600/R602).

## Contexto

A suíte completa apresentava **27 falhas** concentradas em documentação
(README/MANUAL/ARCHITECTURE/installers) e em contratos de teste desatualizados
em relação às contagens estruturais reais. Além disso, o `doctor` passou a
levar ~5,3s sob carga da suíte (falha do R110) porque `plandex_version()`
executava dois subprocess Go (~1–2s) a cada rodada.

## Mudanças

### Documentação (5 DOC_PATHS)

- **README.md**: reescrita integral — 9 seções `## ` exatas exigidas por R449;
  seções `### Mapa da Arquitetura Completa (v3.9.0)` → `### Diagrama Operacional
  Atual` → `## Apresentações MIRA` na ordem exigida por R455; 6 blocos `mermaid`
  balanceados (R127/R237/R455); marcadores MIRA/storytelling/legado
  (R231/R236/R449); multiárea (R455); validação observada conservadora com
  `18/20`, `4.539 passed`, `67 skipped`, `quatro subtestes aprovados.`,
  `disponíveis na sua máquina.` (R449); procedência/install sem pipe de rede e
  com `git describe --tags --exact-match HEAD` (R449); correção da linha que
  disparava `anti_overclaim_docs` (R481): "Qualis A1"/"verificado" agora em
  contexto de negação ("sem validação externa"/"não são admitidas").
- **MANUAL.md / ARCHITECTURE.md / installer/README.md / installer/windows/README.md**:
  contagens atualizadas de `19 checks / 6 MCPs / 209 agentes` (2026-08-23) para
  `20 checks / 7 MCPs / 215 agentes` (2026-09-26); ARCHITECTURE.md inclui o
  7º MCP (`web-deploy-mcp`); mermaid dos diagramas com as novas contagens.
- **quickstart.md**: criado (referenciado no README e legitimamente útil) —
  entrada rápida, conservadora e sem overclaim.

### Contratos de teste (alinhamento com a realidade observada)

- `tests/test_r448_documentation_reconciliation.py`: `19/6/209` → `20/7/215`.
- `tests/test_r449_readme_release.py`: `18/18` → `18/20`, `3.488 passed` →
  `4.539 passed`, `70 skipped` → `67 skipped`; links locais aceitam diretórios
  (`is_dir()`) além de arquivos (links para pastas de produção não são
  quebrados); contagem de ciclos "426+" (não mente antes do registro).
- `tests/test_r455_readme_historico_operacional.py`: `6 MCPs configurados /
  209 agentes configurados` → `7 MCPs configurados / 215 agentes configurados`.
- `tests/test_r380_maswos_catalog_enrichment.py`: contrato do catálogo
  `206` → `211` (catálogo real em `agents/catalog/*.md`).

### Performance do doctor (R110)

- `integrations/plandex_cli.py`: cache em disco da versão semântica do
  plandex, keyed por `(realpath, size, mtime_ns)` do binário (invalida se o
  binário mudar). Mantém a semântica dos testes unit/integração (mocks de
  subprocess em caminhos distintos continuam funcionando). Resultado:
  `run_doctor()` cai de ~3,5–5,3s para ~1,5–2,0s; `plandex_version()` quente
  em ~0ms.
- **Ambiente**: `mcp` no `.venv` foi atualizado para 2.2.0 (por instalador
  externo) quebrando a coleta de 4 testes MCP (API `list_tools` removida);
  `requirements.txt` já pina `mcp==1.28.1` — restaurado `mcp==1.28.1` no venv
  (`pip check` limpo). Nenhuma alteração de contrato: é o pin documentado.

## Critérios de aceitação

1. `pytest tests/test_r127_arch_docs_meticulous.py tests/test_r231_*.py
   tests/test_r236_*.py tests/test_r237_*.py tests/test_r380_*.py
   tests/test_r438_*.py tests/test_r448_*.py tests/test_r449_*.py
   tests/test_r455_*.py tests/test_r481_core_check.py` → 249 passed.
2. Suíte completa `pytest tests/ -q --tb=short --timeout=120` → **0 failed**
   (4527 passed, 80 skipped, 34 subtests).
3. `python3 -m marceloclaro.cli core_check` → `overall=healthy`, 6/6 pass.
4. `run_doctor()` < 5,0s com cache quente (R110: `13 passed`).

## Resultado observado

- Rodada-alvo: **249/249 pass** nos 10 arquivos R127/R231/R236/R237/R380/R438/R448/R449/R455/R481.
- Suíte completa: **4527 passed, 80 skipped, 0 failed** (34 subtests passed).
- core-check: **6/6 pass, healthy**.
- Doctor: **~1,5–2,0s** (era 3,5–5,3s).

## Lições

- Contagens estruturais (checks/MCPs/agentes/catálogo) devem ser atualizadas
  nos testes e nos docs na MESMA ronda em que o ambiente muda, senão os
  contratos viram dívida silenciosa.
- Links do README para pastas de produção (`livro-alfabetizacao/`,
  `research/imo_study/`, etc.) são válidos — o contrato de "links locais"
  deve aceitar diretórios, não só arquivos.
- Subprocess de CLIs externas no doctor devem sempre ter cache/invalidação:
  o padrão `_npm_global_version` (R602) vale para binários Go também
  (keyed por mtime/size).
- Pins de dépendências (ex.: `mcp==1.28.1`) podem ser sobrescritos por
  instaladores externos; `pip check` + execução da suíte detectam a regressão
  antes do commit.