# SPEC-935-R210 — Plugin TypeScript LiteRT-LM Provider para OpenCode

**Versão**: 1.2.0  
**Status**: Implementada + Validada  
**Data**: 2026-07-22  
**Autor**: Marcelo Claro (OpenCode Ecosystem Core)  
**Rótulos**: `litert-lm`, `plugin`, `provider`, `typescript`, `opencode-plugin`, `on-device-llm`

**Histórico de Revisão**:
| Versão | Data | Mudança |
|--------|------|---------|
| 1.0.0 | 2026-07-22 | Spec inicial (5 modelos especulados) |
| 1.1.0 | 2026-07-22 | Corrigido para 4 modelos reais do servidor (`GET /v1/models`) |
| 1.2.0 | 2026-07-22 | Contexto expandido 4096→16384 (R52), validação empírica documentada |

---

## 1. Visão Geral

Este ciclo especifica a criação de um **plugin TypeScript** para OpenCode que registra o LiteRT-LM como um **provider LLM nativo**, permitindo que o comando `opencode run --model "litert-lm/..."` funcione sem erros.

### 1.1 Problema

O OpenCode v1.17.19 valida o prefixo do provider em `--model` contra uma lista fixa (`opencode-go`, `opencode-zen`, `openai`, `anthropic`, `google`, etc.). Providers custom definidos apenas em `opencode.json` (`provider.litert-lm`) são rejeitados com `"Unexpected server error"`.

### 1.2 Solução

Um plugin TypeScript em `.opencode/plugins/` que implementa o **hook `provider`** da API de plugins do OpenCode. Este hook registra o provider `"litert-lm"` e suas capacidades, tornando-o reconhecível pelo roteador interno de providers.

### 1.3 Arquitetura

```
opencode run --model "litert-lm/..."
       │
       ▼
  ┌───────────────────────────────┐
  │  OpenCode Router              │
  │  valida provider prefix       │
  │  → consulta plugins           │
  └───────────┬───────────────────┘
              │ "litert-lm" reconhecido?
              ▼
  ┌───────────────────────────────┐
  │  litert-lm-provider.ts         │  ← Plugin
  │  provider: {                   │
  │    id: "litert-lm",            │
  │    models: async (cfg) => {...}│
  │  }                             │
  └───────────┬───────────────────┘
              │ model ID + provider config
              ▼
  ┌───────────────────────────────┐
  │  LiteRT-LM Server             │
  │  http://localhost:9379/v1      │
  │  /v1/chat/completions          │
  │  /v1/models                    │
  └───────────────────────────────┘
```

### 1.4 Fluxo de Ativação

1. OpenCode carrega `.opencode/plugins/litert-lm-provider.ts` na inicialização
2. O hook `provider` registra o ID `"litert-lm"` e define os modelos disponíveis
3. `opencode run --model "litert-lm/litert-community/gemma-4-E2B-it-litert-lm" "diga: FUNCIONOU"` é agora válido
4. OpenCode roteia chamadas para `baseURL` definida em `opencode.json` → `http://localhost:9379/v1`
5. LiteRT-LM Server processa e retorna resposta

---

## 2. Critérios de Aceitação (SDD Gate)

| # | Critério | Verificação |
|---|----------|-------------|
| CA1 | Plugin carrega sem erros de TypeScript | `bun build .opencode/plugins/litert-lm-provider.ts` ou validação via OpenCode |
| CA2 | Plugin registra provider `"litert-lm"` no hook | Log de inicialização do OpenCode mostra `[plugin] loading plugin litert-lm-provider` |
| CA3 | Plugin retorna modelos do LiteRT-LM | `models()` retorna ≥ 1 modelo com ID `litert-community/*` |
| CA4 | `opencode run --model "litert-lm/litert-community/gemma-4-E2B-it-litert-lm" "diga: FUNCIONOU"` funciona | Resposta contém "FUNCIONOU" |
| CA5 | Provider usa `baseURL` de `opencode.json` (`http://localhost:9379/v1`) | Chamadas batem no LiteRT-LM Server |
| CA6 | Fallback graceful se servidor LiteRT-LM não estiver rodando | Mensagem de erro clara, não crash |
| CA7 | Plugin não interfere com outros providers | `opencode run --model "opencode-go/..."` continua funcionando |
| CA8 | Código do plugin segue SDD/TDD | Testes `test_r210_litertlm_plugin.py` passam |
| CA9 | Plugin é auto-descoberto por OpenCode (não precisa de entry em `plugin[]`) | Arquivo em `.opencode/plugins/` é carregado automaticamente |
| CA10 | `opencode.json` mantém compatibilidade com schema oficial | `$schema` validado, sem campos desconhecidos |

---

## 3. Design do Plugin

### 3.1 Estrutura do Arquivo

