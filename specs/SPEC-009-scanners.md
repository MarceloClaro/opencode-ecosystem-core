# SPEC-009 — Pipeline de Scanners de Diagnóstico

```yaml
spec_id: SPEC-009
title: Pipeline de Diagnóstico — 5 Scanners
module: scanners/pipeline.py
origin: OpenCode_Ecosystem skills/system/academic-audit/*_scanner.py
status: implemented
```

## Objetivo

Executar diagnóstico integral de corpora (código, manuscritos, ecossistemas) com os cinco scanners portados: **Noológico** (estrutura de conhecimento), **Teleológico** (alinhamento a objetivos), **Evolutivo** (lacunas e recomendação), **Potentiality** (potenciais latentes) e **Social Impact** (impacto social).

## Requisitos

| ID | Requisito | Critério de Aceitação |
|---|---|---|
| REQ-009.1 | `run(corpus, domain, goals)` executa os 5 scanners e agrega em um relatório único | chaves `noological`, `teleological`, `potentiality`, `evolutionary` presentes |
| REQ-009.2 | O scanner evolutivo emite `total_gaps` e `recommendation` | presentes em todo relatório |
| REQ-009.3 | Degradação graciosa com corpus vazio | `run("")` não lança exceção |
| REQ-009.4 | Integração metacognitiva: `orchestrator.diagnose()` registra reflexão na memória global | memória episódica cresce após diagnose |

## Invariantes

- INV-009.1: Falha de um scanner individual não derruba o pipeline (isolamento por seção).
- INV-009.2: O score da reflexão decresce com o número de lacunas (1.0 − gaps/10).

## Testes

`tests/test_advanced_subsystems.py::TestDiagnosticPipeline` (2 testes) + `TestOrchestratorIntegration::test_diagnose_records_reflection`.
