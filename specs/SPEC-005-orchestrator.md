---
spec_id: SPEC-005
component: marceloclaro.orchestrator
title: Orquestrador MarceloClaro (Percepção, Delegação, Reflexão)
version: 2.0.0
status: approved
test_file: tests/test_ecosystem.py
---

# SPEC-005 — Orquestrador MarceloClaro

## Objetivo
Coordenar o ecossistema completo: carregar agentes, perceber lições da memória global, delegar via atenção multi-cabeça, executar pipelines gerar→verificar→revisar e auditar o estado global.

## Requisitos Funcionais

| ID | Requisito | Critério de Aceitação | Teste |
|---|---|---|---|
| RF-005.1 | Carregar agentes de `agents/*.md` | 5 agentes essenciais registrados com capacidades corretas | `test_agent_loader_reads_frontmatter` |
| RF-005.2 | Perceber antes de delegar | `delegate` injeta `metacognitive_briefing` no contexto da tarefa | `test_delegation_includes_briefing` |
| RF-005.3 | Rotear via atenção | `_on_cfp` usa `AttentionRouter.route` e publica volunteer no top-1 | `test_blackboard_full_cycle` |
| RF-005.4 | Executar pipeline | `run_pipeline` registra reflexão do orquestrador na memória global | `test_orchestrator_full_transformer_cycle` |
| RF-005.5 | Auditar roteamento | `explain_routing` expõe scores das 4 cabeças por agente | `test_orchestrator_full_transformer_cycle` |
| RF-005.6 | Recuperar memórias | `recall` retorna entradas relevantes via HTM | `test_orchestrator_full_transformer_cycle` |

## Invariantes (Contratos)

1. **INV-005.1**: Toda delegação DEVE consultar a memória metacognitiva antes (percepção obrigatória).
2. **INV-005.2**: O orquestrador NUNCA executa tarefas de domínio diretamente; apenas delega e coordena.
3. **INV-005.3**: `status()` DEVE expor agentes, tarefas, confidence ledger e tamanho da memória (auditabilidade total).

## Não-Objetivos
- Execução paralela/assíncrona de tarefas (versão atual é síncrona).
