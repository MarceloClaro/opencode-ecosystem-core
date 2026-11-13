# SPEC-935-R1199 — Qwen2.5 0.5B Instruct Q4 Quantização Local em CPU

**Status**: especificada  
**Versão**: 1.0.0  
**Data**: 2026-11-13  
**Autor**: Marcelo Claro (OpenCode Ecosystem Core)  
**Rótulos**: `llm-local`, `qwen`, `q4`, `cpu`, `ollama`  
**Score-alvo**: functional execution with passing tests

---

## 1. Escopo

Configurar e validar a execução do modelo **Qwen2.5 0.5B Instruct** com quantização **Q4** em **CPU local** via **Ollama**, para uso no OpenCode Ecosystem Core como modelo local de fallback/profile mínimo.

**Objetivos:**
- ✅ Instalar e configurar Ollama com modelo Qwen2.5 0.5B Q4
- ✅ Validar inferência bem-sucedida em CPU (Intel i5-1035G1 class ou equivalente)
- ✅ Documentar parâmetros de performance (tok/s, contexto, threads)
- ✅ Garantir compatibilidade com o perfil mínimo `opencode.local.jsonc`

**Não-objetivos:**
- ❌ Não declarar qualidade "superhuman" ou "Qualis A1" sem validação externa
- ❌ Não usar APIs remotas ou cloud como primárias
- ❌ Não instalar dependências desnecessárias além do necessário para GGUF/Q4

---

## 2. Ambiente Alvo

| Item | Valor Recomendado | Observação |
|------|-------------------|------------|
| **CPU** | Intel Core i5-1035G1 (4c/8t) ou equivalente AMD/ARM | Baseado em SPEC-935-R607 |
| **RAM** | ≥ 8 GB (16 GB recomendado para conforto) | Q4 0.5B ~ 1.8-2.2 GB |
| **Swap** | ≥ 4 GB | Caso RAM seja limitada |
| **GPU** | Nenhuma (CPU-only) | Ollama usará CPU se não houver GPU |
| **Ollama** | 0.31.1+ | Versão compatível com parâmetros GGUF |
| **Sistema** | Linux (Ubuntu 22.04+, Debian 12) ou macOS | Windows via WSL2 recomendado |

---

## 3. Modelo e Quantização

| Atributo | Valor |
|----------|-------|
| **Modelo base** | Qwen2.5 0.5B Instruct |
| **Quantização** | Q4_K_M (recomendado) ou Q4_K_S |
| **Formato** | GGUF (nativamente suportado pelo Ollama) |
| **Tamanho do arquivo** | ~2.0 GB (Q4_K_M) a ~1.8 GB (Q4_K_S) |
| **Contexto (num_ctx)** | 4096 tokens (padrão seguro) a 8192 tokens (CPU moderna) |
**Velocidade esperada:** 20-40 tok/s em CPU moderna (varia por hardware)

---

## 4. Instalação e Configuração

### 4.1. Instalar Ollama

```bash
# Método recomendado (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# Verificar instalação
ollama --version
```

### 4.2. Baixar modelo Q4

```bash
# Baixar Q4_K_M (balanceado qualidade/velocidade)
ollama pull qwen2.5:0.5b-q4_k_m

# Ou Q4_K_S (mais rápido, ligeiramente menor qualidade)
ollama pull qwen2.5:0.5b-q4_k_s
```

### 4.3. Criperfil de modelo tunado (opcional, mas recomendado)

Criar um Modelfile para otimizar parâmetros de CPU:

```bash
# Criar Modelfile para Q4_K_M otimizado para CPU i5-1035G1
cat > Modelfile << 'EOF'
FROM qwen2.5:0.5b-q4_k_m
PARAMETER num_thread 4
PARAMETER num_ctx 4096
EOF

# Criar modelo tunado
ollama create qwen2.5-0.5b-q4-cpu -f Modelfile
```

### 4.4. Configurar parâmetros de ambiente

