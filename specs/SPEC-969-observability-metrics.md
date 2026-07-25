# SPEC-969: Observabilidade — Métricas e Endpoints de Saúde

**Round**: R222 (evolution registry)
**Data**: 2026-07-25
**Status**: Implementado — 20 testes TDD verdes
**Score**: 0.95

## Objetivo

Implementar observabilidade básica no ecossistema OpenCode Core:
coleta de métricas da LLM Reduction Layer, DataKnowledgeHub e
Orquestrador, expostas via:
1. Comando CLI `/metrics`
2. Endpoint HTTP `/health` e `/metrics` (servidor leve embutido)
3. Seção no Doctor (`diagnóstico`)

## Critérios de Aceitação

- [ ] CA1: `MetricsCollector` coleta stats de LLMReductionLayer
- [ ] CA2: `MetricsCollector` coleta stats de DataKnowledgeHub
- [ ] CA3: `MetricsCollector` coleta stats do Orquestrador (incluindo _llm_calls_saved)
- [ ] CA4: `MetricsCollector.render()` retorna texto formatado para terminal
- [ ] CA5: `MetricsCollector.to_dict()` retorna dict aninhado para API
- [ ] CA6: Servidor HTTP leve (`/health` e `/metrics`) opcional
- [ ] CA7: Doctor inclui seção de métricas de redução LLM
- [ ] CA8: 100% dos testes TDD passando

## Arquivos Afetados

- `marceloclaro/metrics.py` — MetricsCollector e servidor HTTP
- `marceloclaro/doctor.py` — seção de métricas de redução LLM
- `marceloclaro/cli.py` — novo comando `/metrics`
- `marceloclaro/orchestrator.py` — expor `get_metrics()`
- `tests/test_r56_observability_metrics.py` — testes TDD
