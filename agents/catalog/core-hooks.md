---
id: core-hooks
name: core-hooks
description: >-
  Hooks do Core (SPEC-935-R653): engine fail-closed (HookMatcher, eventos
  Pre/PostToolUse e sessão) + política deny-list auditada para Bash, fiada
  ao SDK livre.
type: integration
round: R653
spec: SPEC-935-R653-core-hooks.md
trust: 0.9
---

# core-hooks — engine + política do Core

`hooks/engine.py` (roteamento, primeiro deny vence, exceção nega) e
`hooks/policy.py` (7 regras destrutivas/exfiltradoras + auditoria JSONL
fora do repo). Fiado em `opencode_agent_sdk` via chave `matchers`.
