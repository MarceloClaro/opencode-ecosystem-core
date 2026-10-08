# SPEC-935-R734 — Rede 6→8 com z3 + EvidenceSynthesis sob autorização

**Status:** `em implementação`
**Ciclo:** R734→R735
**Data:** 2026-10-07
**Base:** R732 (z3 cadeia + override MIT) + R733 (evidence cadeia + override Apache) + autorização titular `estender rede 6→8`

## 1. Problema

A rede tem 6 nodos e dois lotes têm cadeia completa com override (z3 MIT,
EvidenceSynthesis Apache). Falta extensão 6→8 idempotente sob autorização.

## 2. Objetivo

Estender `workbench/rede_polimata` com `polymath:lab:z3prover-z3` e
`polymath:lab:ohdsi-evidencesynthesis` via merge idempotente, cadeia somada,
escopo polimata, sem harness.

## 3. Critérios de aceitação

- [ ] AC1 — `nodos.json total 8`, `federados.json total 8`, sem duplicar.
- [ ] AC2 — Autorização registrada com ordem literal.
- [ ] AC3 — Testes R724 verdes; `doctor` sem novos falhos.

## 4. Fora de escopo

- R621, novas aprovações, GPL.

## 5. Verificação

- Merge auditado; `pytest` verde.
