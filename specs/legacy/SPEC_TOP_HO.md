# SPEC-TOP-HO: Handoff Document Protocol
Version: 1.0.0 | Domain: top-level | Status: active

## Objective
Produz documento de handoff estavel e legivel para o contexto do PROXIMO agente (fresh session). O artefato segue formato canonico: TL;DR + State-of-the-world (P15 snapshot) + What-was-delivered (PR table com SHAs) + First action + Pickup state.

## Canonical Shape
```markdown
# <Arc name> — <Stage / Phase>
**TL;DR.** <One-sentence summary with FIRST ACTION.>
## State of the world (P15 snapshot YYYY-MM-DD)
## What <arc> delivered (PR table with SHAs)
## E2E proof (re-runnable command)
## First action
## Pickup state (open threads)
## Related context
```

## Five Anti-Patterns
| # | Anti-Pattern | Failure Mode |
|---|-------------|--------------|
| 1 | Missing P15 snapshot | Agent reasons against stale state |
| 2 | No/vague "first action" | Agent wastes 10+ min triangulating |
| 3 | PR table without SHAs | Can't reproduce substrate state |
| 4 | Lessons buried in prose | Lessons silently lost |
| 5 | Aspirational scope | Agent thrashes on unprioritized list |

## Validation Checklist
- [ ] TL;DR is one sentence and names first action
- [ ] P15 snapshot covers every repo + long-running daemon
- [ ] PR table cites merge SHAs (not just PR numbers)
- [ ] First action is single concrete step with exact command/path
- [ ] Pickup state lists <=5 open threads

## Acceptance Criteria
- [x] CT-1: SKILL.md structure valid (frontmatter, trigger keywords)
- [x] CT-2: Canonical shape documented (TL;DR, State of world, PR table, First action, Pickup state)
- [x] CT-3: All 5 anti-patterns documented
- [x] CT-4: Validation checklist with 5 checks present
- [x] CT-5: Composition rules (persist, bookkeeping, make-spec) documented
- [x] CT-6: File placement rules documented (workspace, project-local, legacy)
- [x] CT-7: handoff-template.md reference exists
- [x] CT-8: SKILL.md > 500 chars

## Test Coverage
- Location: `skills/broomva/handoff/tests/test_handoff.py`
- Classes: 4 (Structure, AntiPatterns, Composition, Available)
- Tests: 10+
