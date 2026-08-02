<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

---
name: Eval Runner
description: Test harness for evaluation framework - DO NOT USE DIRECTLY
version: '1.0.0'
skills:
- id: test-harness-for-evaluation
  name: Test harness for evaluation framework - do not use directly
  description: >-
    Capacidade especializada em test harness for evaluation framework - do not use directly
  tags: [test, harness, evaluation, framework]
  examples: [Aplique test harness for evaluation neste contexto, Avalie usando test harness for evaluation]
tags: [directly, eval runner, evaluation, framework, harness, test, testing, utility]
examples: [Execute esta tarefa conforme especificação, Analise e reporte os resultados, Aplique test harness for evaluation neste contexto]
mode: subagent
temperature: 0.2
type: utility
category: testing
---

# Eval Runner - Test Harness

**⚠️ DO NOT USE THIS AGENT DIRECTLY ⚠️**

This agent is a test harness used by the OpenCode evaluation framework.

## Purpose

This file is **dynamically replaced** during test runs:
- Before tests: Replaced with target agent's prompt (e.g., openagent, opencoder)
- During tests: Acts as the target agent
- After tests: Restored to this default state

## Configuration

- **ID**: eval-runner
- **Mode**: subagent (test harness only)
- **Status**: Template - will be overwritten during test runs

If you see this prompt during a test run, something went wrong with the test setup.
