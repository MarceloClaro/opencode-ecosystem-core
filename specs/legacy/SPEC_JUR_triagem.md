# SPEC-JUR-007: Triagem Juridica
Versao: 1.0.0 | Status: verified | Dominio: juridico

## Objetivo
Skill de classificacao e encaminhamento de demandas juridicas. Triagem sistematica: area do direito, urgencia, dados essenciais e fluxo de encaminhamento. Nunca diagnosticar resultado.

## Criterios de Aceitacao
- [x] CT-1: SKILL.md exists with frontmatter
- [x] CT-2: category: juridico declared
- [x] CT-3: version field present
- [x] CT-4: Regras de compliance OAB documentadas

## Tipo
Prompt-only skill (sem scripts Python)

## Regras de Compliance OAB
- Nao fazer promessa de resultado
- Nao dar opiniao juridica sem contrato firmado
- Nao cobrar consulta inicial sem combinado
- Sempre informar: "triagem inicial, nao constitui consulta juridica"
