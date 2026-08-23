---
spec_id: SPEC-935-R441
title: Amplificação Cognitiva de Modelos Free via DeepSeek Harness
component: integrations/deepseek_harness, rag, marceloclaro/orchestrator, doctor, cli
status: verified
test_file: tests/test_r441_deepseek_harness_amplification.py
---

# SPEC-935-R441 — Amplificação Cognitiva de Modelos Free via DeepSeek Harness

## 1. Contexto e Motivação

O OpenCode Ecosystem oferece acesso a modelos gratuitos e ilimitados (como **Ox Alpha Free / Unlimited**, `deepseek-free`, `qwen-2.5-coder-free`, `gemma-4-e2b-it`, `llama-3.2-3b`, `colibri-olmoe`). No entanto, modelos compactos ou gratuitos de inferência padrão frequentemente sofrem de:
1. Menor profundidade de raciocínio passo a passo (ausência de *test-time compute* / cadeia de pensamento estruturada).
2. Janela de contexto efetiva limitada e alucinações factuais por falta de *grounding*.
3. Ausência de ciclo de auto-correção e verificação reflexiva pós-geração.

Esta especificação define o **Sistema de Amplificação Cognitiva DeepSeek Harness**, integrando o repositório `https://github.com/MarceloClaro/deepseek-harness` ao OpenCode Ecosystem Core para elevar a qualidade de resposta de modelos gratuitos ao nível de raciocínio profundo de modelos de fronteira (*frontier reasoning*), combinando:
- **Scaffolding de Raciocínio Profundo** (emulação de `<think>` com decomposição lógica e testes de borda).
- **Expansão de Contexto e RAG Multi-Fonte com Custo Zero** (Whoosh3 BM25F local + DataKnowledgeHub + EnhancedSearchRAG + MetaBus).
- **Cadeia de Verificação e Auto-Correção Iterativa (CoVe 97%+)** com grading head.
- **Roteamento Transparente para Modelos Free** (`ox-alpha-free`, `deepseek-v3`, `colibri`, `litert-lm`).

## 2. Componentes e Contratos

### C1 — `ContextAmplifier` (`free_model_amplifier.py`)
| Método | Contrato |
|---|---|
| `expand_context(query, max_tokens=4000, sources=...)` | Realiza busca federada no Whoosh3 local (0 LLM), DataKnowledgeHub, MetaBus e buscas acadêmicas, ranqueando e destilando evidências relevantes com citações. |
| `format_grounding_block(retrieved_docs)` | Formata as evidências em bloco canônico `### Contexto Aumentado (Grounded Knowledge Base)`. |

### C2 — `ReasoningScaffoldEngine` (`free_model_amplifier.py`)
| Método | Contrato |
|---|---|
| `build_amplified_prompt(prompt, task_type, context, depth)` | Constrói meta-prompt com diretrizes rigorosas de raciocínio passo a passo, identificação de premissas, hipóteses alternativas e verificação de consistência. |
| `extract_thinking_trace(response_text)` | Separa de forma determinística o bloco `<think>...</think>` da resposta final. |

### C3 — `ChainOfVerification` (CoVe) (`free_model_amplifier.py`)
| Método | Contrato |
|---|---|
| `verify_and_refine(draft_response, context, runner)` | Gera perguntas de checagem factual/lógica, valida contra as evidências e refina a resposta final eliminando inconsistências. |

### C4 — `DeepSeekFreeModelHarness` (Fachada Principal)
| Método | Contrato |
|---|---|
| `amplify(prompt, model="ox-alpha-free", task_type="general", iterations=2, use_rag=True, runner=None)` | Orquestra o ciclo completo de amplificação cognitiva, retornando resposta fundamentada, score de confiança e métricas de execução. |
| `is_free_model(model_name)` | Identifica se um modelo pertence à categoria free/unlimited. |

### C5 — Integração com `MarceloClaroOrchestrator`, `CLI` e `Doctor`
- `MarceloClaroOrchestrator.amplify_free_model_response(...)`: Método de primeira classe no orquestrador primário.
- `python3 -m marceloclaro.cli amplify "<prompt>" [--model ox-alpha-free] [--rag] [--iterations N]`: Comando direto via terminal.
- `marceloclaro.doctor`: Check `free_model_amplification` validando disponibilidade do harness e dos índices locais.

## 3. Critérios de Aceite (CAs)

- **CA1 — RAG e Expansão de Contexto Local**: Recuperação precisa de documentos via Whoosh3 e DataKnowledgeHub sem chamadas pagas de LLM.
- **CA2 — Scaffolding de Raciocínio DeepSeek**: Geração de prompts estruturados com divisão clara de fase de pensamento (`<think>`) e resposta final.
- **CA3 — Auto-Correção e Verificação Iterativa**: Refinamento de respostas candidatas com cálculo de confiança ($\ge 0.90$).
- **CA4 — Suporte Nativo a `ox-alpha-free` e Catálogo Free**: Roteamento e enriquecimento automático de modelos gratuitos.
- **CA5 — Integração com Orquestrador e CLI**: Métodos públicos no orquestrador e comandos na CLI funcionando perfeitamente.
- **CA6 — Diagnóstico no Doctor**: Check `free_model_amplification` reportando `pass` no `python3 -m marceloclaro.cli doctor`.
- **CA7 — Testes TDD 100% Verificados**: Suíte `tests/test_r441_deepseek_harness_amplification.py` verde.
