---
name: claude-plugins
description: >-
  Guia do marketplace Claude Code Plugins (anthropics, licença POR PLUGIN).
  Use para instalar via /plugin install {nome}@claude-plugin-directory,
  auditar estrutura (.claude-plugin/plugin.json, .mcp.json,
  commands/agents/skills) e aplicar o gate de trust: Anthropic NÃO controla
  MCP servers/arquivos dos plugins — checar homepage de cada um. NÃO instala
  plugins automaticamente.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R647
spec: SPEC-935-R647-ecossistema-claude.md
---

# Skill: Claude Plugins (marketplace, SPEC-935-R647)

## Instalação (operador)

```
/plugin install {plugin-name}@claude-plugin-directory
```

ou `/plugin` → Discover. Estrutura: `/plugins` (Anthropic) +
`/external_plugins` (parceiros/comunidade, com submission form e QA).

## Gate de trust (obrigatório por plugin)

1. Ler `plugin.json` + README + homepage do plugin.
2. Inventariar `.mcp.json` (que servidores? que comandos?).
3. Licença é POR PLUGIN — registrar antes de federar (padrão R621:
   sem licença declarada = degraded).
4. Aviso oficial: Anthropic não verifica funcionamento nem mudanças futuras.

## Regras

- Curadoria caso a caso; nenhum plugin entra no pipeline automático sem
  aprovação do operador.
- Referência: https://code.claude.com/docs/en/plugins
