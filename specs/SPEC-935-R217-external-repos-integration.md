---
spec_id: SPEC-935-R217
title: "Integração de Repositórios de Referência: agent-eval, ai-agents-for-beginners e hello-agents"
component: integrations/external_repos.py, benchmarks/
test_file: tests/test_r217_external_repos.py
status: green
---

# SPEC-935-R217 — Integração de Repositórios de Avaliação e Aprendizado
========================================================================

## 1. Visão Geral
Esta especificação estabelece o plano de integração e sinergia entre o **OpenCode Ecosystem Core** e três repositórios de referência essenciais:

1. **`agent-eval`** (`https://github.com/MarceloClaro/agent-eval`): Harness de avaliação quantitativa de trajetórias, custos e TSR (Task Success Rate) para os agentes do catálogo.
2. **`ai-agents-for-beginners`** (`https://github.com/MarceloClaro/ai-agents-for-beginners`): Base de conhecimentos industriais, padrões de observabilidade e tutoriais de engenharia de agentes.
3. **`hello-agents`** (`https://github.com/MarceloClaro/hello-agents`): Implementação didática de princípios fundamentais (ReAct, Plan-and-Solve, Reflection) em Python puro sem dependências pesadas.

## 2. Benefícios Arquiteturais para o Ecossistema
- **Avaliação Contínua**: O `agent-eval` automatiza os testes de regressão de qualidade e latência de respostas do `ModelRouter` e do `ColibriProvider`.
- **Rigor Pedagógico**: O `hello-agents` fornece a implementação de referência para auditar a lógica dos 186+ `AgentCard`s de `agents/catalog/*.md`.
- **Documentação & Onboarding**: O `ai-agents-for-beginners` complementa o `MANUAL.md` e os notebooks acadêmicos com padrões industriais.
