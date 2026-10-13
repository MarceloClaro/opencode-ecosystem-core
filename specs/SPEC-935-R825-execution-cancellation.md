---
spec_id: SPEC-935-R825
title: Interrupção conservadora e limpeza de processos da rede coordenada
status: green
component: integrations/harness_runtime.py + integrations/ecosystem_mcp.py + marceloclaro/autonomous.py + marceloclaro/workflow.py
test_file: tests/test_r825_execution_cancellation.py
---

# SPEC-935-R825 — Interromper a execução e conservar evidência

## Problema reproduzido

O prazo de `HarnessRuntime.execute` encerrava somente a CLI principal: um
descendente local permanecia em execução. O cancelamento de uma requisição MCP
abandonava a espera de `asyncio.to_thread`, mas o workflow continuava a executar
nós posteriores e persistia conclusão bem-sucedida. As reproduções são locais;
nenhuma chamada de modelo ou serviço externo foi necessária.

## Contratos

1. Preservar argv explícito, stdin, flags de leitura, parser e sanitização dos
   erros. Não introduzir shell, aprovação automática nem executor novo.
2. No POSIX, a CLI pertence a um grupo exclusivo da chamada. Prazo, cancelamento
   e encerramento normal devem encerrar também os descendentes desse grupo;
   a limpeza deve ter prazo próprio limitado e não bloquear em pipes herdados.
3. O cancelamento MCP da rede (`ecosystem_run`/`ecosystem_workflow`) deve
   sinalizar a execução em segundo plano. A propagação
   deve atravessar o coordenador existente até a CLI, impedir fallback/revisões
   e impedir que outro nó seja iniciado após a interrupção.
4. Uma execução interrompida não recebe sucesso. Uma etapa ativa conserva sua
   reserva e a incerteza sobre o resultado; a retomada não a repete sem
   `retry_failed=True`. Nós ainda não iniciados podem ser retomados com orçamento
   disponível. Etapas já concluídas antes da interrupção permanecem reutilizáveis.
5. A interrupção libera as exclusões de execução somente depois da limpeza.
   Não apagar entregas anteriores nem transformar cancelamento em inferência
   ou validação externa. Não criar infraestrutura paralela de workflow.
6. No Windows, preservar argv sem shell e aplicar limpeza da árvore pelos
   recursos disponíveis da plataforma. A prova POSIX não certifica o Windows
   nem processos que deliberadamente escapem do grupo/session da chamada.
7. `run_cancellable` resiste tanto a `Task.cancel()` repetido quanto ao
   cancelamento reiterado de `AnyIO.CancelScope`, aguarda a limpeza e conserva
   o cancelamento externo. A fila de `_knowledge_operation` verifica o sinal
   antes e depois da aquisição do lock; uma requisição cancelada não aguarda a
   outra operação nem executa seu método. Os gates imediatos de run/workflow
   mantêm seu contrato de retornar bloqueio quando a rede está ocupada.

## Aceitação

- RED local reproduz prazo com descendente vivo, saída normal com descendente
  vivo e execução de nó seguinte após cancelamento MCP.
- GREEN executa processos Python inertes reais e confirma que a CLI e seus
  descendentes da chamada não continuam em execução após o retorno.
- Cancelamento durante a execução, antes de iniciar e entre etapas impede
  novas chamadas, conserva checkpoint e permite retomada conservadora.
- Regressões R640/R644 passam sem enfraquecer seus contratos de argv, parsing,
  disponibilidade e saúde. Limitações de plataforma permanecem explícitas.

## Evidências

As evidências e os recibos de execução ficam em `outputs/core-r825/`.
O cancelamento anterior foi registrado em
`outputs/core-r820/orchestration-cancel-red.json`.

## Limites do aceite

O prazo limita a operação; a limpeza pode acrescentar seu próprio intervalo
limitado. No Windows, `taskkill /T /F` aplica-se à árvore de uma CLI ainda viva;
uma falha desse comando tem fallback para encerrar o processo principal. O
teste desse fallback usa comando Windows simulado e processo local real, e
não certifica uma árvore Windows nativa nem descendentes após a saída do pai.
O caminho Windows/WSL também não recebeu esse certificado.

As rotas REA e navegador adotam o mesmo helper nas R823/R824. Outras funções
síncronas que não consultem o sinal continuam sujeitas a seus prazos próprios;
esta correção não promete cancelamento instantâneo de terceiros não
cooperativos nem transforma sua execução local em validação externa.
