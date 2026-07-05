# SPEC-034: ADAPTAÇÃO DO ECOSSISTEMA LOCAL OLLAMA — Modelos Customizados, Descoberta Dinâmica e TDD

**Versão:** 1.0.0  
**Data:** 2026-06-13  
**Dependências:** SPEC-024 (Audit Integration), SPEC-028 (Noological Scanner)  
**Autor:** Prof. Marcelo Claro Laranjeira | ORCID: 0000-0001-8996-2887  

---

## 1. Contexto e Objetivos

Este documento especifica a integração de 5 modelos de linguagem customizados e otimizados localmente via Ollama ao ecossistema OpenCode. O objetivo é viabilizar o processamento offline com alta acurácia acadêmica e de desenvolvimento de código, reduzindo latência e custos de nuvem de forma auditável e reprodutível.

Os objetivos específicos são:
1. **Descoberta Dinâmica:** Identificar automaticamente quais modelos locais estão instalados no serviço Ollama local (`http://127.0.0.1:11434`).
2. **Priorização Temática:** Apresentar e sugerir os modelos conforme sua especialidade.
3. **Auditabilidade de Custos:** Registrar no log de auditoria local (`session_token_audit.log`) os custos economizados em relação a APIs de nuvem proprietárias.
4. **Verificação TDD:** Garantir através de testes unitários mockados que o subsistema de descoberta e tratamento de erros é robusto e resiliente.

---

## 2. Catálogo de Modelos do Ecossistema

Cinco modelos customizados foram gerados a partir de seus respectivos Modelfiles e estão disponíveis no ecossistema:

| Modelo Ollama | Tipo | Modelo Base | Especialidade Científica |
| :--- | :--- | :--- | :--- |
| `opencode/deepseek-reasoner` | Custom (7B) | `deepseek-r1:7b` | Raciocínio científico profundo, análise de dados e atualização de dissertação. |
| `opencode/qwen-coder-pro` | Custom (7B) | `qwen2.5-coder:7b` | Geração avançada de código, refatoração e arquitetura de sistemas. |
| `opencode/phi4-orchestrator` | Custom (4B) | `phi4-mini` | Planejamento, orquestração de subagentes e tomada de decisão lógica. |
| `opencode/qwen-coder-fast` | Custom (1.5B) | `qwen2.5-coder:1.5b` | Validação rápida de sintaxe, geração de scripts temporários e testes de caixa branca. |
| `opencode/gemma-scholar` | Custom (1B) | `gemma3:1b` | Pesquisa de literatura, formatação de referências e citações acadêmicas. |

---

## 3. Arquitetura de Integração e Descoberta

A descoberta de modelos locais funciona em duas camadas de fallback:

### 3.1. Consulta à API Local (REST)
O Ollama expõe um endpoint local que retorna a lista de tags instaladas em formato JSON:
- **Endpoint:** `GET http://127.0.0.1:11434/api/tags`
- **Estrutura de Resposta:**
  ```json
  {
    "models": [
      { "name": "opencode/deepseek-reasoner:latest", ... },
      { "name": "qwen2.5-coder:1.5b", ... }
    ]
  }
  ```

### 3.2. Estrutura de Configuração (`opencode.json`)
A configuração dos modelos está formalizada no arquivo de configuração do ecossistema:
```json
  "ollama": {
    "enabled": true,
    "host": "http://127.0.0.1:11434",
    "models": {
      "opencode/deepseek-reasoner": { "type": "reasoner", "base": "deepseek-r1:7b" },
      "opencode/qwen-coder-pro": { "type": "coder-pro", "base": "qwen2.5-coder:7b" },
      ...
    }
  }
```

---

## 4. Testes e Validação (TDD)

A suite `tests/test_chat_ollama.py` foi estendida para garantir a estabilidade do processo de descoberta em ambientes isolados de teste.

### Casos de Teste Adicionados

| Identificador | Objetivo do Teste | Validação / Asserção |
| :--- | :--- | :--- |
| `test_obter_modelos_locais_mocked` | Validar a análise de resposta correta do endpoint `/api/tags`. | Mock do urllib retorna JSON simulado com 2 modelos. A lista retornada deve conter exatamente as duas strings esperadas. |
| `test_obter_modelos_locais_error_handling` | Validar a resiliência do sistema quando o serviço Ollama está offline. | Simulação de exceção de conexão no urllib. O retorno deve ser uma lista vazia (`[]`), evitando travamentos da interface do console. |

---

## 5. Auditoria de Custos e Tokenização

Cada inferência executada localmente gera métricas de auditoria para fins de reprodutibilidade científica (Qualis A1). A economia é calculada com base na estimativa de tarifas cloud padrão:

- **Tokens de Entrada (Input):** $0.15 por 1 milhão de tokens
- **Tokens de Saída (Output):** $0.60 por 1 milhão de tokens

A fórmula de economia gerada total por requisição é:
$$\text{Economia} = \left(\frac{\text{Prompt\_Tokens}}{1.000.000} \times 0.15\right) + \left(\frac{\text{Eval\_Tokens}}{1.000.000} \times 0.60\right)$$

O histórico acumulado é salvo em `docs/session_token_audit.log` sob a forma de variáveis de ambiente persistentes.
