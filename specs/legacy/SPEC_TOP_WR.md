# SPEC-TOP-WR: Weekly Review Scanner
Version: 1.0.0 | Domain: top-level | Status: active

## Objective
Escaneia o vault e atividade git da ultima semana, identifica o que mudou, destaca itens que precisam de atencao e gera prioridades para a proxima semana. Produz revisao estruturada escaneavel em menos de 3 minutos.

## Six-Step Workflow
1. **Scan vault changes** — Files in `~/broomva-vault/` modified in last 7 days
2. **Scan git activity** — `git log --since="7 days ago"` across all repos
3. **Extract completed items** — `[x]` tasks with recent modification dates
4. **Find open items** — Overdue tasks, stale PRs/branches, urgency markers
5. **Identify themes** — Most-attention projects, new ideas, silent projects
6. **Generate next week's priorities** — From unfinished items, deadlines, momentum

## Output Sections
| Section | Content |
|---------|---------|
| Week at a Glance | Commits, notes created/modified, tasks completed/open |
| What Got Done | Completed items with project links |
| What's Still Open | Overdue, In Progress, Stalled |
| Project Activity | Table: Project, Commits, Notes, Status |
| Themes & Observations | Dominant patterns, surprises, watch items |
| Next Week's Priorities | 1-3 priorities with reasons |
| Carry-Forward | Items that must continue |

## Behavioral Rules
- Be factual — don't editorialize
- Highlight slipped items without judgment
- Priorities should emerge from data, not be invented
- If vault sparse, focus on git activity
- Keep review scannable in under 3 minutes

## Acceptance Criteria
- [x] CT-1: SKILL.md structure valid (frontmatter, workflow steps)
- [x] CT-2: Week at a Glance section with commits/notes/tasks metrics
- [x] CT-3: Next Week's Priorities section documented
- [x] CT-4: Project Activity table with status column
- [x] CT-5: Data-driven priorities rule documented ("emerge from data")
- [x] CT-6: Git activity fallback when vault sparse
- [x] CT-7: Scannability requirement (3 minutes) documented
- [x] CT-8: SKILL.md > 300 chars, vault integration documented

## Vault Integration
- Save to: `~/broomva-vault/reviews/weekly-review-[YYYY-MM-DD].md`
- Link back to project notes referenced
- Reference prior weekly review for continuity

## Test Coverage
- Location: `skills/broomva/weekly-review/tests/test_weekly_review.py`
- Classes: 4 (Structure, Format, Behavior, Available)
- Tests: 10+
