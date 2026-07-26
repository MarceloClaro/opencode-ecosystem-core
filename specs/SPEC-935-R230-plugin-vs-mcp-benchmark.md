---
spec_id: SPEC-935-R230
title: "Benchmark Comparativo de Eficiência: Plugins In-Process vs MCP Protocol"
component: benchmarks/plugin_vs_mcp_eval.py
test_file: tests/test_r230_plugin_vs_mcp_eval.py
status: green
---

# SPEC-935-R230 — Benchmark Comparativo: Plugins In-Process vs Servidores MCP
=============================================================================

## 1. Visão Geral
Esta especificação provê o harness de avaliação de desempenho comparativo **`PluginVsMcpBenchmark`** para mensurar de forma empírica a latência (ms), segurança de processo e consumo de memória entre a execução embutida de Plugins (in-process) e a execução via protocolo MCP (IPC/stdio).

## 2. Requisitos Funcionais
- **Classe `PluginVsMcpBenchmark`**:
  - `evaluate_execution_overhead(iterations: int = 50) -> Dict[str, Any]`
  - Medição de tempo de resposta em milissegundos para Plugins embutidos vs Servidores MCP.
  - Análise de isolamento e segurança contra exceções e travamentos de processo.
