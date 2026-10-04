# SPEC-935-R649 — OpenCode Agent SDK (free, local-first)

**Ronda:** R649 (SPEC) / evolução R653
**Status:** em implementação
**Data:** 2026-10-03
**Autor:** marceloclaro (orquestrador central)
**Padrão:** M7 — SDK livre espelhando a superfície do `claude-agent-sdk`

## Objetivo

Responder com código (não só curadoria) à pergunta "tem como fazer algo
similar ao `claude_agent_sdk` e FREE?": um SDK de agente **gratuito,
local-first e sem conta**, falando HTTP OpenAI-compatível com provedores
que já estão de pé nesta máquina (verificado em 2026-10-03):

- LiteRT-LM `:9379` — Gemma 4 (E2B/E4B/12B), OpenAI-compatível, UP.
- Ollama `:11434` — `gemma4:e2b-tuned`, `/v1` OpenAI-compatível, UP.
- Colibri `:8090` — fora do ar no momento (ponte existe, prova adiada).

Custo marginal: **R$ 0,00** (inferência on-device/locaal, sem token faturável).

## Superfície (espelho mecânico do Claude SDK)

| Claude (`anthropics`, $$) | OpenCode SDK (este, R$ 0) |
|---|---|
| `query(prompt, options)` async | `query(prompt, options)` gerador sync de eventos (`text/tool_use/result`) |
| `ClaudeAgentOptions` | `build_options(...)` mesmo vocabulário (system, allowed/disallowed, max_turns, cwd, permission_mode) |
| `ClaudeSDKClient` + custom tools + hooks | loop agêntico com tools locais + hooks `PreToolUse` |
| `@tool` + `create_sdk_mcp_server` (in-process) | `@tool` + `create_local_tool_server` (dispatch direto, zero IPC; export FastMCP se `mcp` instalado) |
| CLI `claude` embutido | autodetect `LiteRT-LM → Ollama → Colibri` (primeiro saudável), override por env/arg |

Diferenças assumidas: sem cobrança/conta; sem `cli_path`; eventos como dicts
(documentados), não classes de mensagem; loop sync.

## Critérios de aceitação

1. Transporte só-stdlib (`urllib`), sem dependência nova.
2. `build_options(prompt, ...)` valida prompt; `ValueError` em português.
3. `detect_provider()` retorna o primeiro saudável (`GET /v1/models`, timeout
   curto); `None` se nenhum; nunca lança.
4. `query()` executa loop agêntico até `max_turns`: tool_calls de tools
   permitidas executam localmente; bloqueadas vão a `permission_mode`/hooks;
   hooks podem negar (`deny`).
5. `@tool` registra função + JSON schema; `create_local_tool_server`
   devolve servidor in-process executável sem `mcp`.
6. `doctor_check()`: pass com ≥1 provedor saudável; warn caso contrário.
7. `main()`: `status|doctor|install|query|tools` + `--help`; exit 2 em misuse.
8. Gate TDD: mocks de HTTP (tool_call → execução → texto final; deny de hook;
   autodetect) + **prova ao vivo** contra provedor local (loop com tool real).
9. Skill + card + `/opencode-sdk`; doctor global 0 fail; ciclo R653.

## Decisões registradas

- Sync em vez de async: Core é sync; `anyio` não entra como dependência.
- Sem fallback em nuvem: se nada local responde, `query()` falha explícito
  (sem tentar pago escondido — FREE é garantia, não preferência).
- Degradação honesta: modelo sem tool-calling devolve texto; o loop não finge.
