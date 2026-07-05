# SPEC-TOP-005: Entity NER Reader
Version: 1.0.0 | Domain: knowledge-graph

## Objective
Leitura e filtragem de entidades em grafos de conhecimento. Inspirado pelo EntityReader do MiroFish-Offline. Modos: list, filter, context, stats.

## Acceptance Criteria
- [x] CT-1: filter_defined_entities returns correct counts
- [x] CT-2: get_entities_by_type filters by Person
- [x] CT-3: get_entity_with_context returns edges and related nodes
- [x] CT-4: refine_graph bridge creates entity tables

## Assets
- scripts/entity_reader.py
- scripts/refine_graph.py
- tests/test_entity_ner_reader.py
