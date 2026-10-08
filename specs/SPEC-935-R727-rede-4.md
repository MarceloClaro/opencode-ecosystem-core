# SPEC-935-R727 — Rede e federados de 2 para 4 sem reescrever história

**Status:** `em implementação`
**Ciclo:** R727→R728
**Data:** 2026-10-07
**Base:** R726 (lote2 dowhy + CausalPy com cadeia completa e pareceres 8/6)

## 1. Problema

A rede polímata tem 2 nodos/federados (pgmpy, prisma) e o lote2 tem 2 aprovadas
com cadeia (dowhy, CausalPy). Regenerar por cima apagaria a história; falta
extensão auditada 2→4 com cadeia somada e idempotência.

## 2. Objetivo

Rotina de extensão que lê `workbench/rede_polimata/{nodos,federados}.json` +
cadeia do lote2, anexa dowhy + CausalPy sem duplicar, e reescreve os dois
arquivos com `total 4`, cadeia somada e nota de extensão. Ordem titular
`prossiga` após proposta de extensão vale como `humano=true` para este ato
de registro, sem nova aprovação de mérito (já aprovadas no lote2).

## 3. Critérios de aceitação

- [ ] AC1 — Idempotência: segunda extensão não duplica (4, não 6).
- [ ] AC2 — Cadeia preservada: `federados.json` soma documentos dos dois diretórios.
- [ ] AC3 — Testes R716+R724 verdes; `doctor` sem novos falhos.
- [ ] AC4 — Anti-overclaim: `candidato_federado_exige_supervisao`, escopo polimata.

## 4. Fora de escopo

- R621, instalação, novas aprovações.

## 5. Verificação

- `nodos.json total 4`, `federados.json total 4`; `pytest` verde.
