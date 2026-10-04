---
name: colab-mcp
description: >-
  Ponte do Colab MCP Server (googlecolab/colab-mcp) como ferramenta
  orquestrável (SPEC-935-R645). Use para codificação assistida interativa
  dentro do notebook Colab (complemento do fluxo terminal do colab-cli):
  checar presença (binário ou uvx), emitir config stdio para opencode.json
  e orientar registro. Não executa o protocolo MCP; credenciais do notebook
  pertencem ao operador.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R645
spec: SPEC-935-R645-colab-cli-mcp.md
---

# Skill: Colab MCP Server (SPEC-935-R645)

Ponte orquestrável. O orquestrador deve ler este SKILL.md e executar as
instruções no contexto atual.

## Comandos

| Comando | Ação |
|---|---|
| `/colab-mcp status` | JSON com presença (binário/uvx), versão e origem |
| `/colab-mcp config [--no-uvx]` | Snippet stdio `{"colab-mcp": {...}}` para `opencode.json` |
| `/colab-mcp doctor` | Saúde (pass/warn, nunca fail) |
| `/colab-mcp install` | Uso via `uvx colab-mcp` ou `pip install colab-mcp` |

## Uso programático

```python
from integrations.colab_mcp import mcp_available, mcp_config, doctor_check

mcp_available()          # True se `colab-mcp` ou `uvx` no PATH
mcp_config()             # {"type": "local", "command": ["uvx", "colab-mcp"], ...}
doctor_check()           # {"name": "colab-mcp", "status": ..., "detail": ...}
```

## Regras

- Complemento do `colab-cli` (terminal/headless), não substituto.
- `mcp_version()` nunca faz download: sem binário local retorna None mesmo
  com `uvx` presente (evita rede implícita no doctor).
- Nunca declarar ferramentas do notebook como "verificadas" sem validação (R110).
