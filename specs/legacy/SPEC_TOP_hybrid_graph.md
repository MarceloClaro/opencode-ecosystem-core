# SPEC-TOP-009: Hybrid Graph Retrieval
Version: 1.0.0 | Domain: knowledge-graph

## Objective
Tres estrategias complementares de busca em grafo de conhecimento. Inspirado pelo GraphTools do MiroFish-Offline. InsightForge (profundo), PanoramaSearch (amplo), QuickSearch (rapido).

## Acceptance Criteria
- [x] CT-1: quick_search returns SearchResult with facts
- [x] CT-2: insight_forge generates sub_queries
- [x] CT-3: panorama_search returns nodes+edges
- [x] CT-4: SearchResult and InsightForgeResult serialize to text

## Assets
- scripts/hybrid_search.py
- references/strategies.md
- tests/test_hybrid_graph_retrieval.py
