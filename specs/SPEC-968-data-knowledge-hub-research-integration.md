# SPEC-968: DataKnowledgeHub — Integração ao Pipeline de Pesquisa

**Round**: R221 (evolution registry)
**Data**: 2026-07-25
**Status**: Implementado — 11 testes TDD verdes
**Score**: 0.93

## Objetivo

Integrar o `DataKnowledgeHub` (16 fontes, 5 domínios, validação cruzada,
calibração de confiança e audit trail) ao pipeline de pesquisa acadêmica
do `ResearchHub`, de modo que:

1. Pesquisas acadêmicas incluam dados de contexto de fontes confiáveis
   (BCB/SGS, IBGE, Wikipedia, Wikidata, etc.)
2. O manifesto de pesquisa ganhe uma seção `data_knowledge` com dados
   validados e calibrados por confiança
3. Decisões de pesquisa possam ser calibradas por dados reais (não só
   por relevância textual)

## Critérios de Aceitação

- [ ] CA1: `ResearchHub.__init__` aceita parâmetro `data_hub` opcional
- [ ] CA2: Se não fornecido, obtém via `LLMReductionLayer.data_hub`
- [ ] CA3: `ResearchHub.run()` aceita `use_data_hub=True` para enriquecer
       o pipeline
- [ ] CA4: Quando `use_data_hub=True`, consulta o `DataKnowledgeHub`
       com o tema da pesquisa como query
- [ ] CA5: Resultados do DataKnowledgeHub são adicionados ao manifest
       como seção `data_knowledge`
- [ ] CA6: Cada resultado inclui `confidence` do CalibrationLayer
- [ ] CA7: 100% dos testes TDD passando

## Arquivos Afetados

- `research/hub.py` — integração do DataKnowledgeHub
- `tests/test_r55_data_knowledge_hub_research_integration.py` — testes TDD

## Pipeline

```
ResearchHub.run(use_data_hub=True) →
  1. Busca acadêmica normal (MultiSearcher)
  2. DataKnowledgeHub.search(topic) → dados de contexto
  3. CrossValidator.validate() → consenso entre fontes
  4. CalibrationLayer.calibrate() → confiança
  5. Seção data_knowledge adicionada ao manifest
```
