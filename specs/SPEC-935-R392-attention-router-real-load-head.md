---
spec_id: SPEC-935-R392
title: Cabeça de carga (load) do AttentionRouter deixa de ser constante morta
component: mci/blackboard.py, transformer/attention.py
status: verified
test_file: tests/test_r212_attention_blackboard.py
---

# SPEC-935-R392 — Cabeça "load" do AttentionRouter passa a computar carga real

**Data:** 2026-08-03
**Motivação:** o usuário perguntou se o roteamento por atenção multi-cabeça
funciona de verdade ou é uma "cascata vazia". Investigação ao vivo (rodando
`AttentionRouter.explain()` com dados reais dos 210 agentes do Blackboard)
confirmou que 3 das 4 cabeças (`semantic`, `capability`, `confidence`) têm
sinal real e diferenciado, mas a quarta (`load`, 10% do peso) retornava
`1.0` para os 210 agentes, sempre, sem exceção — um componente morto dentro
de um sistema real.

## 1. Causa raiz

`mci/blackboard.py::AgentCard.to_dict()` nunca publicava a chave `"load"`.
`transformer/attention.py::AttentionRouter._head_load()` lê
`card.get("load", 0.0)` — com a chave sempre ausente, o default `0.0` era
usado para todo agente, produzindo `1.0 - 0.0 = 1.0` universalmente. Os 10%
de peso dessa cabeça no somatório de utilidade nunca diferenciavam a
decisão de roteamento entre nenhum par de agentes elegíveis.

## 2. Por que não é só "usar o status busy/available"

O `AttentionRouter._hard_gate_reasons()` já exclui agentes com
`status != "available"` **antes** da fase de pontuação — nenhum agente
literalmente "ocupado agora" chega a ser pontuado pelas 4 cabeças. Um
sinal binário busy/available não geraria diferenciação alguma entre os
candidatos que de fato competem pela tarefa (todos já "available" por
construção). O sinal de carga precisa refletir volume de trabalho
*recente/atribuído*, não o instante presente.

## 3. Correção

Nova função `mci/blackboard.py::_live_load(agent_id)`: conta tarefas do
Blackboard com `assigned_to == agent_id` e `status` em
`("assigned", "completed", "failed")`, normaliza por uma capacidade de
referência (`_LOAD_REFERENCE_CAPACITY = 5`), retorna `[0, 1]`.
`AgentCard.to_dict()` passa a incluir `"load": _live_load(self.agent_id)`.
`_head_load` (não alterado) já fazia `1.0 - load` corretamente — só
precisava receber um valor real em vez do default silencioso.

## 4. Verificação

- TDD: `tests/test_r212_attention_blackboard.py::TestR212LoadHeadIsLive`
  (2 testes novos) — RED confirmado antes da correção
  (`load_scores["idle-agent"] == load_scores["busy-agent"] == 1.0`), GREEN
  depois.
- Verificação end-to-end com o orquestrador real (não só teste isolado):
  atribuídas 4 tarefas reais a `academic_writer` no Blackboard ao vivo —
  `to_dict()["load"]` passou a reportar `0.8` para ele contra `0.0` para
  os demais agentes amostrados.
- Suíte completa: 2674 aprovados (2672 + 2 novos), 0 falhas, 56 pulados —
  zero regressão.

## 5. Critérios de aceitação

1. `AgentCard.to_dict()` sempre inclui uma chave `"load"` numérica em
   `[0, 1]`, derivada de tarefas reais atribuídas no Blackboard, nunca de
   um placeholder constante.
2. A cabeça `load` do `AttentionRouter` diferencia entre um agente ocioso
   e um agente com backlog real, com todos os outros fatores iguais.
3. Nenhuma outra cabeça (`semantic`, `capability`, `confidence`) foi
   alterada — a correção é estritamente aditiva.
4. Verificado tanto em teste isolado (RED→GREEN) quanto em execução real
   do orquestrador com o Blackboard ao vivo.
5. Zero regressão na suíte completa.