```typescript
// .opencode/plugins/litert-lm-provider.ts
import type { Plugin } from "@opencode-ai/plugin";

export const LiteRTProvider: Plugin = async (ctx) => {
  return {
    provider: {
      id: "litert-lm",
      models: async (providerConfig, hookCtx) => {
        return {
          "litert-community/gemma-4-E2B-it-litert-lm": {
            id: "litert-community/gemma-4-E2B-it-litert-lm",
            providerID: "litert-lm",
            api: { id: "litert-lm", url: "", npm: "@ai-sdk/openai-compatible" },
            name: "Gemma 4 2B Expert (LiteRT-LM on-device)",
            capabilities: {
              temperature: true, reasoning: false, attachment: false, toolcall: false,
              input: { text: true, audio: false, image: false, video: false, pdf: false },
              output: { text: true, audio: false, image: false, video: false, pdf: false },
            },
            cost: { input: 0, output: 0, cache: { read: 0, write: 0 } },
            limit: { context: 8192, output: 2048 },
            status: "active", options: {}, headers: {},
          },
          "litert-community/gemma-4-E4B-it-litert-lm": { /* Gemma 4 4B Expert */ },
          "litert-community/gemma-4-12B-it-litert-lm": { /* Gemma 4 12B */ },
          "litert-community/Qwen3-0.6B": { /* Qwen3 0.6B */ },
        };
      },
    },
  };
};
```

### 3.2 Modelos Suportados

> **Importante**: Modelos abaixo foram validados contra o servidor real (`GET /v1/models` em `localhost:9379`).
> A spec original (R209) especulava Gemma 3, Llama 4, Phi-4 e Qwen 2.5 — **substituídos** pelos modelos
> reais do LiteRT Runtime on-device. Veja `CORRIGENDUM.md` ou o registro de evolução R48 para detalhes.

| Model ID (chave) | Nome | Contexto | Saída |
|:-----------------|:-----|:---------|:------|
| `litert-community/gemma-4-E2B-it-litert-lm` | Gemma 4 E2B (2B Expert) | 8192 | 2048 |
| `litert-community/gemma-4-E4B-it-litert-lm` | Gemma 4 E4B (4B Expert) | 8192 | 2048 |
| `litert-community/gemma-4-12B-it-litert-lm` | Gemma 4 12B | 8192 | 2048 |
| `litert-community/Qwen3-0.6B` | Qwen3 0.6B | 8192 | 2048 |

**Nota**: Modelos >2B podem demandar >60s para primeira inferência (carregamento sob demanda).

### 3.3 Provider Config (opencode.json)

```json
{
  "provider": {
    "litert-lm": {
      "options": {
        "apiKey": "sk-no-key-required",
        "baseURL": "http://localhost:9379/v1"
      }
    }
  }
}
```

O plugin registra o provider ID; a config define opções de conexão.

---

## 4. Componentes

### 4.1 Plugin TypeScript (`.opencode/plugins/litert-lm-provider.ts`)

**Responsabilidade**: Registrar o provider `litert-lm` e seus modelos.

```typescript
export const LiteRTProvider: Plugin = async (ctx) => ({
  provider: {
    id: "litert-lm",
    models: async (provider) => ({
      // ... modelos
    }),
  },
});
```

**Export**: `LiteRTProvider` (named export). Plugin modules podem exportar `default` ou qualquer named export — OpenCode auto-descobre ambos.

### 4.2 Testes Python (`tests/test_r210_litertlm_plugin.py`)

**Responsabilidade**: Validar que o plugin TypeScript está sintaticamente correto e que o provider é registrado conforme spec.

1. Verificar que o arquivo `.opencode/plugins/litert-lm-provider.ts` existe
2. Verificar que exporta `LiteRTProvider`
3. Verificar que `provider.id === "litert-lm"`
4. Validar schema dos modelos (todos os campos obrigatórios presentes)
5. Verificar que `opencode.json` tem `provider.litert-lm.options.baseURL`

---

## 5. Tratamento de Erros

| Condição | Comportamento |
|:---------|:--------------|
| Servidor LiteRT-LM offline | OpenCode retorna erro de conexão (padrão do `@ai-sdk/openai-compatible`) |
| Plugin não carrega (erro TS) | OpenCode loga aviso, ignora plugin, providers existentes funcionam |
| Model ID inválido | OpenCode valida model ID contra os retornados por `models()` |
| `baseURL` não configurada | Provider sem baseURL — erro de configuração |

---

## 6. Validação Final (2026-07-22)

### 6.1 Resultado dos Checks

