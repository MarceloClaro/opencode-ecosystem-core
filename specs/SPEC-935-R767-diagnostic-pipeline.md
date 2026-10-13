---
spec_id: SPEC-935-R767
title: Pipeline de Diagnóstico por Gaps — Auditoria Hermética entre Artefatos
component: scanners/diagnostic_pipeline, tests/test_r767_diagnostic_pipeline
status: proposed
round_id: R767
test_file: tests/test_r767_diagnostic_pipeline.py
---

# SPEC-935-R767 — Pipeline de Diagnóstico por Gaps

## 1. Motivação

Revisões por gaps (R766) hoje são manuais. Este módulo automatiza a parte
mecânica de forma hermética: sem rede, subprocesso ou LLM. Não substitui
compilação Lean, execução de testes ou validação externa; encontra derivas
de sincronia (nomes, cobertura, tokens proibidos) antes delas virarem falha.

## 2. Requisitos

### R767.1 — `DiagnosticPipeline.varrer(plano: dict) -> dict`

Plano com duas checagens:

1. `{"tipo": "nomes", "id", "arquivo", "regex", "esperados": [...],
   "proibidos": [...]}` — extrai nomes via regex com 1 grupo; acusa
   faltantes, excedentes e ocorrências de padrões proibidos.
2. `{"tipo": "cobertura", "id", "arquivo", "regex", "referencia":
   {"arquivo", "regex"}}` — todo nome de A deve ocorrer em B.

Retorno: `{spec_id, gerador, total_checks, passaram, falharam,
gaps: [{id, motivo}], rotulo: candidato_a_inspecao, exige_validacao_externa:
True}`. Arquivo ausente ou ilegível vira gap (nunca exceção); plano malformado
levanta `ValueError` (fail-closed).

## 3. Aceite (`tests/test_r767_diagnostic_pipeline.py`, hermético, `tmp_path`)

1. Plano consistente → 0 gaps.
2. Nome esperado ausente → gap `faltante`.
3. Token proibido presente → gap `proibido`.
4. Nome sem cobertura → gap `cobertura`.
5. Plano malformado → `ValueError`.
6. Arquivo ausente → gap (sem exceção).

## 4. Invioláveis

- Sem rede, subprocesso, LLM ou import de terceiros além da stdlib.
- Rótulo sempre `candidato_a_inspecao`; nada é declarado verificado.
