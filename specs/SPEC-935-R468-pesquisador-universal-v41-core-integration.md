# SPEC-935-R468 — Pesquisador Universal v4.1 incorporado ao Core

## Objetivo
Registrar a supercamada científica v4.1 como extensão nativa do OpenCode
Ecosystem Core, preservando o Core como kernel de orquestração.

## Invariantes
1. `marceloclaro` permanece orquestrador primário.
2. MetaBus, Blackboard, AttentionRouter e SDD/TDD não são substituídos.
3. A skill OpenCode é registrada em `.opencode/skills/pesquisador-universal-marcelo-claro/`.
4. A bridge nativa é `python -m marceloclaro.scientific_lab`.
5. O commit `a5478054...` é baseline auditada, não HEAD obrigatório pós-merge.
6. Ausência da instalação científica resulta em `not_installed`/exit 4.
7. Nenhum gate humano científico pode ser contornado pela bridge.
8. `scihub-cli` permanece ausente.
9. Supply-chain evidence não constitui evidência científica.

## Critérios de aceitação
- CA1: `scientific_lab.runtime` importa sem dependência científica pesada.
- CA2: discovery respeita `PESQUISADOR_UNIVERSAL_HOME` antes do caminho padrão.
- CA3: path sem `SKILL.md`, `VERSION.json` ou validator é recusado.
- CA4: `status` diferencia `installed`, `invalid` e `not_installed`.
- CA5: `core-check` exige os oito componentes estruturais observados no baseline.
- CA6: a skill OpenCode está registrada.
- CA7: dispatch não usa `shell=True` e só aceita controllers allowlisted.
- CA8: CI testa a bridge em Python 3.10–3.14; configuração não equivale a execução comprovada.
