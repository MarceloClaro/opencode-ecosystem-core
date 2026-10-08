# SPEC-935-R742 — Painel auditado da rede polímata sem commit

**Status:** `em implementação`
**Ciclo:** R742→R743
**Data:** 2026-10-07
**Base:** R741 (rede 16/16 persistida; commit pendente de ordem explícita)

## 1. Problema

O estado da rede só existe em JSONs dispersos; titular e agentes não têm
leitura única com contagens, licenças, pendências e custódia. Commit exige
ordem explícita e não será executado aqui — entrega-se prévia auditada.

## 2. Objetivo

`workbench/polymath/DASHBOARD.md` gerado por script a partir dos JSONs
canônicos (nodos, federados, INDICE, proposta), com totais, tabela por lab
(licença, classe, parecer) e pendências; teste garante sincronia com os JSONs.

## 3. Critérios de aceitação

- [ ] AC1 — Totais do painel iguais aos JSONs (16/16, 5 retidas).
- [ ] AC2 — Cada federado lista licença e parecer quando existir.
- [ ] AC3 — Teste hermético de sincronia; `doctor` íntegro.
- [ ] AC4 — Nenhum commit executado; prévia `git status --short` anexada ao relato.

## 4. Fora de escopo

- Commit, push, R621.

## 5. Verificação

- Painel gerado; teste verde.
