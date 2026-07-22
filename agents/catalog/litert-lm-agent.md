# litert-lm-agent

**ID**: `litert-lm-agent`  
**Tipo**: Agente de inferência on-device  
**Skill**: `skills/litert_lm/`  
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
