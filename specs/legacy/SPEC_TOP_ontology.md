# SPEC-TOP-012: Ontology Generator
Version: 1.0.0 | Domain: knowledge-graph

## Objective
Geracao automatica de ontologias para grafos de conhecimento social. Inspirado pelo OntologyGenerator do MiroFish-Offline. Analisa textos e requisitos para produzir entity_types e edge_types.

## Acceptance Criteria
- [x] CT-1: ONTOLOGY_SYSTEM_PROMPT contains knowledge graph instructions
- [x] CT-2: PERSON_FALLBACK and ORGANIZATION_FALLBACK have correct structure
- [x] CT-3: Constants MAX_TEXT/ENTITY/EDGE_TYPES defined
- [x] CT-4: SKILL.md and references exist

## Assets
- scripts/generate_ontology.py
- references/prompt-design.md
- tests/test_ontology_generator.py
