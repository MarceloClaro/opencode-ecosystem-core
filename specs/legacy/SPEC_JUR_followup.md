# SPEC-JUR-003: Follow-up Advocacia
Versao: 1.0.0 | Status: verified | Dominio: juridico

## Objetivo
Skill de produtividade e gestao de demandas para advogados. Opera em 3 camadas (diaria, semanal, mensal) com sistema de alertas por urgencia e integracao com MCPs (time, sqlite, websearch, fetch).

## Criterios de Aceitacao
- [x] CT-1: SKILL.md exists with frontmatter
- [x] CT-2: category: juridico declared
- [x] CT-3: version field present
- [x] CT-4: Camadas diaria/semanal/mensal documentadas

## Tipo
Prompt-only skill (sem scripts Python)

## Sistema de Alertas
| Nivel | Trigger | Acao |
|-------|---------|------|
| URGENTE | Prazo < 48h | Contato imediato |
| ALTO | Prazo < 5 dias | Alerta hoje |
| MEDIO | Prazo < 15 dias | Agendar revisao |
| BAIXO | Prazo > 15 dias | Revisao semanal |
