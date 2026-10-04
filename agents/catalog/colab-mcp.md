---
id: colab-mcp
name: colab-mcp
description: >-
  Ponte orquestrável do Colab MCP Server (googlecolab/colab-mcp, Apache-2.0):
  codificação assistida interativa dentro do notebook Colab, complemento do
  fluxo terminal do colab-cli. Expõe presença, versão e config stdio.
type: integration
round: R645
spec: SPEC-935-R645-colab-cli-mcp.md
trust: 0.9
---

# colab-mcp — Colab MCP Server (in-notebook)

Ponte orquestrável (não executa o protocolo MCP): `colab-mcp`
(repositório `googlecolab/colab-mcp`, fork `MarceloClaro/colab-mcp`).

## Capacidades

- `mcp_available()` — True se `colab-mcp` ou `uvx` no PATH.
- `mcp_version()` — semver via binário local; None sem rede implícita.
- `mcp_config(prefer_uvx)` — dict stdio pronto para `opencode.json`.
- `doctor_check()` — pass se executável (binário ou uvx), warn se ausente.
- CLI `/colab-mcp status|config|doctor|install`.

## Limites (anti-overclaim R110)

- Complemento do `colab-cli`, não substituto.
- Credenciais/kernels do notebook pertencem ao operador.
- Ferramentas do notebook NÃO são "verificadas" sem validação do Core.
