# Component Registry — OpenCode Ecosystem v4.2

> "A manutencao consome 67% do custo total. Sem registro, planejar manutencao e impossivel." — Cap. 4

Registro central de todos os componentes do ecossistema com classificacao SWEBOK de manutencao. Atualizar a cada novo componente.

**Total:** 235+ componentes (118 agentes, 74 skills, 23 plugins, 20 MCPs, ~15 comandos)
**Ultima atualizacao:** 2026-05-27
**Cobertura:** Parcial (skills superpowers + core components)

---

## Core Components (Python)

| ID | Componente | Status | SWEBOK | Freq. Mudanca | Dependencias | Testes |
|----|-----------|--------|--------|--------------|-------------|--------|
| core-agent-manager | core/agent_manager.py | active | evolutiva | media | errors, DI | test_agent_manager.py |
| core-state-manager | core/state_manager.py | active | adaptativa | baixa | config, state, state_file | test_state_manager.py, test_unified_state_manager.py |
| core-plugin-manager | core/plugin_manager.py | active | evolutiva | media | errors, DI | test_plugin_manager.py, plugin.test.ts |
| core-task-queue | core/task_queue.py | active | evolutiva | media | errors | test_task_queue.py |
| core-errors | core/errors.py | active | adaptativa | baixa | — | — |
| core-validators | core/validators.py | active | corretiva | baixa | — | test_validators.py |
| core-cache | core/cache.py | active | adaptativa | baixa | — | test_cache.py |
| core-rest-client | core/rest_client.py | active | adaptativa | baixa | — | test_rest_client.py |
| core-services-evolution | core/services/evolution.py | active | evolutiva | alta | agent_manager, state_manager | test_services.py |
| core-services-health | core/services/health.py | active | preventiva | media | agent_manager, state_manager | test_services.py |

## Skills — Superpowers

| ID | Skill | Versao | Status | SWEBOK | Dependencias | Spec |
|----|-------|--------|--------|--------|-------------|------|
| skill-ai-eng-harness | ai-engineering-harness | 1.0.0 | active | evolutiva | using-git-worktrees, tdd, subagent-driven, verification | inline SKILL.md |
| skill-maintenance-first | maintenance-first | 1.0.0 | active | preventiva | ai-eng-harness, tdd, code-review | inline SKILL.md |
| skill-git-worktrees | using-git-worktrees | 2.0.0 | active | adaptativa | subagent-driven | inline SKILL.md |
| skill-tdd | test-driven-development | 1.0.0 | active | preventiva | — | inline SKILL.md |
| skill-subagent | subagent-driven-development | 1.0.0 | active | evolutiva | — | inline SKILL.md |
| skill-verification | verification-before-completion | 1.0.0 | active | corretiva | — | inline SKILL.md |
| skill-writing-plans | writing-plans | 1.0.0 | active | evolutiva | — | — |
| skill-executing-plans | executing-plans | 1.0.0 | active | evolutiva | writing-plans | — |
| skill-brainstorming | brainstorming | 1.0.0 | active | evolutiva | — | — |
| skill-code-review-req | requesting-code-review | 1.0.0 | active | corretiva | — | — |
| skill-finishing-branch | finishing-a-development-branch | 1.0.0 | active | adaptativa | using-git-worktrees | — |
| skill-systematic-debug | systematic-debugging | 1.0.0 | active | corretiva | — | — |

## Skills — System

| ID | Skill | Versao | Status | SWEBOK | Dependencias | Spec |
|----|-------|--------|--------|--------|-------------|------|
| skill-code-review | code-review | 2.1.0 | active | corretiva | — | inline SKILL.md |
| skill-reasoning-orch | reasoning-orchestrator | 9.0.0 | active | evolutiva | token-efficiency | inline SKILL.md |
| skill-reasoning-v11 | reasoning-orchestrator-v11 | 11.0.0 | active | evolutiva | cora-debate | inline SKILL.md |
| skill-token-efficiency | token-efficiency | 1.0.0 | active | preventiva | — | — |
| skill-self-heal | self-heal | 1.0.0 | active | corretiva | health | — |
| skill-skill-creator | skill-creator | 1.0.0 | active | evolutiva | SKILL_TEMPLATE.md | — |
| skill-plan-review | plan-review | 1.0.0 | active | corretiva | — | — |
| skill-evo-11 | evo-11-autonomous-operation | 1.0.0 | active | evolutiva | — | — |
| skill-philosophy | philosophy-enforcement | 1.0.0 | active | preventiva | — | — |
| skill-code-philosophy | code-philosophy | 1.0.0 | active | preventiva | — | — |
| skill-academic-audit | academic-audit | 1.0.0 | active | corretiva | — | — |

## ADRs

| ID | Titulo | Status | Data |
|----|--------|--------|------|
| ADR-001 | Token Budget Rigido para Skills | active | 2026-05-27 |
| ADR-002 | Arquitetura em 3 Camadas | active | 2026-05-27 |
| ADR-006 | Spec-First para Novas Skills | active | 2026-05-27 |
| ADR-007 | CI Pipeline com Spec Coverage Gate | proposed | 2026-05-27 |
| ADR-008 | Component Registry com SWEBOK | proposed | 2026-05-27 |

## Specs

| ID | Spec | Status | Cobre |
|----|------|--------|-------|
| spec-agent-manager | specs/core/agent-manager.md | active | core/agent_manager.py |
| spec-state-manager | specs/core/state-manager.md | active | core/state_manager.py |
| spec-plugin-manager | specs/core/plugin-manager.md | active | core/plugin_manager.py |
| spec-ci-pipeline | specs/integration/ci-pipeline.md | proposed | CI pipeline |
| spec-test-harness | specs/integration/test-harness.md | proposed | Testes de integracao |

---

## Metricas de Cobertura

| Metrica | Valor | Alvo | Status |
|---------|-------|------|--------|
| Core components com spec | 3/10 (30%) | 100% | 🔴 |
| Skills superpowers com spec | 6/12 (50%) | 100% | 🟡 |
| ADRs documentadas | 5 | — | 🟢 |
| Componentes no registry | 22 | 235+ | 🔴 |
| Testes de integracao | 0 cenarios | 10+ | 🔴 |
| CI pipeline | proposto | ativo | 🟡 |
