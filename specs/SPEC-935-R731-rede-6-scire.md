# SPEC-935-R731 — Rede 5→6 com scir sob aceite GPL explícito

**Status:** `em implementação`
**Ciclo:** R731→R732
**Data:** 2026-10-07
**Base:** R728 (lote3 scir: 1 aprovada, readiness 1, minuta 1, parecer 5 + nota GPL) + aceite titular `aceito GPL do scir`

## 1. Problema

O scir tinha cadeia completa mas fedia à federação por copyleft sem aceite. O
titular agora aceita a GPL-3.0 nos termos da nota: referência/benchmark sem
contaminação; derivar código exigiria GPL. Falta registrar o aceite e estender
4→6 idempotente (lote4 já levou a 5).

## 2. Objetivo

Registrar `aceite_gpl.json` no lote3 (quando, responsável titular, escopo
referência sem derivação) e estender `workbench/rede_polimata` com
`polymath:lab:idiap-scir`, cadeia somada, escopo polimata, sem harness.

## 3. Critérios de aceitação

- [ ] AC1 — Aceite com ordem literal, escopo e vedação de derivação proprietária.
- [ ] AC2 — `nodos.json total 6`, `federados.json total 6`, idempotente.
- [ ] AC3 — Testes R724 verdes; `doctor` sem novos falhos.
- [ ] AC4 — Anti-overclaim mantido; nota GPL gravada no federado.

## 4. Fora de escopo

- R621, derivação de código, novas aprovações.

## 5. Verificação

- Merge auditado; `pytest` verde.
