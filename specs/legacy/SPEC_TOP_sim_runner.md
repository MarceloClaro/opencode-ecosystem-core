# SPEC-TOP-014: Simulation Runner
Version: 1.0.0 | Domain: simulation

## Objective
Motor de simulacao multiagente local (P20). Supera o MiroFish original com milhares de agentes, multi-rodada, Teoria dos Jogos, emergencia coletiva, persistencia SQLite. BRAZIL_TZ timezone.

## Acceptance Criteria
- [x] CT-1: AgentState/ActionType/Sentiment enums defined
- [x] CT-2: AgentMemory dataclass has correct defaults
- [x] CT-3: BRAZIL_TZ offset is UTC-3
- [x] CT-4: Core module files exist (sim_engine, profile_manager, etc.)

## Assets
- scripts/sim_engine.py
- scripts/profile_manager.py
- scripts/llm_discourse.py
- scripts/multiagent_warroom.py
- scripts/omen_engine.py
- scripts/countermeasures.py
- scripts/diagnostic_analyzer.py
- scripts/expanded_profiles.py
- scripts/graph_decision_engine.py
- scripts/mirofish_omni.py
- scripts/rigorous_ml_pipeline.py
- scripts/transformer_orchestrator.py
- tests/test_simulation_runner.py
