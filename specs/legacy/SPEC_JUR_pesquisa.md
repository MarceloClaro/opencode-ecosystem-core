# SPEC-JUR-006: Pesquisa Jurisprudencial
Versao: 1.0.0 | Status: verified | Dominio: juridico

## Objetivo
Skill de pesquisa jurisprudencial em multiplas bases (STF, STJ, TJs, TRTs) com protocolo de citacao responsavel. Nunca inventar precedentes; sempre verificar existencia real.

## Criterios de Aceitacao
- [x] CT-1: SKILL.md exists with frontmatter
- [x] CT-2: category: juridico declared
- [x] CT-3: version field present
- [x] CT-4: Regras de integridade de citacao documentadas

## Tipo
Prompt-only skill (sem scripts Python)

## Regras de Integridade
- Nunca resumir ementa de forma que altere o sentido
- Nunca citar precedente sem verificar existencia real
- Sempre informar quando pesquisa nao encontrar resultado
- Sempre distinguir caso concreto do precedente
