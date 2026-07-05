---
spec_id: SPEC-002
component: mci.blackboard
title: Blackboard e Agent Cards (Protocolo A2A)
version: 1.0.0
status: approved
test_file: tests/test_ecosystem.py
---

# SPEC-002 — Blackboard e Agent Cards

## Objetivo
Coordenar tarefas entre agentes via quadro negro compartilhado, com registro dinâmico de capacidades (Agent Cards, padrão A2A) e ciclo CFP → voluntariado → atribuição → conclusão.

## Requisitos Funcionais

| ID | Requisito | Critério de Aceitação | Teste |
|---|---|---|---|
| RF-002.1 | Registrar Agent Card | Evento `agent.register` cria card com `agent_id`, `capabilities`, `confidence_score` | `test_agent_loader_reads_frontmatter` |
| RF-002.2 | Postar tarefa | Evento `task.post` cria `BlackboardTask` com status `open` | `test_blackboard_full_cycle` |
| RF-002.3 | Emitir CFP | Tarefa postada gera `task.cfp` com agentes elegíveis (match de capacidades) | `test_blackboard_full_cycle` |
| RF-002.4 | Atribuir tarefa | Evento `task.volunteer` muda status para `assigned` e agente para `busy` | `test_blackboard_full_cycle` |
| RF-002.5 | Concluir e refletir | Evento `task.complete` muda status, libera o agente e dispara `metacognition.reflect_request` | `test_blackboard_full_cycle` |

## Invariantes (Contratos)

1. **INV-002.1**: Uma tarefa `assigned` NUNCA pode ser reatribuída sem antes ser concluída ou falhar.
2. **INV-002.2**: Apenas agentes com status `available` entram no CFP.
3. **INV-002.3**: O agente que conclui DEVE ser o mesmo que recebeu a atribuição (`assigned_to == agent_id`).
4. **INV-002.4**: Toda conclusão DEVE disparar o pedido de reflexão metacognitiva.

## Não-Objetivos
- Filas de prioridade entre tarefas concorrentes.
- Timeout/reatribuição automática de tarefas abandonadas (futuro: SPEC-007).
