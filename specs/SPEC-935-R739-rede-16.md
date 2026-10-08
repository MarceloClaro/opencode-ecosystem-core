# SPEC-935-R739 — Rede 14→16 com z3 + EvidenceSynthesis

**Status:** `em implementação`
**Ciclo:** R739→R740
**Data:** 2026-10-07
**Base:** R732 (z3 cadeia + override MIT) + R733 (evidence cadeia + override Apache) + ordem `estender 14→16`

## 1. Problema

A rede tem 14 nodos e dois lotes têm cadeia completa com override auditado.
Falta extensão 14→16 idempotente. A ordem sucinta segue o padrão das extensões
anteriores autorizadas; registra-se como autorização de registro.

## 2. Objetivo

Estender `workbench/rede_polimata` com `polymath:lab:z3prover-z3` e
`polymath:lab:ohdsi-evidencesynthesis`, cadeia somada, escopo polimata.

## 3. Critérios de aceitação

- [ ] AC1 — `nodos.json total 16`, `federados.json total 16`, idempotente.
- [ ] AC2 — Testes R724 verdes; `doctor` sem novos falhos.

## 4. Fora de escopo

- R621, novas aprovações, as 5 retidas.

## 5. Verificação

- Merge auditado (resultado: zero anexos, idempotente); `pytest` verde.

## 6. Errata (verificação 2026-10-07)

Premissa falsa: `z3 + EvidenceSynthesis` já constavam na rede desde R734
(`lote5_z3_lote6_evidence`). A fusão executada anexou zero — idempotência
comprovada e registrada como `lote5_lote6_z3_evidence: []`. Rede segue 14/14.
Caminho real para 16: `sympy` (re-executar readiness+minuta com override BSD
no piloto) + `reasonkit-core` (cadeia completa a construir). Nada foi
sobrescrito; a evolução R741 desta spec fica superscriptada por esta errata.
