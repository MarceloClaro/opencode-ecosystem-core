---
name: awesome-mcp-servers
description: >-
  Curadoria executável da lista wong2/awesome-mcp-servers (SPEC-935-R652).
  Política referência-primeiro: servidores modelcontextprotocol sem auth
  (fetch, sequential-thinking, filesystem) já registrados no opencode.json;
  SaaS com API key só caso a caso com trust gate. Use para receitas de
  instalação (uvx/npx) e para decidir o que federar.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R652
spec: SPEC-935-R652-awesome-mcp-servers.md
---

# Skill: Awesome MCP Servers (SPEC-935-R652)

## Já registrados (provados ao vivo em 2026-10-04)

| MCP | Comando | Prova |
|---|---|---|
| `fetch` | `uvx mcp-server-fetch` | conteúdo real de example.com |
| `sequential-thinking` | `npx -y @modelcontextprotocol/server-sequential-thinking` | thought registrada |
| `filesystem` | `npx .../server-filesystem <repo>` | allowlist confirmada |

## Receitas

```bash
uvx mcp-server-fetch                    # Python, sem auth
npx -y @modelcontextprotocol/server-sequential-thinking
npx -y @modelcontextprotocol/server-filesystem /caminho/escopo
```

## Trust gate (Official/Community SaaS)

1. Exige API key/segredo? → só com ordem explícita do operador.
2. Licença declarada? Sem LICENSE = degraded (padrão R621).
3. `.mcp.json` do plugin lido antes de registrar.

## Adiado com motivo

- `memory` (KG): sobrepõe MetaBus — SPEC própria futura.
- `git`/`time`: bash cobre.
