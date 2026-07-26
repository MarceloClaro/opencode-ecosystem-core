---
name: colibri-agent
type: specialist
category: inference
capabilities:
  - colibri:chat
  - colibri:complete
  - colibri:olmoe:complete
  - colibri:olmoe:validate
  - colibri:status
  - colibri:info
  - inference-on-device
  - glm-5.2
  - olmoe
  - moe-744b
  - expert-streaming
  - openai-compatible-api
  - local-llm
---

# colibri-agent

**ID**: `colibri-agent`  
**Tipo**: Agente de inferência on-device (A2A registrado no Blackboard)  
**MCP Server**: `integrations/colibri/colibri_mcp_server.py`  
**Bridge**: `integrations/colibri/bridge.py::ColibriBridge`  
**Repositório**: `https://github.com/MarceloClaro/colibri` (fork de `JustVugg/colibri`)  
**Confiança inicial**: 0.90 (Trust Engine)

---

## Descrição

Agente especializado em execução local de modelos MoE via runtime **Colibri** — motor de inferência em C puro, zero dependências. Suporta dois modelos:

| Modelo | Params | Experts | RAM | Status |
|---|---|---|---|---|
| **OLMoE-1B-7B** | 1B dense + 7B sparse | 64 (8 ativos) | ~8 GB | ✅ Já convertido e validado |
| **GLM-5.2** | 744B MoE | 19.456 | ~25 GB mínimo | 🚧 Requer hardware com GPU |

## Capacidades

| Capacidade | Descrição |
|---|---|
| `colibri:chat` | Chat multi-turn com GLM-5.2 (API OpenAI) |
| `colibri:complete` | Completion single-turn (GLM-5.2) |
| `colibri:olmoe:complete` | Inferência OLMoE via binário nativo C (CPU) |
| `colibri:olmoe:validate` | Validação token-exata contra referência |
| `colibri:status` | Estado dos runtimes disponíveis |
| `colibri:info` | Informações detalhadas dos engines |
| `inference-on-device` | Inferência 100% local |
| `olmoe` | Suporte OLMoE (Allen AI) |
| `local-llm` | Provedor LLM local genérico |

## Caminhos no ecossistema

```
Binário OLMoE:   colibri/c/olmoe  (compilado, 93 KB)
Modelo OLMoE:    /home/marceloclaro/models/olmoe_merged/  (6.5 GB, int8)
Referência:      colibri/c/ref_olmoe_real.json
Bridge Python:   integrations/colibri/bridge.py::ColibriBridge
MCP Server:      integrations/colibri/colibri_mcp_server.py
```

## Performance medida (OLMoE)

| Métrica | Valor |
|---|---|
| **Correspondência de tokens** | 12/12 (100% contra referência) |
| **Cache hit rate** | 62.4% (1278 hits / 770 misses) |
| **Pico RSS** | 4.79 GB |
| **Carregamento denso** | 12.3s |
| **Quantização** | int8 (expert cache) |
| **Tamanho dos especialistas** | 6.5 GB (compressão de 50% sobre 12.9 GB) |

## Uso

```python
from integrations.colibri import ColibriBridge

bridge = ColibriBridge()

# Inferência OLMoE (já funciona!)
if bridge.olmoe_available:
    result = bridge.olmoe_complete("Explique o que é um modelo MoE")
    print(result["stdout"])

# GLM-5.2 (requer server)
if bridge.available:
    bridge.start_server()
    result = bridge.complete("Explique o que é um modelo MoE")
    bridge.stop_server()
```
