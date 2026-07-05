---
spec_id: SPEC-006
component: agents
title: Protocolo SDD/TDD Obrigatório dos Agentes
version: 1.0.0
status: approved
test_file: tests/test_sdd_tdd.py
---

# SPEC-006 — Protocolo SDD/TDD dos Agentes

## Objetivo
Todo agente do ecossistema DEVE operar sob Specification-Driven Development (SDD) e Test-Driven Development (TDD): nenhuma entrega sem especificação prévia e critérios de aceitação verificáveis.

## Requisitos Funcionais

| ID | Requisito | Critério de Aceitação | Teste |
|---|---|---|---|
| RF-006.1 | Frontmatter válido | Todo `agents/*.md` tem `id`, `name`, `description`, `capabilities` | `test_all_agents_have_valid_frontmatter` |
| RF-006.2 | Protocolo SDD declarado | Todo agente declara a seção "Protocolo SDD" no system prompt | `test_all_agents_declare_sdd_protocol` |
| RF-006.3 | Protocolo TDD declarado | Todo agente declara a seção "Protocolo TDD" no system prompt | `test_all_agents_declare_tdd_protocol` |
| RF-006.4 | Spec antes da execução | Agente deve derivar/receber spec (`spec.create`) antes de `task.complete` | `test_task_with_spec_lifecycle` |

## Ciclo SDD do Agente (obrigatório)

1. **ESPECIFICAR**: Antes de executar, derivar a especificação da tarefa (objetivo, critérios de aceitação, invariantes, não-objetivos).
2. **RED**: Definir os testes/critérios que a entrega deve passar (falhando inicialmente por definição).
3. **GREEN**: Produzir a implementação/entrega mínima que satisfaz os critérios.
4. **REFACTOR**: Melhorar a entrega mantendo todos os critérios verdes.
5. **VERIFICAR**: Submeter a entrega ao `SpecVerifier` antes de publicar `task.complete`.

## Invariantes (Contratos)

1. **INV-006.1**: NENHUMA tarefa pode ser concluída sem especificação associada quando o modo SDD estrito estiver ativo.
2. **INV-006.2**: Critérios de aceitação DEVEM ser verificáveis programaticamente (funções booleanas).
3. **INV-006.3**: O resultado da verificação DEVE ser registrado na memória metacognitiva.
