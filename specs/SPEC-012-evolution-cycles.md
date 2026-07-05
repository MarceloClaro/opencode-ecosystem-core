# SPEC-012 — Ciclos Evolutivos (R1–R46 → R47+)

```yaml
spec_id: SPEC-012
title: Registro de Ciclos Evolutivos com Scores
module: evolution/cycles.py
origin: OpenCode_Ecosystem evolution/evo-*.md (R1 a R46)
status: implemented
```

## Objetivo

Preservar a história evolutiva documentada do ecossistema original (rounds R1–R46 com scores) e continuar o registro de novos ciclos a partir de **R47**, injetando lições aprendidas na memória metacognitiva global.

## Requisitos

| ID | Requisito | Critério de Aceitação |
|---|---|---|
| REQ-012.1 | Numeração contínua a partir de R47 | primeiro `record()` ⇒ `R47`, segundo ⇒ `R48` |
| REQ-012.2 | Ciclos documentados do original indexáveis | `load_documented_cycles()` ≥ 10 documentos |
| REQ-012.3 | Score médio calculável sobre os ciclos registrados | `average_score()` correto |
| REQ-012.4 | Lições de cada ciclo viram reflexões na memória global | `orchestrator.record_evolution(lessons=[...])` incrementa memória episódica |
| REQ-012.5 | Persistência em JSON entre execuções | `cycles.json` regravado a cada record |

## Invariantes

- INV-012.1: round_id é único e monotônico.
- INV-012.2: O registro nunca sobrescreve a história documentada (evo-*.md são somente leitura).

## Testes

`tests/test_advanced_subsystems.py::TestEvolution` (2 testes).
