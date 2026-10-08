# SPEC-935-R730 — Rede e federados de 4 para 5 com aweai

**Status:** `em implementação`
**Ciclo:** R730→R731
**Data:** 2026-10-07
**Base:** R729 (lote4 aweai: 1 aprovada, readiness 1, minuta 1, parecer 9 sem riscos)

## 1. Problema

A rede tem 4 nodos e o lote4 tem 1 aprovada com cadeia limpa MIT. Falta extensão
4→5 idempotente. O scir segue fora por aceite GPL pendente — genérico não aceita
copyleft.

## 2. Objetivo

Estender `workbench/rede_polimata` com `polymath:lab:aweai-team-aiscientist`
via merge idempotente, cadeia somada, escopo polimata, sem harness.

## 3. Critérios de aceitação

- [ ] AC1 — `nodos.json total 5`, `federados.json total 5`, sem duplicar em repetição.
- [ ] AC2 — Testes R724 verdes; `doctor` sem novos falhos.
- [ ] AC3 — Anti-overclaim: `candidato_federado_exige_supervisao`.

## 4. Fora de escopo

- R621, GPL, decisão nova.

## 5. Verificação

- Merge auditado com ids; `pytest` verde.
