# SPEC-TOP-DL: Decision Log
Version: 1.0.0 | Domain: top-level | Status: active

## Objective
Captura decisoes com contexto, alternativas consideradas e racional, vinculando ao documento de projeto relevante no vault. Cria registro pesquisavel de decisoes para auditoria futura.

## Workflow
1. **Capture the decision** — What was decided, context, alternatives
2. **Document rationale** — Why chosen, trade-offs, constraints
3. **Assess each alternative** — Pros/cons, why rejected, reconsideration conditions
4. **Identify consequences** — Immediate actions, long-term implications, reversibility (one-way / two-way door), review trigger
5. **Link to project** — Vault docs, prior decisions, people involved

## Output Template Fields
| Field | Required | Description |
|-------|----------|-------------|
| date | Yes | YYYY-MM-DD |
| status | Yes | decided / proposed / superseded |
| project | Yes | [[Project Name]] |
| decision-makers | Yes | List of people |
| reversibility | Yes | one-way-door / two-way-door |
| review-by | Yes | Date or trigger condition |
| tags | Yes | decision, project-name, topic |

## Acceptance Criteria
- [x] CT-1: SKILL.md structure valid (frontmatter, name, all required template fields)
- [x] CT-2: Alternatives section documented in template
- [x] CT-3: Consequences section documented in template
- [x] CT-4: Alternatives rule documented (never skip alternatives)
- [x] CT-5: Reversibility concept (one-way vs two-way door) documented
- [x] CT-6: Vault integration documented (save path)
- [x] CT-7: SKILL.md > 300 chars (substantial content)
- [x] CT-8: Frontmatter valid (3+ YAML sections)

## Behavioral Rules
- Don't skip alternatives — even "nothing else" is worth recording
- Capture emotional/political context if shared
- For one-way-door decisions, emphasize review trigger
- Keep factual — record, not advocacy

## Test Coverage
- Location: `skills/broomva/decision-log/tests/test_decision_log.py`
- Classes: 4 (Structure, Template, Behavior, Available)
- Tests: 10+
