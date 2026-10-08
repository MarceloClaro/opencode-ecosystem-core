---
name: core-hooks
description: >-
  Hooks do Core (SPEC-935-R653/R659): engine fail-closed com HookMatcher e
  política deny-list auditada para Bash. Use para rotear eventos
  (PreToolUse/PostToolUse/SessionStart/SessionEnd), bloquear comandos
  destrutivos/exfiltradores e auditar em JSONL. Exceção de hook nega.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R653
spec: SPEC-935-R653-core-hooks.md
---

# Skill: Hooks do Core (SPEC-935-R653)

## Uso

```python
from hooks.engine import HookMatcher, run_hooks
from hooks.policy import default_matchers, check_bash, audit_log

check_bash("rm -rf /")          # {"allow": False, "regra": "rm-rf-raiz", ...}
run_hooks("PreToolUse", "Bash", {"command": cmd}, default_matchers())
audit_log("PreToolUse", {...})  # ~/.cache/opencode-hooks/audit.jsonl
```

Matcher próprio: `HookMatcher("Bash", hooks=[fn])`, `HookMatcher("mcp__*", ...)`,
`HookMatcher("re:^colab", ...)`. Vereditos de negação: `False`,
`{"deny": True}` ou `{"permissionDecision": "deny"}`.

## Fiação no SDK livre

`build_options(..., hooks={"PreToolUse": [HookMatcher(...)]})` — aceito
junto às lambdas legadas. Exceção nega (fail-closed, lição R650).

O alias `hooks={"matchers": [...]}` também aplica `PreToolUse`. Os callbacks
podem receber `(nome, argumentos)` ou `(nome, argumentos, contexto)`; a engine
escolhe a assinatura antes de executar, sem repetir um callback que lance
`TypeError`. O contexto inclui `event`, e `PostToolUse` recebe o resultado.
`SessionEnd` ocorre também em falha ou fechamento do iterador. Uma falha de
`PostToolUse` informa que a ferramenta já foi executada; ela não desfaz o efeito.

## Regras

- Deny-list evolui por **adição com teste** (cada padrão tem caso).
- Auditoria fora do repo; falha de disco nunca lança.
- Auditoria de Bash registra hash e tamanho do comando; campos sensíveis são redigidos.
- A lista de bloqueio não implementa isolamento do sistema operacional.
- `| sudo bash` também é pipe-para-shell (bypass corrigido ao vivo, R656).
