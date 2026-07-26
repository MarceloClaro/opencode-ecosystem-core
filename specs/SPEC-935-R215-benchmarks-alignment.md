---
spec_id: SPEC-935-R215
title: "Mapeamento e Alinhamento com Frameworks e Benchmarks de Agentes SOTA (MAF, NVIDIA Agent-Eval, LangGraph)"
component: mci/metacognitive_evaluator.py, trust/trust_engine.py, sdd/spec_engine.py
test_file: tests/test_r215_benchmarks_alignment.py
status: green
---

# SPEC-935-R215 — Alinhamento de Avaliação e Orquestração Multi-Agente SOTA
=============================================================================

## 1. Visão Geral
Esta especificação formaliza o alinhamento arquitetural do **OpenCode Ecosystem Core** com os frameworks e benchmarks de avaliação de agentes de estado da arte (SOTA) da indústria (NVIDIA Agent Evaluation, MAF, Agent-eval, LangGraph e Research-Agent).

## 2. Dimensões de Avaliação e Alinhamento

### A. Métricas de Avaliação de Agentes (NVIDIA Agent-Eval & Agent-eval)
- **TSR (Task Success Rate)**: Medido pelo `SpecVerifier` em `sdd/spec_engine.py` através da transição determinística RED → GREEN.
- **Precisão nas Chamadas de Ferramentas (Tool Call Accuracy)**: Verificado pelo `TrustEngine` (`trust/trust_engine.py`) com pontuação comportamental baseada em acertos e falhas.
- **Eficiência da Trajetória & Custos**: Monitorado via `LLMReductionEngine` e `MetaBus` para otimização do consumo de tokens e latência.

### B. Padrões de Orquestração Multi-Agente (MAF, LangGraph & AutoGen)
- **Checkpoint & Breakpoint Resume**: Suportado no Blackboard A2A e no registro de sessões persistentes.
- **Intervenção Humana no Fluxo (Human-in-the-loop)**: Garantido via política `permission: ask` no `opencode.json`.
- **Re-planejamento Dinâmico em Lacunas de Conhecimento**: Alinhado com o `Research-Agent` para busca paralela de fontes e auto-refinamento.

### C. Transparência Ecológica e Autocorreção (CORRIGENDUM & Hello-Agents)
- **Política Anti-Overclaim**: Verificada pelo `classify_metacognitive_tier` (`mci/metacognitive_evaluator.py`) e auditada pelo `CORRIGENDUM.md`.
- **Verificação de Saúde**: Diagnóstico instantâneo executado pelo `python3 -m marceloclaro.cli doctor`.
