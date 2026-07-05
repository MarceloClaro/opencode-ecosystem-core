# SPEC-TOP-PP: Plan Protocol
Version: 1.0.0 | Domain: top-level | Status: active

## Objective
Diretrizes para criacao e gerenciamento de planos de implementacao com citacoes. Define formato canonico para YAML frontmatter, secoes Goal/Context/Phases, status markers, task numbering hierarquico e citacoes rastreaveis.

## Protocol Rules
1. YAML frontmatter with `status`, `phase`, `updated`
2. `## Goal` section (one sentence)
3. `## Context & Decisions` table with citations (`ref:delegation-id`)
4. Phases with status markers: `[COMPLETE]`, `[IN PROGRESS]`, `[PENDING]`
5. Tasks with hierarchical numbering (1.1, 1.2, 2.1)
6. Only ONE task marked `← CURRENT`
7. Citations for all research-based decisions

## Reference Files
| File | Content |
|------|---------|
| plan-format.md | Canonical plan format specification |
| state-machine.md | State machine transitions |
| citations-and-delegations.md | Citation format and delegation protocol |
| examples.md | Real-world plan examples |
| troubleshooting.md | Common issues and fixes |
| before-saving-checklist.md | Pre-save validation checklist |

## Acceptance Criteria
- [x] CT-1: SKILL.md structure valid (frontmatter, name, allowed-tools)
- [x] CT-2: All 6 reference files present with content (>30 chars each)
- [x] CT-3: Status markers documented (COMPLETE, IN PROGRESS, PENDING)
- [x] CT-4: CURRENT marker rule documented (only ONE task)
- [x] CT-5: Checklist items present in SKILL.md
- [x] CT-6: SKILL.md > 200 chars (substantial content)
- [x] CT-7: Goal section requirement documented
- [x] CT-8: Citation format (`ref:delegation-id`) documented

## Integration
- Part of the workflows category in OpenCode skills ecosystem
- Complements: SDD (Spec-Driven Development), ADR (Architecture Decision Records)
- Homepage: github.com/anomalyco/opencode

## Test Coverage
- Location: `skills/workflows/plan-protocol/tests/test_plan_protocol.py`
- Classes: 4 (Structure, Rules, References, Available)
- Tests: 10+