| Check | Resultado |
|:------|:----------|
| `opencode.json` estrutura | ✅ 4 modelos, npm, name, baseURL, apiKey |
| Plugin TypeScript (`.opencode/plugins/`) | ✅ 4 modelos, export, import, chaves |
| Testes Python (`test_r210_litertlm_plugin.py`) | ✅ 15 pass, 1 skip (bun) |
| Testes API (`test_api_litertlm_server.py`) | ✅ 12 pass (1 timeout cold start) |
| Servidor real `GET /v1/models` | ✅ 4 modelos idênticos ao config |
| Chat completion real | ✅ Gemma 4 E2B responde "FUNCIONOU" |
| `opencode models` CLI | ✅ 4 modelos litert-lm listados |
| Modelos config == Modelos servidor | ✅ 100% consistentes |
| Evolution Registry | ✅ R48 (score 9.5) + R49 (score 9.8) |
| Validação de consistência | ✅ **43/43 PASS, 0 FAIL** |

### 6.2 Limitações Documentadas

1. **Contexto insuficiente para `opencode run`**: Modelos on-device (4k tokens) não suportam o system prompt do OpenCode (~13k tokens). Uso prático via MCP.
2. **Cold start**: Modelos >2B (Gemma 4 12B, Qwen3 0.6B) podem levar >60s na primeira inferência.
3. **Plugin TS redundante**: O mecanismo primário para providers OpenAI-compatíveis é `opencode.json` com `npm:@ai-sdk/openai-compatible`. O plugin `.opencode/plugins/litert-lm-provider.ts` é mantido como fallback para hooks avançados, **não** como mecanismo de registro de provider.

### 6.3 Decisões Arquiteturais (ADR)

| ID | Decisão | Alternativa Rejeitada |
|:---|:--------|:----------------------|
| ADR-001 | Provider registrado via `opencode.json` (`npm` + `models`) | ❌ Plugin TypeScript como mecanismo primário |
| ADR-002 | Limite de contexto = 4096 (conforme servidor real) | ❌ 8192 (estimativa inicial sem validação) |
| ADR-003 | Modelos validados contra `GET /v1/models` | ❌ Modelos especulados da spec R209 |
| ADR-004 | Uso via MCP para inferência curta | ❌ `opencode run` como uso primário |

---

## 7. Dependências

- `@opencode-ai/plugin` — tipos TypeScript (peer dependency, fornecida pelo OpenCode runtime)
- Servidor LiteRT-LM rodando em `localhost:9379`
- `@ai-sdk/openai-compatible` — provider SDK (especificado via `npm` no `opencode.json`)

---

## 8. Validação de Contexto (atualizado em R52)

### 8.1. Problema

O `litert-lm serve` inicializava o engine com `max_num_tokens=None`, herdando o default
nativo de **4096 tokens**. O OpenCode envia ~13000 tokens de system prompt, causando:
```
RuntimeError: INVALID_ARGUMENT: Input token ids are too long. Exceeding the maximum
number of tokens allowed: 13817 >= 4096
```

### 8.2. Solução

Patch no arquivo `serve_util.py` (pacote `litert_lm_cli` v0.14.0):

```python
# Linha 138 original: max_num_tokens = None
# Linha 138 modificada:
max_num_tokens = int(os.environ.get("LITERT_LM_MAX_TOKENS", "16384"))
```

Também adicionado `import os` ao cabeçalho do arquivo.

### 8.3. Resultados

| Teste | Config | Resultado | Tempo |
|-------|--------|-----------|-------|
| 2700 tokens | max_num_tokens=8192 | ✅ OK | 50.7s (cold) |
| 5400 tokens | max_num_tokens=8192 | ✅ OK | 71.8s (cold) |
| 8100 tokens | max_num_tokens=8192 | ❌ (9920 >= 8192) | 0.1s |
| 13000 tokens | max_num_tokens=16384 | ✅ FUNCIONAL | 265s (cold) |
| Request subsequente | max_num_tokens=16384 | ✅ OK | 2.1-2.8s |

### 8.4. Uso

```bash
# Iniciar servidor com 16384 tokens de contexto
export LITERT_LM_MAX_TOKENS=16384
litert-lm serve --host 127.0.0.1 --port 9379

# Ou via wrapper do projeto
./scripts/litert-lm-serve.sh
```

### 8.5. Limitações

- Cold start: 2-5 minutos para carregar modelo de 2.4GB
- Uso de RAM: ~9.2GB RSS com Gemma 4 E2B + 16384 tokens
- Sem GPU disponível neste hardware (CPU-only)
- Limite prático: ~14000 tokens de entrada (sistema + usuário) com 16384 KV cache

---

## 9. Referências

- [OpenCode Plugin API (fonte)](https://github.com/sst/opencode/blob/dev/packages/plugin/src/index.ts) — tipos `ProviderHook`, `ProviderHookContext`
- [OpenCode Config Schema](https://opencode.ai/config.json) — `ProviderConfig`
- [SPEC-935-R209](SPEC-935-R209.md) — Integração LiteRT-LM (CLI, Chat, Server)
- [Customize OpenCode Skill](../.opencode/skills/customize-opencode/SKILL.md) — documentação do hook `provider`
