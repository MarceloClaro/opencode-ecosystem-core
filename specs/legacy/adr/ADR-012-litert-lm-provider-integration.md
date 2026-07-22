# ADR-012: Integração LiteRT-LM como Provider OpenAI-Compatível no OpenCode

**Data**: 2026-07-22
**Status**: Aceito
**Ciclo**: R48 → R49
**Autor**: Marcelo Claro (Orquestrador Central)

## Contexto

O OpenCode Ecosystem Core precisa suportar modelos on-device via LiteRT-LM (Google
GEMma 4, Qwen3) como provider LLM nativo. O servidor LiteRT-LM expõe API
OpenAI-compatível em `localhost:9379`.

## Decisão

### 1. Provider registrado via `opencode.json`

```json
"litert-lm": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "LiteRT-LM (on-device)",
  "options": {
    "apiKey": "sk-no-key-required",
    "baseURL": "http://localhost:9379/v1"
  },
  "models": { ... }
}
```

**Motivação**: A documentação oficial do OpenCode (Atomic Chat, llama.cpp) demonstra
que providers OpenAI-compatíveis são registrados via `npm` + `models` no config —
não via plugin TypeScript.

### 2. Plugin TS mantido como fallback

O plugin em `.opencode/plugins/litert-lm-provider.ts` é mantido para:
- Documentar o formato do hook `provider` para referência futura
- Servir como template se o OpenCode mudar a API de plugins
- Registrar hooks avançados (chat.params, tool.execute) se necessário

### 3. Modelos validados contra servidor real

Os 4 modelos foram validados por:
- `GET /v1/models` → 4 modelos retornados
- `POST /v1/chat/completions` → Gemma 4 E2B responde
- `opencode models` → 4 modelos listados

### 4. Limite de contexto = 4096

Aferido empiricamente: o servidor rejeita prompts >4096 tokens. Todos os modelos
on-device compartilham este limite.

## Consequências

### Positivas
- Provider reconhecido pelo OpenCode sem plugin TypeScript
- 4 modelos disponíveis via `opencode models`
- Chat completion funcional via API direta
- MCP server funcional para inferências curtas

### Negativas / Limitações
- `opencode run --model "litert-lm/..."` falha por contexto insuficiente (4k < 13k)
- Modelos >2B têm cold start lento (>60s)
- Plugin TypeScript não é o mecanismo primário (documentação inicial estava errada)

## Alternativas Consideradas

| Alternativa | Motivo da Rejeição |
|-------------|-------------------|
| Plugin TypeScript como mecanismo primário | OpenCode não carrega models de plugin para providers custom |
| Provider sem `npm` | OpenCode não reconhece o SDK correto |
| 5 modelos especulados (R209) | Servidor real expõe 4 modelos diferentes |
| Contexto 8192 | Servidor real limita a 4096 |

## Referências

- [SPEC-935-R210-litertlm-plugin-provider.md](../SPEC-935-R210-litertlm-plugin-provider.md)
- [SPEC-935-R209.md](../SPEC-935-R209.md)
- [OpenCode Providers Docs](https://opencode.ai/docs/providers/#custom-provider)
- [OpenCode Plugins Docs](https://opencode.ai/docs/plugins/)
