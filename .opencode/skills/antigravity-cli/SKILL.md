---
name: antigravity-cli
description: >-
  Runner direto do Antigravity CLI (agy) como executor externo orquestrável
  (SPEC-935-R651), complemento da ponte profunda (bridge + MCP + executor).
  Use para /agy status, /agy run '<prompt>' [--agent A] [--format F] e
  /agy doctor. Forma canônica --agent/--print/--output-format com detecção
  de falha silenciosa; nunca herdar TTY.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R651
spec: SPEC-935-R651-antigravity-cli-runner.md
---

# Skill: Antigravity CLI runner (SPEC-935-R651)

## Duas vias (complementares, não concorrentes)

| Via | Quando |
|---|---|
| `/agy run '<prompt>'` | Chamada direta, sem revisão (este runner) |
| `ecosystem_run` executor `antigravity` | Análise com revisão independente (R621) |

## Forma canônica

```
agy --agent <agent> --print '<prompt>' --output-format text
```

Sintaxe errada abre TUI (`bubbletea: error opening TTY`); `rc 0` com
`CLI error:/Error:` no stdout é falha — o runner detecta.

## Estado ao vivo (R654)

Binário 1.2.16 responsivo (`--version`, `agent` rc 0); chamadas ao provedor
oscilaram (eligibility/avatar EOF 2x + hang 1x) sob carga — runner trata
ambos como `ok: False` (timeout incluído). Resposta direta do provedor
pendente de janela estável.

## Regras

- stdin sempre DEVNULL; timeout sempre configurado.
- Nunca declarar saída como verificada sem validação (R110).
