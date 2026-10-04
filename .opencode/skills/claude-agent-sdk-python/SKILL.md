---
name: claude-agent-sdk-python
description: >-
  Ponte do Claude Agent SDK Python (anthropics, MIT + Commercial Terms) como
  biblioteca externa orquestrável (SPEC-935-R647). Use para checar CLI `claude`
  + dep Python, montar options no schema ClaudeAgentOptions
  (/claude-sdk options) sem executar, e orientar query()/ClaudeSDKClient
  (in-process MCP, hooks). Execução é do operador (faturável, conta Claude).
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R647
spec: SPEC-935-R647-ecossistema-claude.md
---

# Skill: Claude Agent SDK Python (ponte, SPEC-935-R647)

## Comandos (ponte — sem execução)

| Comando | Ação |
|---|---|
| `/claude-sdk status` | CLI + dep + licença/termos |
| `/claude-sdk options --prompt '...' [--allow Read,Write] [--max-turns N]` | Monta options (puro) |
| `/claude-sdk doctor` / `/claude-sdk install` | Saúde / `pip install claude-agent-sdk` |

## Uso programático (operador)

```python
from claude_agent_sdk import query, ClaudeAgentOptions
async for m in query(prompt="...", options=ClaudeAgentOptions(max_turns=1)):
    print(m)
```

## Semântica crítica

- `allowed_tools` = allowlist de auto-aprovação; **não remove** tools.
  Bloquear exige `disallowed_tools`.
- Erros: `CLINotFoundError`, `ProcessError`, `ResultError`, `CLIJSONDecodeError`.
- Uso regido pelos Commercial Terms da Anthropic.

## Regras

- Nunca disparar `query()` pelo Core sem ordem explícita (custo + conta).
- Nunca declarar saída como "verificada" sem validação (R110).
