---
name: litert-lm-agent
description: Agente especializado litert-lm-agent
version: '1.0.0'
skills:
- id: litert-lm-list
  name: Litert Lm:List
  description: Capacidade especializada em litert lm:list.
  tags: [litert, litert-lm-list]
  examples: [Aplique litert lm list, Execute operação de litert lm list]
- id: litert-lm-run
  name: Litert Lm:Run
  description: Capacidade especializada em litert lm:run.
  tags: [litert, litert-lm-run]
  examples: [Aplique litert lm run, Execute operação de litert lm run]
- id: litert-lm-chat
  name: Litert Lm:Chat
  description: Capacidade especializada em litert lm:chat.
  tags: [litert, litert-lm-chat]
  examples: [Aplique litert lm chat, Execute operação de litert lm chat]
- id: litert-lm-import
  name: Litert Lm:Import
  description: Capacidade especializada em litert lm:import.
  tags: [litert, litert-lm-import]
  examples: [Aplique litert lm import, Execute operação de litert lm import]
- id: litert-lm-serve
  name: Litert Lm:Serve
  description: Capacidade especializada em litert lm:serve.
  tags: [litert, litert-lm-serve]
  examples: [Aplique litert lm serve, Execute operação de litert lm serve]
- id: litert-lm-info
  name: Litert Lm:Info
  description: Capacidade especializada em litert lm:info.
  tags: [litert, litert-lm-info]
  examples: [Aplique litert lm info, Execute operação de litert lm info]
- id: litert-lm-delete
  name: Litert Lm:Delete
  description: Capacidade especializada em litert lm:delete.
  tags: [litert, litert-lm-delete]
  examples: [Aplique litert lm delete, Execute operação de litert lm delete]
- id: inference-on-device
  name: Inference On Device
  description: Capacidade especializada em inference on device.
  tags: [inference, inference-on-device]
  examples: [Aplique inference on device, Execute operação de inference on device]
tags: [engineering, inference, inference-on-device, litert, litert-lm-chat, litert-lm-delete, litert-lm-import, litert-lm-info, litert-lm-list, litert-lm-run]
examples: [Execute esta tarefa conforme especificação, Analise e reporte os resultados, Aplique litert lm list, Aplique litert lm run]
type: specialist
category: engineering
---

# litert-lm-agent

**ID**: `litert-lm-agent`  
**Tipo**: Agente de inferência on-device (A2A registrado no Blackboard)  
**Skill**: `skills/litert_lm/`  
**Agente A2A**: `skills/litert_lm/agent.py::LiteRTLMAgent`  
**Especificação**: `specs/SPEC-935-R209.md`  
**Confiança**: 0.95 (Trust Engine)

---

## Descrição

Agente especializado em execução de modelos LLM on-device via **LiteRT-LM** (Google AI Edge). Capaz de baixar, gerenciar, executar e servir modelos `.litertlm` do HuggingFace com aceleração CPU/GPU/NPU.

---

## Capacidades

| Capacidade | Descrição |
|:-----------|:----------|
| `litert-lm:list` | Lista modelos disponíveis localmente |
| `litert-lm:run` | Executa prompt único em um modelo |
| `litert-lm:chat` | Sessão interativa com streaming |
| `litert-lm:import` | Download de modelos do HuggingFace |
| `litert-lm:serve` | Servidor OpenAI-compatible |
| `litert-lm:info` | Inspeção de metadados do modelo |
| `litert-lm:delete` | Remoção de modelo do cache |

---

## Exemplos de Uso

```bash
# Listar modelos
litert-lm list

# Executar prompt único
litert-lm run gemma-4-E2B-it --prompt "Qual a capital da França?"

# Chat interativo
litert-lm chat gemma-4-E2B-it

# Servidor OpenAI
litert-lm serve gemma-4-E2B-it --port 9379

# Importar do HuggingFace
litert-lm import litert-community/gemma-4-E2B-it-litert-lm
```

---

## Modelos Suportados

- **Gemma 4**: 2B, 9B, 12B (E2B, E4B com MTP)
- **Gemma 3**: 1B, 4B, 12B, 27B
- **Gemma 2**: 2B, 9B, 27B
- **Llama 4**: 17B
- **Llama 3**: 8B, 70B
- **Phi-4**: 14B
- **Qwen 2.5**: 7B, 32B

---

## Dependências

- `litert-lm >= 0.14` — SDK Python
- `click >= 8.0` — CLI framework
- `huggingface-hub` — Download de modelos
- `prompt-toolkit` — Chat interativo (opcional)

---

## TDD

Testes em `tests/test_r209_litert_lm.py` (39 cenários, cobertura ≥ 85%).
