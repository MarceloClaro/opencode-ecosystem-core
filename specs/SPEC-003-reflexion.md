---
spec_id: SPEC-003
component: mci.reflexion
title: Reflexion Middleware (Auto-Reflexão Pós-Execução)
version: 1.0.0
status: approved
test_file: tests/test_ecosystem.py
---

# SPEC-003 — Reflexion Middleware

## Objetivo
Garantir que toda conclusão de tarefa gere uma auto-reflexão verbal (padrão Reflexion, Shinn et al. 2023) que atualize a memória metacognitiva global e o confidence ledger.

## Requisitos Funcionais

| ID | Requisito | Critério de Aceitação | Teste |
|---|---|---|---|
| RF-003.1 | Interceptar conclusões | Assina `metacognition.reflect_request` e processa todo evento | `test_blackboard_full_cycle` |
| RF-003.2 | Gerar reflexão | Produz texto de reflexão contendo contexto e diagnóstico de sucesso/falha | `test_blackboard_full_cycle` |
| RF-003.3 | Atualizar confiança | Sucesso eleva a confiança; falha reduz (via `add_reflection`) | `test_failed_task_lowers_confidence` |
| RF-003.4 | Publicar resultado | Emite `metacognition.reflected` com `agent_id` e `new_confidence` | `test_blackboard_full_cycle` |

## Invariantes (Contratos)

1. **INV-003.1**: NENHUMA conclusão de tarefa pode escapar da reflexão (cobertura total).
2. **INV-003.2**: Score de sucesso = 1.0; score de falha = 0.0 (mapeamento determinístico).
3. **INV-003.3**: A reflexão DEVE ser persistida na memória episódica antes da publicação do evento `metacognition.reflected`.

## Não-Objetivos
- Reflexões geradas por LLM (a interface aceita injeção futura; o núcleo usa template determinístico).
