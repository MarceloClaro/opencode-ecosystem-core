# SPEC-TOP-PM: Premortem Analysis
Version: 1.0.0 | Domain: top-level | Status: active

## Objective
Executa premortem em qualquer plano, lancamento, produto, contratacao, estrategia ou decisao. Assume que ja falhou daqui a 6 meses e trabalha de tras para frente para encontrar todas as razoes. Produz plano revisado com pontos cegos expostos.

## Method Attribution
- **Gary Klein** (1998-2007): Premortem technique, Harvard Business Review
- **Daniel Kahneman** (2011): Popularized in Thinking, Fast and Slow
- **Ole Lehmann** (2026-05-02): AI-skill formulation, parallel sub-agents, HTML report
- **Broomva Stack**: Bundled into strategy-skills Layer 7

## Six-Step Workflow
1. **Set the frame** — "It's 6 months from now. This has failed."
2. **Generate failure reasons** — Raw premortem, comprehensive, specific
3. **Deep-dive agents** — One sub-agent per failure reason, all in parallel
4. **Synthesis** — Most likely failure, most dangerous, hidden assumption, revised plan, checklist
5. **Generate report** — HTML report with dark theme, visual cards, severity indicators
6. **Save transcript** — Full Markdown transcript for reference

## Synthesis Components
1. **Most Likely Failure** — Most probable scenario
2. **Most Dangerous Failure** — Highest impact scenario
3. **Hidden Assumption** — Biggest unquestioned assumption
4. **Revised Plan** — Concrete changes, map to failure scenarios
5. **Pre-Launch Checklist** — 3-5 verifiable items

## Output Files
- `premortem-report-[timestamp].html` — Visual report
- `premortem-transcript-[timestamp].md` — Full transcript

## Acceptance Criteria
- [x] CT-1: SKILL.md structure valid (frontmatter, trigger keywords)
- [x] CT-2: 6 workflow steps documented (at least 4/6 detected)
- [x] CT-3: Output files defined (.html report + .md transcript)
- [x] CT-4: Synthesis components documented (Most Likely, Hidden Assumption, Revised Plan, Checklist)
- [x] CT-5: Attribution chain present (Klein → Kahneman → Lehmann → Broomva)
- [x] CT-6: Context threshold rule documented (minimum bar)
- [x] CT-7: Bad premortem targets documented (vague ideas, creative feedback)
- [x] CT-8: SKILL.md > 800 chars

## Test Coverage
- Location: `skills/broomva/premortem/tests/test_premortem.py`
- Classes: 4 (Structure, Workflow, Rules, Available)
- Tests: 10+
