---
name: opencode-agent-sdk
description: >-
  SDK de agente FREE e local-first do Core (SPEC-935-R649, custo R$ 0,00).
  Espelha o claude-agent-sdk (query, options, @tool, servidor in-process,
  hooks) sobre HTTP OpenAI-compatível com LiteRT-LM :9379, Ollama :11434 e
  Colibri :8090. Use para consultas agênticas locais com tools Python,
  detectar provedor, montar options e checar saúde. Sem conta, sem cobrança,
  sem fallback em nuvem.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R649
spec: SPEC-935-R649-opencode-agent-sdk.md
---

# Skill: OpenCode Agent SDK (free, SPEC-935-R649)

## Comandos

| Comando | Ação |
|---|---|
| `/opencode-sdk status` | Provedor detectado + custo R$ 0,00 |
| `/opencode-sdk query --prompt '...' [--model M] [--max-turns N]` | Loop agêntico local (texto + tools) |
| `/opencode-sdk tools` | Tools registradas no processo |
| `/opencode-sdk doctor` / `/opencode-sdk install` | Saúde / como subir provedor |

## Uso programático

```python
from integrations.opencode_agent_sdk import tool, query, build_options

@tool("somar", "Soma dois inteiros", {"a": {"type": "integer"}, "b": {"type": "integer"}})
def somar(args):
    return args["a"] + args["b"]

for ev in query("", build_options("Some 20+22.", allowed_tools=["somar"], max_turns=3)):
    print(ev)  # {"type": "text"|"tool_use"|"tool_denied"|"result"|"error", ...}
```

## Provas ao vivo (R653, R$ 0,00)

- Texto: E2B devolveu `LIVRE-FUNCIONA` + `result/stop` via `query()`.
- Tool loop: E2B chamou `somar(a=20, b=22)` → execução local `42`
  (`tool_use`); a síntese final estourou o tempo sob carga — máquina
  i5 sem GPU exige paciência (reconhecer, não mascarar).

## Hooks e negação

```python
opts = build_options("...", allowed_tools=["somar"],
                     hooks={"PreToolUse": [lambda nome, args: {"permissionDecision": "deny"}]})
```

## Regras

- FREE é garantia: sem provedor local, `query()` falha explícito (nunca tenta nuvem).
- Modelos pequenos podem ignorar `tool_choice` (degradação honesta em texto).
- Override: `OPENCODE_SDK_BASE_URL` (+ `OPENCODE_SDK_MODEL`).
- On-device é lento sob carga (i5 sem GPU): prefira E2B e `max_turns` baixo.
