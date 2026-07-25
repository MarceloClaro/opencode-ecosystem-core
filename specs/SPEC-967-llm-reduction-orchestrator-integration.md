# SPEC-967: LLM Reduction Layer — Integração ao Orquestrador

**Round**: R220 (evolution registry)
**Data**: 2026-07-25
**Status**: Implementado — 15 testes TDD verdes
**Score**: 0.94

## Objetivo

Integrar a `LLMReductionLayer` (6 componentes: Whoosh3Engine, RuleBasedRouter,
LocalClassifier, GameTheoryLocal, Jinja2Engine, DataKnowledgeHub) ao fluxo de
roteamento do `MarceloClaroOrchestrator`, de modo que:

1. Toda tarefa postada no Blackboard passe primeiro pela `LLMReductionLayer.route()`
2. Se a confiança do roteamento determinístico for **≥ 0.85**, o agente indicado
   seja usado diretamente, **evitando** a chamada ao `AttentionRouter` (LLM real)
3. Se for **< 0.85**, o fluxo cai no `AttentionRouter` como fallback
4. Estatísticas de LLM calls saved sejam acumuladas e expostas

## Critérios de Aceitação

- [ ] CA1: `MarceloClaroOrchestrator.__init__` aceita parâmetro `reduction_layer` opcional
- [ ] CA2: Se não fornecido, instancia `LLMReductionLayer()` automaticamente
- [ ] CA3: Roteamento com confiança ≥ 0.85 seleciona o agente sem passar pelo `AttentionRouter`
- [ ] CA4: Roteamento com confiança < 0.85 delega ao `AttentionRouter` como fallback
- [ ] CA5: `LLMReductionLayer.stats["total_llm_calls_saved"]` incrementa a cada roteamento bem-sucedido
- [ ] CA6: Método `get_reduction_stats()` expõe as estatísticas da camada de redução
- [ ] CA7: 100% dos testes TDD passando (RED → GREEN → REFACTOR)

## Arquivos Afetados

- `marceloclaro/orchestrator.py` — injeção da LLMReductionLayer no `_on_cfp`
- `skills/tooling/llm_reduction.py` — pequeno ajuste para expor `reduction_threshold`
- `tests/test_r54_llm_reduction_integration.py` — testes TDD

## Pipeline

```
delegate() → _on_cfp() → [NOVO] LLMReductionLayer.route(desc)
    ├─ conf ≥ 0.85 → usa agente direto → LLM calls saved++
    └─ conf < 0.85 → AttentionRouter.route() → LLM normal
```
