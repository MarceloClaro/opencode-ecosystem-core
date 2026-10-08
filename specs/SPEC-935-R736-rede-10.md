# SPEC-935-R736 — Rede 8→10 com trAIce + repro_audit sob autorização

**Status:** `em implementação`
**Ciclo:** R736→R737
**Data:** 2026-10-07
**Base:** R735 (lote7 parecer 4 + lote8 parecer 8) + autorização titular

## 1. Problema

A rede tem 8 nodos e dois lotes têm cadeia limpa MIT sem pendência jurídica.
Falta extensão 8→10 idempotente.

## 2. Objetivo

Estender `workbench/rede_polimata` com `polymath:lab:cqh4046-prisma-traice` e
`polymath:lab:aqibrahimbt-repro-audit`, cadeia somada, escopo polimata.

## 3. Critérios de aceitação

- [ ] AC1 — `nodos.json total 10`, `federados.json total 10`, idempotente.
- [ ] AC2 — Testes R724 verdes; `doctor` sem novos falhos.

## 4. Fora de escopo

- R621, novas aprovações.

## 5. Verificação

- Merge auditado; `pytest` verde.
