# SPEC-935-R738 — Rede 10→14 com as 4 MIT sob autorização

**Status:** `em implementação`
**Ciclo:** R738→R739
**Data:** 2026-10-07
**Base:** R737 (lote9: 4 aprovadas, readiness 4, minuta 4, pareceres, MIT em API+arquivo+sha) + autorização titular

## 1. Problema

A rede tem 10 nodos e o lote9 tem 4 aprovadas com cadeia limpa MIT. Falta
extensão 10→14 idempotente.

## 2. Objetivo

Estender `workbench/rede_polimata` com os 4 labs, cadeia somada, escopo
polimata, sem harness.

## 3. Critérios de aceitação

- [ ] AC1 — `nodos.json total 14`, `federados.json total 14`, idempotente.
- [ ] AC2 — Testes R724 verdes; `doctor` sem novos falhos.

## 4. Fora de escopo

- R621, novas aprovações, as 5 retidas.

## 5. Verificação

- Merge auditado; `pytest` verde.
