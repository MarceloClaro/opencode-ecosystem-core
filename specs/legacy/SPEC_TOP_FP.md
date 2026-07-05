# SPEC-TOP-FP: Frontend Philosophy (5 Pillars of Intentional UI)
Version: 1.0.0 | Domain: top-level | Status: active

## Objective
Filosofia visual e de UI definindo os 5 Pilares da UI Intencional. Fornece checklist de aderencia e guia de referencia para construcao de interfaces consistentes e propositais.

## Reference Files
| File | Content |
|------|---------|
| the-5-pillars.md | Os 5 Pilares da UI Intencional |
| adherence-checklist.md | Checklist de aderencia aos pilares |

## Acceptance Criteria
- [x] CT-1: SKILL.md structure valid (frontmatter, name, version, allowed-tools)
- [x] CT-2: Reference directory contains the-5-pillars.md and adherence-checklist.md
- [x] CT-3: SKILL.md references the 5 pillars by name or path
- [x] CT-4: Allowed tools specified in SKILL.md
- [x] CT-5: No empty .md files in directory tree
- [x] CT-6: SKILL.md > 100 chars (has content)

## Integration
- Part of the frontend category in OpenCode skills ecosystem
- Complements: html-ppt, web-prototype, open-design-landing skills
- Homepage: github.com/anomalyco/opencode

## Test Coverage
- Location: `skills/frontend/frontend-philosophy/tests/test_frontend_philosophy.py`
- Classes: 4 (Structure, References, Content, Available)
- Tests: 8+
