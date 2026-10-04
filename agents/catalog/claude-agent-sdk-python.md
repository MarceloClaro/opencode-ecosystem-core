---
id: claude-agent-sdk-python
name: claude-agent-sdk-python
description: >-
  Ponte do Claude Agent SDK Python (anthropics, MIT + Commercial Terms):
  query()/ClaudeSDKClient, in-process MCP, hooks; monta options sem executar.
type: integration
round: R647
spec: SPEC-935-R647-ecossistema-claude.md
trust: 0.9
---

# claude-agent-sdk-python — ponte de biblioteca

Ponte orquestrável (fork `MarceloClaro/claude-agent-sdk-python`):
`integrations/claude_agent_sdk.py` — presença do CLI `claude` + dep Python,
`build_query_options()` puro, doctor tolerante. Execução (faturável) pertence
ao operador.
