---
spec_id: SPEC-935-R1254
title: Preflight SDD e esquema explícito no gateway MCP de delegação
component: integrations.ecosystem_mcp + marceloclaro.workflow + marceloclaro.autonomous
status: red
test_file: tests/test_r1254_delegation_gateway.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1254-PREFLIGHT:
      - tests/test_r1254_delegation_gateway.py::test_missing_or_unknown_spec_blocks_before_checkpoint_and_dispatch
      - tests/test_r1254_delegation_gateway.py::test_invalid_node_blocks_entire_workflow_before_any_dispatch
      - tests/test_r1254_delegation_gateway.py::test_valid_spec_is_preflighted_and_forwarded_to_node
      - tests/test_r1254_delegation_gateway.py::test_resume_preflight_failure_preserves_checkpoint
    R1254-SCHEMA:
      - tests/test_r1254_delegation_gateway.py::test_mcp_workflow_schema_documents_spec_id_and_node_budget
      - tests/test_r1254_delegation_gateway.py::test_mcp_run_schema_exposes_spec_id
    R1254-COMPATIBILITY:
      - tests/test_r1254_delegation_gateway.py::test_non_strict_mode_keeps_legacy_workflow_without_spec_id
      - tests/test_r1254_delegation_gateway.py::test_spec_preflight_delegates_known_and_unknown_ids
---

# SPEC-935-R1254 — Preflight SDD e esquema explícito no gateway MCP de delegação

## Objetivo

Fechar a fronteira entre `ecosystem_workflow`/`ecosystem_run`, o
`WorkflowCoordinator` e o `AutonomousCoordinator`: tornar `spec_id` visível no
contrato MCP, validá-lo antes de persistir checkpoint ou reservar execução, e
preservar sua passagem até cada nó sem iniciar agente quando o preflight falhar.

## Decisões normativas

- Cada nó de `ecosystem_workflow` pode declarar `spec_id` e
  `per_node_max_steps`; ambos devem aparecer no schema MCP e na descrição da
  ferramenta. Em modo SDD estrito, `spec_id` é obrigatório. O modo legado não
  estrito continua aceitando nó sem `spec_id`.
- O `AutonomousCoordinator` expõe um preflight reutilizável que retorna o
  resultado de `MarceloClaroOrchestrator.sdd_preflight(spec_id)`; ausência de
  `spec_id` em modo estrito retorna `spec_id_required`, e IDs inválidos
  preservam `spec_not_found` ou a razão precisa do gate SDD.
- Antes de criar checkpoint de workflow, reservar passos, postar CFP, criar
  tarefa no Blackboard ou chamar executor, todos os nós da nova definição são
  preflightados. Uma falha em qualquer nó bloqueia o workflow inteiro.
- Falha de preflight retorna objeto estruturado com `status=blocked`,
  `success=false`, `error=sdd_preflight_failed`, a lista de nós/reasons,
  `steps=0` e `checkpoint_created=false`. Não cria registro, task ou chamada de
  executor. O `spec_id` válido é encaminhado inalterado ao nó.
- Workflows retomados preservam seu checkpoint existente; preflight inválido
  não pode reescrevê-lo nem repetir uma execução. `ecosystem_run` mantém seu
  parâmetro `spec_id` e seu gate atual; a mudança não contorna a exigência de
  RED para specs de software.
- O contrato é validado offline com coordenadores e stores simulados. Nenhum
  executor, provedor LLM, agente externo ou aplicação de usuário é chamado por
  estes testes.

## Critérios de aceitação executáveis

- `R1254-PREFLIGHT` — ausência/invalidade de `spec_id` em SDD estrito produz
  bloqueio estruturado antes de checkpoint ou despacho; qualquer nó inválido
  impede despacho parcial; um ID válido é preflightado e chega intacto ao nó.
- `R1254-SCHEMA` — o schema e a descrição MCP expõem `spec_id` e
  `per_node_max_steps` no workflow, e `spec_id` no run, incluindo a exigência
  de especificação em modo estrito.
- `R1254-COMPATIBILITY` — modo não estrito sem ID continua funcional; o
  preflight do coordenador delega IDs ao gate SDD sem executar tarefa.

## Limites

Os testes não comprovam disponibilidade de executores, inferência, revisão A2A
externa ou qualidade do conteúdo produzido. Um resultado `ready` comprova apenas
que o gate SDD local autorizou a etapa; não equivale a execução nem validação.
