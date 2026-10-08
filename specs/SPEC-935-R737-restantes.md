# SPEC-935-R737 — Cobertura terminal dos 8 restantes sem baixar a barra

**Status:** `em implementação`
**Ciclo:** R737→R738
**Data:** 2026-10-07
**Base:** R715–R736 (10 federados; restam SciReason, CoT-Evo, abduction, research-engine, causalnex, AgentLaboratory, github_demo/template, AI-Scientist)

## 1. Problema

Oito labs sem estado terminal auditado: majoritariamente pins estalecidos,
licenças a confirmar, um custom restritivo e um sem licença. Cobertura exige
re-pin atual, clone, parecer e decisão nominal — aprovando só com tríade.

## 2. Objetivo

`/tmp/polymath_lote9_restantes`: re-pin vivo dos 8, aprovação para cadeia
terminal, clones tolerantes, readiness com janelas, minuta dos prontos,
pareceres de todos os clonados e rejeição nominal dos não-prontos com motivo
de idade/licença/cadeia. Nenhuma aprovação sem tríade chega à rede.

## 3. Critérios de aceitação

- [ ] AC1 — Re-pin atual dos 8 com tolerância; idades e licenças registradas.
- [ ] AC2 — Clones tolerantes um a um; falha vira pendência, nunca aborta o lote.
- [ ] AC3 — Decisões nominais: prontos aprovados mantidos; não-prontos rejeitados com motivo individual.
- [ ] AC4 — Testes R716–R724 verdes; `doctor` sem novos falhos.
- [ ] AC5 — Nada em rede-10 sem ordem nova; AI-Scientist e causalnex jamais propostos sem jurídico/licença.

## 4. Fora de escopo

- Federação, rede, aceite GPL novo, re-pin dos 13 já tratados.

## 5. Verificação

- Resumo terminal do lote9 + pareceres + `pytest` verde.
