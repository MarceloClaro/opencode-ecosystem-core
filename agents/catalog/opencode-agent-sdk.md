---
id: opencode-agent-sdk
name: opencode-agent-sdk
description: >-
  SDK de agente FREE local-first (SPEC-935-R649, R$ 0,00): query() com loop
  agêntico, @tool in-process, hooks e autodetect LiteRT-LM/Ollama/Colibri
  sobre HTTP OpenAI-compatível. Sem conta e sem cobrança.
type: integration
round: R649
spec: SPEC-935-R649-opencode-agent-sdk.md
trust: 0.9
---

# opencode-agent-sdk — SDK livre do Core

`integrations/opencode_agent_sdk.py`: espelho gratuito do `claude-agent-sdk`
(só stdlib no transporte). Tools executam localmente sob allowlist + hooks;
sem provedor local, falha explícita — nunca cobra.
