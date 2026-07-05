# SPEC-010 — Pipeline Acadêmico MASWOS (Qualis A1)

```yaml
spec_id: SPEC-010
title: MASWOS — Multi-Agent Scientific Writing Orchestration System
module: academic/maswos.py
origin: OpenCode_Ecosystem MASWOS + SEEKER + AUTO_SCORE_QUALIS
status: implemented
```

## Objetivo

Produção científica real em 16 estágios (diagnóstico de escopo, busca SEEKER, estatística, redação IMRaD, referências ABNT, QA Qualis A1, entre outros), com **gate de qualidade AUTO_SCORE_QUALIS** que aprova apenas manuscritos com nota ≥ 8.0/10.

## Requisitos

| ID | Requisito | Critério de Aceitação |
|---|---|---|
| REQ-010.1 | O pipeline define exatamente 16 estágios canônicos | `len(MASWOS_STAGES) == 16` |
| REQ-010.2 | Sem `delegate_fn`, opera em dry-run (estágios `skipped`) | `run()` sem delegação marca todos como skipped |
| REQ-010.3 | Com `delegate_fn`, estágios selecionados são executados por agentes reais via Blackboard | estágios `completed` |
| REQ-010.4 | AUTO_SCORE avalia o manuscrito (estrutura, estatística, referências, originalidade) em 0–10 | `final_score` presente; `approved = score >= 8.0` |
| REQ-010.5 | Manuscritos rasos são reprovados no gate | texto sem estrutura ⇒ `approved is False` |

## Invariantes

- INV-010.1: O gate nunca aprova manuscrito vazio.
- INV-010.2: Cada execução registra reflexão na memória metacognitiva global (via `orchestrator.academic_pipeline`).

## Testes

`tests/test_advanced_subsystems.py::TestMaswos` (3 testes).
