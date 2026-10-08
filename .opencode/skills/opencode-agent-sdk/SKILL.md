---
name: opencode-agent-sdk
description: >-
  SDK de agente com provedores locais por padrão (SPEC-935-R649/R659).
  Espelha o claude-agent-sdk (query, options, @tool, servidor in-process,
  hooks) sobre HTTP OpenAI-compatível com LiteRT-LM :9379, Ollama :11434 e
  Colibri :8090. Use para consultas agênticas locais com tools Python,
  detectar provedor, montar options e checar saúde. Uma URL configurada pelo
  operador pode apontar para serviço remoto; custo depende desse serviço.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R649
spec: SPEC-935-R649-opencode-agent-sdk.md
---

# Skill: OpenCode Agent SDK (SPEC-935-R649/R659)

## Comandos

| Comando | Ação |
|---|---|
| `/opencode-sdk status` | Disponibilidade do provedor; não comprova inferência |
| `/opencode-sdk query --prompt '...' [--model M] [--max-turns N]` | Loop agêntico local (texto + tools) |
| `/opencode-sdk tools` | Tools registradas no processo |
| `/opencode-sdk doctor` / `/opencode-sdk install` | Saúde / como subir provedor |

## Uso programático

```python
from integrations.opencode_agent_sdk import tool, query, build_options

@tool("somar", "Soma dois inteiros", {
    "type": "object", "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
    "required": ["a", "b"], "additionalProperties": False,
})
def somar(args):
    return args["a"] + args["b"]

for ev in query("", build_options("Some 20+22.", allowed_tools=["somar"], max_turns=3)):
    print(ev)  # {"type": "text"|"tool_use"|"tool_denied"|"result"|"error", ...}
```

## Evidência de execução

Consulte `docs/evidence/R659_SDK_HOOKS_*.json`. Cada registro identifica o
modelo, o resultado de cada fase e eventuais erros. Uma resposta de saúde não
substitui a sequência ferramenta → resposta final. A ferramenta Python é nativa
no processo; `create_local_tool_server` não a exporta como servidor MCP.

## Hooks e negação

```python
opts = build_options("...", allowed_tools=["somar"],
                     hooks={"PreToolUse": [lambda nome, args: {"permissionDecision": "deny"}]})
```

## Regras

- Sem provedor disponível, `query()` informa erro; não há fallback automático em nuvem.
- Modelos pequenos podem ignorar `tool_choice` (degradação honesta em texto).
- Override: `OPENCODE_SDK_BASE_URL` (+ `OPENCODE_SDK_MODEL`).
- Defina `max_turns` e `timeout`; a CLI retorna não zero em falha ou orçamento esgotado.
- Os quatro eventos de hooks são aplicados; `matchers` legado equivale a `PreToolUse`.
- Argumentos inválidos não executam ferramentas, inclusive após alteração por hook.
- Servidores de ferramentas locais conservam o schema do próprio handler, mesmo com nomes iguais.