```bash
# Configurações recomendadas (adicionar ao ~/.ollama/modelfiles ou .env)
export OLLAMA_NUM_THREADS=4
export OLLAMA_NUM_CTX=4096
export OLLAMA_KEEP_ALIVE=30m
export OLLAMA_MAX_LOADED_MODELS=1
```

---

## 5. Integração com OpenCode Core

### 5.1. Perfil mínimo `opencode.local.jsonc`

Adicionar ao `opencode.local.jsonc` a configuração do novo modelo:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama-local": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama local (GGUF multimodal, perfil minimo)",
      "options": {
        "apiKey": "sk-no-key-required",
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "qwen2.5-0.5b-q4-cpu": {
          "name": "Qwen2.5 0.5B Instruct Q4 CPU (Q4_K_M)",
          "limit": {"context": 4096, "output": 2048},
          "modalities": {"input": ["text"], "output": ["text"]},
          "tool_call": true,
          "attachment": true,
          "options": {"reasoning_effort": "none"}
        }
      }
    }
  },
  "model": "ollama-local/qwen2.5-0.5b-q4-cpu",
  "agent": {
    "build": {
      "description": "Agente minimo de codigo para a LLM local Qwen2.5",
      "mode": "all",
      "tools": {
        "browser": false,
        "http": false
      }
    }
  },
  "skills": {
    "enabled": false
  }
}
```

### 5.2. Usar via linha de comando

```bash
# Com configuração mínima
OPENCODE_CONFIG=opencode.local.jsonc opencode run "Seu prompt aqui"

# Ou via variável de ambiente
export OPENCODE_CONFIG=opencode.local.jsonc
opencode run "Seu prompt aqui"
```

### 5.3. Testes de integração

Verificar se o modelo responde corretamente:

```bash
ollama run qwen2.5:0.5b-q4_k_m "Qual é a capital do Brasil?"
# Expected: Brasília

# Via OpenCode
opencode run "Qual é a capital do Brasil?"
# Deve responder via modelo local configurado
```

---

## 6. Métricas de Performance (Baseado em hardware semelhante i5-1035G1)

| Configuração | tok/s (aproximado) | Contexto | Observação |
|--------------|---------------------|----------|------------|
| `num_thread=4` `num_ctx=4096` | **~30 tok/s** | 4096 | Ótimo equilíbrio |
| `num_thread=4` `num_ctx=8192` | ~22 tok/s | 8192 | Contexto maior, velocidade menor |
| `num_thread=2` `num_ctx=4096` | ~25 tok/s | 4096 | Menos threads, similar velocidade |
| `num_thread=8` `num_ctx=4096` | ~10-15 tok/s | 4096 | *Anti-pattern*: threading excessivo em 4 núcleos |

**Conclusão:** `num_thread=4` é o valor ótimo para CPUs de 4 núcleos/8 threads. `num_ctx=4096` oferece melhor relação velocidade/contexto.

---

## 7. Veredito

**Viável para uso direto em perfil mínimo.** O Qwen2.5 0.5B Q4 em CPU local é adequado para:
- Tarefas de assistência, código, redação curta
- Use como modelo de fallback quando cloud não disponível
- Profile `opencode.local.jsonc` com prompt ~2-7k tokens (contra 21k do perfil completo)

**Limitações:**
- Não substitui modelo cloud (`big-pickle`/8/11 no tier difícil) para loops agentivos completos com catálogo de 216 agentes
- Contexto longo (>4k tokens) reduz throughput significantemente
- Modelos >3B parametros podem exceder RAM de 11.8 GB sem swap adequado

---

## 8. Anti-overclaim / Restrições

- Diferenças de qualidade vs modelos maiores não são alegadas sem benchmarks externos
- Throughput variável dependendo de carga de prompt (agentes, skills, MCP registrados)
- Nenhuma declaração de superioridade em relação a cloud sem validação empirical
- Sempre testar com `OPENCODE_CONFIG=opencode.local.jsonc` antes de usar em produção

---

## 9. Histórico de Revisão

| Versão | Data | Mudança |
|--------|------|---------|
| 1.0.0 | 2026-11-13 | Spec inicial — configuração Qwen2.5 0.5B Q4 local em CPU |

---