# SPEC-TOP-SU: Stakeholder Update Generator
Version: 1.0.0 | Domain: top-level | Status: active

## Objective
Transforma um conjunto de fatos de projeto em tres versoes especificas para audiencia: tecnica (engenharia), impacto de negocios (lideranca) e voltada ao cliente (equipes de sucesso). Cada versao deve ser autonoma e usar o nivel de formalidade adequado.

## Three Versions
| Version | Audience | Focus |
|---------|----------|-------|
| Technical | Engineering | Implementation details, PRs, tech debt, performance |
| Business | Leadership | Revenue impact, risk reduction, strategic alignment, timeline |
| Customer-Facing | Success Teams | User benefit, UX changes, action items, talking points |

## Workflow
1. **Gather facts** — Raw project facts (bullets, PR desc, conversation, vault note)
2. **Extract core** — What changed, why it matters, what's next, risks/blockers
3. **Generate three versions** — Each standalone, audience-appropriate

## Behavioral Rules
- Never invent facts — only reframe what's provided
- If input too sparse, ask for more context
- Each version must stand alone
- Match formality level to audience
- Save to vault: `vault/updates/stakeholder-[topic]-[YYYY-MM-DD].md`

## Acceptance Criteria
- [x] CT-1: SKILL.md structure valid (frontmatter, three version templates)
- [x] CT-2: Technical version template references code/PRs/commits
- [x] CT-3: Business version template references metrics/revenue/timeline
- [x] CT-4: Customer version template references user benefits/talking points
- [x] CT-5: "Never invent facts" rule documented
- [x] CT-6: Standalone requirement documented
- [x] CT-7: Vault save path documented
- [x] CT-8: SKILL.md > 200 chars, trigger keywords present

## Test Coverage
- Location: `skills/broomva/stakeholder-update/tests/test_stakeholder_update.py`
- Classes: 4 (Structure, Versions, Behavior, Available)
- Tests: 10+
