---
spec_id: SPEC-935-R219
title: "Agent Evaluation & Trajectory Benchmark Harness (Agent-Eval)"
component: benchmarks/agent_eval_harness.py
test_file: tests/test_r219_agent_eval_harness.py
status: green
---

# SPEC-935-R219 — Agent Evaluation & Trajectory Benchmark Harness
===================================================================

## 1. Visão Geral
Esta especificação introduz a infraestrutura de avaliação quantitativa de agentes de IA inspirada no **`agent-eval`** e nos benchmarks industriais da NVIDIA.

## 2. Requisitos Funcionais
- **Métricas de Desempenho**:
  - `TSR` (Task Success Rate - Taxa de Sucesso em %): Calculado via especificação SDD.
  - `Tool Accuracy` (Precisão na Execução de Ferramentas em %): Rastreamento de acertos/erros de comandos.
  - `Trajectory Efficiency`: Estatísticas de percentis (P50, P90, P99) para latência e contagem de tokens por turno.
- **Interface da Classe `AgentEvalHarness`**:
  - `evaluate_agent(agent_id: str, test_tasks: List[Dict[str, Any]]) -> Dict[str, Any]`
  - `generate_benchmark_report() -> Dict[str, Any]`
