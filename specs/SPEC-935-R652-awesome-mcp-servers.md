# SPEC-935-R652 — Awesome MCP Servers: referência primeiro (R651 real)

**Ronda:** R652 (SPEC)
**Status:** em implementação
**Data:** 2026-10-04
**Autor:** marceloclaro (orquestrador central)
**Padrão:** M7 federado — curadoria executável (espelho de R648)

## Objetivo

Transformar a lista `wong2/awesome-mcp-servers` (583 linhas, ~487 links:
Reference + Official + Community + Clients + Frameworks) em cobertura real
no Core, com política **referência primeiro**: servidores oficiais de
referência (modelcontextprotocol, sem auth, instaláveis via uvx/npx) entram
como MCP locais; SaaS com API key ficam em curadoria com trust gate.

## Fonte de verdade (anti-overclaim)

README capturado em 2026-10-04 (raw, 583 linhas). Prova ao vivo nesta
máquina (protocolo stdio, initialize → list → call):
- `fetch` (uvx `mcp-server-fetch`): `fetch(example.com)` → conteúdo real.
- `sequentialthinking` (npx): thought registrada (`thoughtHistoryLength 1`).
- `filesystem` (npx, escopo `/tmp/opencode`): allowlist confirmada.

## Escopo

- `opencode.json#mcp`: `fetch`, `sequential-thinking`, `filesystem`
  (escopo = raiz do repo) via `build_config()`.
- `.opencode/skills/awesome-mcp-servers/SKILL.md` (política + receitas) +
  `agents/catalog/awesome-mcp-servers.md`.
- Testes: presença/comandos dos 3 servidores em `build_config()` (sem rede).
- Sem MCP remoto/SaaS nesta ronda (exigem segredos do operador).

## Critérios de aceitação

1. `build_config()["mcp"]` contém os 3 com comandos exatos (uvx/npx).
2. `opencode.json --check` OK após regen.
3. Nenhum teste existente quebrado; doctor global 0 fail.
4. Skill documenta trust gate (SaaS = caso a caso, nunca auto-install com key).
5. Ciclo de evolução registrado.

## Decisões registradas

- `filesystem` escopado à raiz do repo (contexto de trabalho dos agentes).
- `memory` (KG) adiado: sobrepõe o MetaBus episódico; merece SPEC própria.
- `git`/`time` adiados: bash cobre; custo/benefício baixo.
