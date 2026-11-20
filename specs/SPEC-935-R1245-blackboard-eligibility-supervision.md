---
spec_id: SPEC-935-R1245
title: Elegibilidade, ciclo de vida e supervisão no Blackboard
component: mci.blackboard
status: planned
test_file: tests/test_r1245_blackboard_policy.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1245-ELIGIBILITY:
      - tests/test_r1245_blackboard_policy.py::test_volunteer_must_belong_to_current_cfp_and_still_be_eligible
      - tests/test_r1245_blackboard_policy.py::test_live_load_counts_only_assigned_tasks
    R1245-LIFECYCLE:
      - tests/test_r1245_blackboard_policy.py::test_completion_accepts_only_assignee_and_terminal_status_once
      - tests/test_r1245_blackboard_policy.py::test_agent_is_released_only_when_no_other_task_is_assigned
    R1245-SUPERVISION:
      - tests/test_r1245_blackboard_policy.py::test_trust_below_point_three_requires_supervision_without_auto_volunteer
      - tests/test_r1245_blackboard_policy.py::test_trust_at_point_three_is_eligible_and_confidence_remains_distinct
---

# SPEC-935-R1245 — Elegibilidade, ciclo de vida e supervisão no Blackboard

## Objetivo

Tornar a atribuição do Blackboard resistente a voluntariado fora do CFP ou
desatualizado, definir estados terminais e liberação de agentes de forma
consistente, e explicitar como o Trust Engine e o ledger de confiança participam
da decisão sem confundir suas medidas.

## Política normativa

- Capacidades exigidas continuam sendo `all_of`; o voluntário deve constar no
  CFP corrente, estar registrado e disponível, e ainda satisfazer as capacidades
  no instante da atribuição.
- Estados permitidos: `open`, `assigned`, `completed`, `failed`, `blocked` e
  `awaiting_supervision`. Só `open` pode receber voluntário. Só a pessoa
  atribuída pode concluir/falhar uma tarefa atribuída; resultados aceitos são
  `completed` e `failed`. Estados terminais não reabrem por eventos duplicados.
- A carga operacional conta exclusivamente tarefas `assigned`; tarefas
  concluídas/falhas não consomem capacidade atual. O agente permanece `busy`
  enquanto tiver alguma tarefa atribuída e é liberado depois da última.
- O gate do Trust Engine é obrigatório: exceção ou `allowed=False` exclui o
  agente. Score do Trust Engine abaixo de `0.30` nunca recebe atribuição
  automática; o Blackboard registra `awaiting_supervision` e publica um pedido
  explícito de supervisão com identidade, score e proveniência. `0.30` é
  inclusivo para roteamento automático, desde que o gate permita.
- O score de `confidence_ledger` é sinal distinto: normalizado e usado para
  ranking/atenção; não substitui o `trust_score` do gate nem remove o requisito
  de supervisão. Score de trust ausente em implementação legada recebe o valor
  neutro `0.5`, explicitamente identificado como fallback; valor fornecido
  inválido é fail-closed.
- Esta mudança não implementa autenticação de supervisores nem uma interface de
  aprovação. `awaiting_supervision` é um estado de retenção, não uma aprovação.

## Critérios de aceitação executáveis

- `R1245-ELIGIBILITY` — voluntário que não consta no CFP atual, deixou de estar
  disponível ou não cumpre todas as capacidades não altera a tarefa nem reserva
  o agente; carga ativa ignora tarefas terminais.
- `R1245-LIFECYCLE` — conclusão só é aceita uma vez pelo agente atribuído e com
  estado terminal permitido; um agente só retorna a `available` quando nenhuma
  outra tarefa dele permanece `assigned`.
- `R1245-SUPERVISION` — score de trust estritamente menor que `0.30` resulta em
  `awaiting_supervision` e evento de supervisão, sem `task.volunteer`; score
  igual a `0.30` pode ser roteado quando autorizado. Ledger de confiança e score
  de trust são reportados como sinais separados.

## Limites e verificação

Testes offline validam apenas os contratos locais da implementação. Não provam
autenticação de supervisor, concorrência entre processos no Blackboard,
calibração estatística dos scores ou qualidade de inferência dos agentes.
