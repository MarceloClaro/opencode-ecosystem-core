# R126 — Agente-executor MIRA de runtime (delegável pelo Blackboard)

## Objetivo

Fechar o acoplamento formal entre o pipeline MIRA de apresentações (R123)
e o runtime multiagente: um agente-executor registrado no Blackboard,
com capacidade própria, que realiza o método MIRA quando uma tarefa de
apresentação é **delegada** — fechando o laço completo
`delegate → match (CFP + atenção) → execute → report_completion`, com o
Trust Engine e a Token Economy aprendendo com o resultado.

## Motivação

Pedido do usuário: "prossiga" — dando sequência à evolução natural
explicitada no evo-34 (R125): o acoplamento formal entre um
agente-executor do runtime e o pipeline ficara como ciclo futuro.

Após o R125, o pipeline era alcançável pelo CLI (`present()`), mas rodava
**fora** do laço de delegação: não postava tarefa, não passava pelo
matching por atenção, não acionava Trust/Economy. Os agent cards MIRA do
catálogo eram cartões de markdown, sem executor real. Faltava um agente
de runtime que **encarnasse** o pipeline e fosse **delegável**.

## Mudanças Entregues

1. **`illustrations/mira_agent.py` (novo)**: `MiraPresentationAgent`
   - identidade fixa `agent_id="mira-presenter"`, com
     `capabilities=["apresentacao", "apresentacao-mira", "mira-deck",
     "slides-animados"]`. A capacidade `apresentacao-mira` é
     **distintiva** (exclusiva do agente), garantindo elegibilidade
     determinística no matching do Blackboard.
   - `register_payload()` → dict pronto para `agent.register`.
   - `execute(context)` → lê `production_folder`, valida `manuscrito.md`,
     roda `MiraDeckPipeline.run()` e retorna resultado padronizado
     (`ok`/`passed`/`deck`/`conformidade`/`violations`); contexto
     inválido/manuscrito ausente → `{"ok": False, "error": ...}` sem
     exceção.
2. **`illustrations/__init__.py`**: exporta `MiraPresentationAgent`,
   `MIRA_AGENT_ID`, `MIRA_CAPABILITIES`.
3. **`marceloclaro/orchestrator.py`**:
   - Registro do agente na inicialização (quando `auto_load_agents`) —
     aparece em `list_agents()`/`status()`.
   - `register_mira_agent()` idempotente (não duplica o cartão).
   - `present_task(production_folder)`: delega a apresentação como tarefa
     do Blackboard (`required_capabilities=["apresentacao-mira"]`),
     executa pelo agente e reporta a conclusão via `report_completion`.
     Retorna o rastro `task_id` + `agent_id` + resultado.
4. **`tests/test_r126_mira_agent_runtime.py` (novo)**: 9 testes TDD.

## Verificação

- TDD: testes escritos antes → vermelho (9 failed) → verde (9 passed).
- Prova E2E real: `present_task` numa produção sintética → tarefa
  `completed` e `assigned_to == "mira-presenter"`, deck gerado, e o
  Trust Engine aprendeu (o `confidence_ledger` passou a ter entrada para
  `mira-presenter`). O laço multiagente completo fecha de fato.
- Subconjunto sensível a contagem de agentes (orchestrator/agent/catalog/
  status/blackboard): 195 passed, sem regressão pela adição do agente.
- `python3 -m pytest tests/ -q` completo.

## Lições

1. `metabus.publish` é **síncrono** (dispara os handlers em linha), então
   ao retornar de `delegate()` a tarefa já percorreu CFP → volunteer →
   assigned. Isso permitiu que `present_task` execute e reporte na mesma
   chamada, sem esperar callbacks — mas depende dessa sincronia; se o
   MetaBus virasse assíncrono, o executor precisaria aguardar o
   `task.assigned` antes de reportar.
2. Uma capacidade **distintiva** (`apresentacao-mira`, exclusiva do
   agente) é o que torna a atribuição determinística: sem ela, o
   matching por atenção entre agentes com capacidades genéricas poderia
   escolher outro agente, e o `report_completion` do executor não casaria
   com `task.assigned_to`. Capacidades exclusivas são a forma barata de
   acoplar um executor específico a um tipo de tarefa.
3. Coexistência intencional de duas vias: `present()` (direta, chamada de
   biblioteca — usada pelo CLI do R125) e `present_task()` (delegada, sob
   governo do runtime). A via delegada não substitui a direta; ela a
   promove a cidadã de primeira classe do Blackboard quando o governo
   (confiança/economia/reflexão) importa.

## Score

**8.6/10**

- Fecha o elo que faltava (motor → agente delegável), verificado por
  prova E2E do laço completo, não só por mocks.
- TDD real, capacidade distintiva para atribuição determinística,
  idempotência do registro, sem regressão na contagem de agentes.
- Não expõe `present_task` no CLI (a via direta do R125 permanece o
  caminho do usuário) nem trata concorrência de múltiplas tarefas —
  deixados explícitos como escopo futuro.
