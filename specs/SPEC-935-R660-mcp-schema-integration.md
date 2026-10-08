---
spec_id: SPEC-935-R660
title: Validacao JSON Schema comum antes de efeitos MCP
status: green
validation_scope: local_runtime
release_gate: docs/evidence/R659_R662_RELEASE_GATE.json
component: integrations/mcp_validation.py + mci/mcp_server.py + synthetic_university/mcp_security.py
test_file: tests/test_r660_mcp_validation.py
---

# R660 — MCPs validam o mesmo contrato antes de executar

## Contratos

1. Helper local usa jsonschema pinado, valida schema e instância, cobrindo
   required, null, items, bounds, enum, objetos aninhados e additionalProperties.
2. Rejeitar valores numéricos não finitos, schemas inválidos e referências
   remotas sem rede. Diagnósticos identificam campos/regras sem ecoar valores.
3. MCI, SyntheticUniversity com/sem guard e scanner assíncrono/síncrono aplicam
   schema antes do handler. Chamadas rejeitadas não publicam tarefas/agentes.
4. Contratos expostos por tools/list coincidem com validação. Preservar formatos
   de erros compatíveis; tratar falhas como isError, sem sucesso falso.
5. MCI limita leitura de memória e mantém tipos/capacidades válidos. TDD e prova
   stdio real cobrem negativos sem efeitos e chamada válida conectada ao Blackboard.

## Critérios de aceitação executáveis

- `R660-SCHEMA` — Validação completa aceita entradas válidas e recusa incompatíveis.
- `R660-EFFECTS` — Chamadas inválidas não invocam handlers nos servidores.
- `R660-OFFLINE` — Schema inválido/remoto e número não finito falham sem rede.
