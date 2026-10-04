---
name: minizinc-mcp
description: >-
  Ponte do MiniZinc Constraint Solver MCP Server (r33drichards/minizinc-mcp,
  MIT) como ferramenta orquestrável (SPEC-935-R646). Use para modelar e
  despachar problemas CSP/COP (4-Queens, knapsack, scheduling) via tool
  solve_constraint: montar payloads, checar solver MiniZinc + deps Python,
  emitir config stdio/SSE e orientar uso hospedado, local ou Docker.
  Não resolve modelos no Core; resolução é externa.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R646
spec: SPEC-935-R646-minizinc-mcp.md
---

# Skill: MiniZinc MCP (SPEC-935-R646)

Ponte orquestrável. O orquestrador deve ler este SKILL.md e executar as
instruções no contexto atual.

## Comandos

| Comando | Ação |
|---|---|
| `/minizinc status` | JSON com solver, versão, deps Python e SSE hospedado |
| `/minizinc config [--hosted]` | Snippet stdio local ou JSON com URL SSE |
| `/minizinc payload --model-text '...' \| --model-file M [--data-json '{...}'] [--solver gecode] [--all] [--timeout SEG]` | Monta payload ConstraintModel (puro, sem rede) |
| `/minizinc solvers` | Lista solvers (requer binário `minizinc`) |
| `/minizinc doctor` | Saúde (pass/warn, nunca fail) |
| `/minizinc install` | Pré-requisitos + pip + Docker + SSE + Claude |

## Uso programático

```python
from integrations.minizinc_mcp import build_solve_payload, mcp_config, hosted_sse

payload = build_solve_payload("var 1..4: q; solve satisfy;", solver="gecode", timeout=30)
mcp_config()   # {"type": "local", "command": [...], "enabled": True}
hosted_sse()   # "https://minizinc-mcp.up.railway.app/sse"
```

## Execução real (adendo R651, provada ao vivo)

```python
from integrations.minizinc_mcp import solve_via_server  # protocolo MCP stdio
r = solve_via_server("var 1..10: x; ...", server_dir="/caminho/do/servidor")
# {"ok": True, "result": {"status": "SATISFIED", "solutions": [...]}}
```

Exige o checkout do servidor (`MINIZINC_MCP_DIR` ou `server_dir`) + solver.

## Modos de execução (operador)

1. **SSE hospedado** (sem instalar): registrar a URL no Claude Connectors ou
   `claude mcp add minizinc -t sse <URL>`.
2. **Local**: `pip install -r requirements.txt && python main.py` (Python 3.11+,
   MiniZinc 2.8+).
3. **Docker**: `docker build -t minizinc-mcp . && docker run -p 8000:8000 minizinc-mcp`.

## Regras

- O Core monta payloads; a resolução (`gecode` etc.) é externa.
- Nunca declarar soluções como "ótimas/verificadas" sem validar `status`
  (`OPTIMAL`, `SATISFIED`, ...) retornado pelo servidor.
- Sem sondagem de rede no doctor; SSE é constante documentada.
