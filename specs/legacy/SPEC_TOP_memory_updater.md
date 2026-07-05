# SPEC-TOP-008: Graph Memory Updater
Version: 1.0.0 | Domain: knowledge-graph

## Objective
Atualizacao em tempo real de grafos com atividades de agentes. Inspirado pelo GraphMemoryUpdater do MiroFish-Offline. Buffer por plataforma, envio em lote, retry e persistencia SQLite.

## Acceptance Criteria
- [x] CT-1: Updater start/stop lifecycle works
- [x] CT-2: AgentActivity.to_episode_text generates narratives
- [x] CT-3: DO_NOTHING actions are skipped
- [x] CT-4: Stats report includes total/sent/failed counts

## Assets
- scripts/memory_updater.py
- tests/test_graph_memory_updater.py
