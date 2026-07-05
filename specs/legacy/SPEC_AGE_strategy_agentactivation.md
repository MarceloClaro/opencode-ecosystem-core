# SPEC-AGE-012: AgentActivationEngine
Version: 1.0.0 | Status: verified | TDD: verified | Domain: strategy

## Objective
Prompt template engine for NEXUS agent activation. Resolves role-specific prompts by division, interpolates placeholders, and supports NEXUS-Full/Sprint/Micro pipeline modes.

## Acceptance Criteria
- [x] CT-1: `test_known_agent` — resolve_prompt para `Frontend Developer` na fase Build inclui nome do agente e placeholder `[PROJECT NAME]`
- [x] CT-2: `test_full_mode` — get_orchestrator_prompt modo NEXUS-Full referencia pipeline 7-phase
- [x] CT-3: `test_all_placeholders_replaced` — interpolate substitui todos os placeholders fornecidos e nao deixa residuos
- [x] CT-4: `test_returns_divisions` — list_supported_agents retorna divisoes Engineering e Product com agentes populados

## Engine
<scripts/agent_activation_engine.py> -> AgentActivationEngine

## Test Results
All CTs PASSED
