# SPEC-SYS-CODE_REVIEW: code-review
Version: 1.0.0 | Domain: system

## Objective
Metodologia abrangente de revisao de codigo com classificacao de gravidade e limites de confianca. Revisao sistematica em 4 camadas com threshold de confianca >= 80%. Inclui referencias a arquivos de processo de revisao.

## Acceptance Criteria
- [x] CT-1: SKILL.md exists with valid frontmatter (name, category, version, kind, allowed-tools)
- [x] CT-2: category declared as "system"
- [x] CT-3: version field present ("1.0.0" root, "2.1.0" metadata)
- [x] CT-4: references 7 external files (review-layers, severity-classification, confidence-threshold, review-process, output-format, what-not-to-do, adherence-checklist)
