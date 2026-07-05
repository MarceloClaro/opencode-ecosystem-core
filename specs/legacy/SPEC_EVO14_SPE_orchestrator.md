# SPEC_EVO14_SPE_ORCHESTRATOR -- Agents Orchestrator Engine v1.0

**Domain**: agency-agents/specialized/agents-orchestrator
**Python**: 3.12, stdlib only
**Status**: Draft

---

## CT-01: Pipeline Happy Path
Todas as tarefas executam e passam sem retry. Estado final: todas PASSED, complete=True.

## CT-02: Retry Logic
Tarefa falha 2 vezes e passa na 3a tentativa (max_retries=3). retry_count=2, state=PASSED.

## CT-03: Max Retries Exceeded
Tarefa com max_retries=2 falha permanentemente. state=FAILED, can_retry=False.

## CT-04: Status Report
Relatorio reflete estado real: passed=1, failed=1, pending=1, current_stage=0, complete=False.

---

## Implementation
- `scripts/orchestrator_engine.py`: Pipeline, Stage, Task, TaskState
- `tests/test_orchestrator.py`: 4 CTs via pytest
