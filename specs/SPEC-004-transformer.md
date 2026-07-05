---
spec_id: SPEC-004
component: transformer
title: Camada Transformer (Embedder, Attention, Pipeline, HTM Memory)
version: 2.0.0
status: approved
test_file: tests/test_transformer.py
---

# SPEC-004 — Camada Transformer

## Objetivo
Mapear conceitos da arquitetura Transformer (Vaswani et al. 2017) para orquestração multiagente: embeddings de tarefas, roteamento por atenção multi-cabeça, pipeline gerar→verificar→revisar (Aletheia) e memória hierárquica (HTM).

## Requisitos Funcionais

| ID | Requisito | Critério de Aceitação | Teste |
|---|---|---|---|
| RF-004.1 | Embedding determinístico | Mesmo texto → mesmo vetor d=64, L2-normalizado | `test_embedder_determinism_and_norm` |
| RF-004.2 | Roteamento por capacidade | Tarefa com capacidade `search` roteia para agente com `search` | `test_attention_routes_by_capability` |
| RF-004.3 | Softmax normalizado | Pesos de atenção somam 1.0 (±1e-6) | `test_attention_routes_by_capability` |
| RF-004.4 | Penalizar agentes ocupados | Agente `busy` perde para `available` mesmo com maior confiança | `test_attention_penalizes_busy_agents` |
| RF-004.5 | Grading em escala 0-7 | Saída vazia = 0; saída ancorada e substancial >= 5 (aprovada) | `test_grading_head_scale` |
| RF-004.6 | Ciclo gerar-verificar-revisar | Nota < 5 gera revisão; pipeline converge ou esgota camadas | `test_pipeline_generate_verify_revise` |
| RF-004.7 | Recuperação hierárquica | Consulta retorna entradas ordenadas por relevância (2 níveis) | `test_hierarchical_memory_retrieve` |

## Invariantes (Contratos)

1. **INV-004.1**: Embeddings DEVEM ter norma L2 = 1.0 (±1e-6).
2. **INV-004.2**: Os pesos das 4 cabeças de atenção DEVEM somar 1.0 (semantic 0.30 + capability 0.35 + confidence 0.25 + load 0.10).
3. **INV-004.3**: `GradingHead.grade` DEVE retornar score inteiro em [0, 7].
4. **INV-004.4**: O pipeline DEVE preservar todas as revisões (conexão residual) no resultado final.
5. **INV-004.5**: O pipeline DEVE encerrar antecipadamente (early exit) quando `passed == True`.

## Não-Objetivos
- Treinamento de pesos das cabeças de atenção (fixos nesta versão; aprendizado futuro: SPEC-008).
