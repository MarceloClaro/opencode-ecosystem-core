# SPEC-934: Integração Pervasiva ao MetaBus para Orquestração Consciente

```yaml
spec_id: SPEC-934
title: Integração transversal de reasoning, scanners, agents, specs, research, publishing e subsistemas científicos ao MetaBus + Transformer
version: 1.0.0
status: active
owner: marceloclaro
depends_on: [SPEC-001, SPEC-002, SPEC-004, SPEC-005, SPEC-009, SPEC-920, SPEC-924, SPEC-933]
origin: pedido do usuário para sincronizar noológico, mci, oqs, vsee, egs, scientific rag, superhuman suite, metacognitive eval, mirofish, game theory, publishing e research ao MetaBus com orquestração mais consciente
```

**STATUS**: IMPLEMENTADO  
**DATA**: 2026-07-08  
**AUTOR**: marceloclaro  
**VERSÃO**: 1.0

## 1. Objetivo

Tornar a orquestração do ecossistema **mais consciente, refinada e rastreável**, conectando transversalmente os principais subsistemas ao `MetaBus` e à memória do `MCI`, de forma que produzam telemetria, memória episódica/semântica, confiança por tópico e eventos observáveis pelo restante da arquitetura.

## 2. Escopo

### 2.1 Subsistemas-alvo

- reasoning
- scanners / noological / oqs / vsee / egs
- scientific rag
- superhuman readiness suite
- metacognitive evaluator
- mirofish / game theory
- publishing
- research
- sdd/specs

### 2.2 Capacidades novas

1. `publish_subsystem_event(subsystem, event_name, payload, source_agent)`
2. `update_topic_confidence(topic_key, score)`
3. `search_memory(query, limit)`
4. eventos publicados por wrappers principais dos subsistemas
5. reflexões/semântica incremental por subsystem-topic

## 3. Critérios de Aceitação (TDD)

1. OQS publica evento no MetaBus
2. VSEE publica evento no MetaBus
3. EGS publica evento no MetaBus
4. ScientificRAG publica evento ao responder
5. Superhuman suite publica evento ao finalizar
6. MiroFish publica evento de predição
7. SpecRegistry/SpecVerifier publicam eventos SDD
8. `search_memory()` encontra reflexões/semântica relevantes

## 4. Resultado Esperado

O ecossistema passa a operar menos como um conjunto de módulos isolados e mais como um **organismo metacognitivo integrado**, com melhor memória, telemetria, busca de contexto e confiança por tópico/subsistema.
