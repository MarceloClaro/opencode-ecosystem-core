# SPEC-933: Refinamento Jurídico do MetaBus

```yaml
spec_id: SPEC-933
title: Refinamento do MetaBus para eventos jurídicos, confiança por domínio e memória semântica especializada
version: 1.0.0
status: active
owner: marceloclaro
depends_on: [SPEC-924, SPEC-927, SPEC-932, SPEC-001]
origin: pedido do usuário para refinar o MetaBus junto com a expansão jurídica da webapp
```

**STATUS**: IMPLEMENTADO  
**DATA**: 2026-07-08  
**AUTOR**: marceloclaro  
**VERSÃO**: 1.0

## 1. Objetivo

Refinar o `MetaBus` para suportar melhor o subsistema jurídico, adicionando:

- eventos jurídicos especializados;
- leitura filtrada de eventos recentes;
- memória semântica incremental por tópico;
- confiança por domínio jurídico.

## 2. Escopo

### 2.1 Memória

- `upsert_semantic_topic(topic, lesson, metadata)`
- `update_domain_confidence(domain_id, score)`

### 2.2 Barramento de eventos

- `publish_legal_event(event_name, domain_id, payload, source_agent)`
- `get_recent_events(limit, topic_prefix, source)`

### 2.3 Integração

- `MarceloClaroOrchestrator.diagnose(..., include_legal_impact=True)` publica evento jurídico e atualiza confiança por domínio.

## 3. Critérios de Aceitação (TDD)

1. `publish_legal_event()` publica tópico prefixado com `legal.`
2. `get_recent_events()` filtra por prefixo e source
3. `upsert_semantic_topic()` acumula lições sem apagar as anteriores
4. `update_domain_confidence()` atualiza o ledger para `legal:<domain_id>`
5. `orchestrator.diagnose()` com `include_legal_impact=True` registra evento jurídico no MetaBus

## 4. Resultado Esperado

O MCI passa a observar e lembrar melhor o comportamento jurídico do ecossistema, tornando a camada legal não apenas funcional, mas **metacognitivamente rastreável por domínio**.
