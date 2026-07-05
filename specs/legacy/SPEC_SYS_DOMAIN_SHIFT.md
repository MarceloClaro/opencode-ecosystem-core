# SPEC-SYS-DOMAIN_SHIFT: domain-shift-camada1b
Version: 1.0.0 | Domain: system

## Objective
Deteccao de Domain Shift em corpora multi-institucionais. Distingue 'padrao real que evoluiu' de 'domain shift que invalida a comparacao' usando decomposicao em 3 deltas de Jaccard (temporal, cross-inst, confundido) com limiares calibrados por bootstrap. Extensao da SPEC-008 Camada 1.

## Acceptance Criteria
- [x] CT-1: SKILL.md exists with valid frontmatter (name, category, version, spec, dependencies, author, orcid)
- [x] CT-2: category declared as "system" with tags [validation, domain-shift, jaccard, bootstrap, multi-institutional]
- [x] CT-3: version field present ("1.0") with TDD suite reference (article/evaluations/domain_shift_audit.py)
- [x] CT-4: scripts/domain_shift_audit.py imports cleanly and exposes key functions (jaccard, decompor_variancia, bootstrap_limiar_jaccard, aplicar_regra_decisao, gerar_relatorio_completo) + dataclasses (Documento, PadraoInstituicao)
