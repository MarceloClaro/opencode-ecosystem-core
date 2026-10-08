---
spec_id: SPEC-935-R644
title: Workflows com dependências, retomada e saúde dos executores
status: red
component: marceloclaro/workflow.py + marceloclaro/workflow_store.py + integrations/harness_health.py
test_file: tests/test_r644_workflow.py
---

# SPEC-935-R644 — Coordenação de tarefas dependentes e recuperação

## Melhoria solicitada

A R640 conecta roteamento e execução de uma tarefa. Esta evolução permite
coordenar análises com etapas dependentes e revisão por outro especialista,
retomar etapas concluídas e evitar chamadas automáticas repetidas a um serviço
que já recusou a execução. Corrige também o diagnóstico falso de CLIs ausentes
fora do shell de login.

## Contratos

1. Um workflow contém até oito etapas, com IDs únicos, tarefa, capacidades,
   executor opcional e dependências explícitas. Recusar ciclos, IDs duplicados,
   referências desconhecidas e descrições vazias antes de criar tarefas.
2. Cada etapa passa pelo AutonomousCoordinator e pelo orquestrador existente.
   As saídas das dependências chegam às etapas seguintes como contexto com IDs
   e origem identificados, permitindo análise seguida de revisão independente.
3. Passos e tempo têm orçamento global. As etapas executam sequencialmente
   porque Blackboard e MetaBus são compartilhados; declarar esta estratégia
   em vez de prometer paralelismo que o runtime não garante.
4. Persistir estado antes e depois de cada execução. Retomada exige a mesma
   definição e reutiliza etapas concluídas. Uma etapa interrompida não pode ser
   anunciada como concluída nem repetida silenciosamente.
5. O armazenamento é atômico, não aceita caminhos arbitrários e impede duas
   execuções concorrentes do mesmo workflow. Falha de persistência é explícita.
6. Saúde dos executores distingue instalação de execução. Persistir somente
   metadados sanitizados, sem prompts, respostas ou credenciais. Após recusa
   de saldo/autenticação/timeout, aplicar pausa de 120 segundos na seleção
   automática; escolha explícita continua disponível. Mudança de binário
   invalida evidência antiga.
7. Diagnóstico de CLIs usa executáveis reais no PATH, pastas do usuário e venv,
   sem instalar programas nem confundir instruções de configuração com binário.
8. Expor workflow e consulta de estado pelo mesmo MCP e CLI. Manter ferramentas
   R640 e contratos anteriores; registrar limites e evidência real separada dos
   mocks de testes. Escopo continua análise e geração de texto com leitura.
9. O carregador do catálogo preserva capacidades explicitamente declaradas em
   listas legadas `capabilities` e `tags`, com prioridade do formato A2A de
   skills quando presente. Registrar um especialista do catálogo não deve
   apagar uma capacidade que o próprio arquivo declara e tornar tarefas
   compatíveis inelegíveis.

## Aceitação

- RED/GREEN: validação de DAG, transferência de contexto, bloqueio por falha,
  orçamento global, retomada, interrupção e concorrência do armazenamento.
- RED/GREEN: saúde persistente, pausa automática, invalidação, isolamento dos
  testes e detecção verdadeira de executáveis.
- Regressões R640 e configuração/MCP; lint e diagnóstico sem falhas.
- Workflow real de análise e revisão com executores disponíveis, incluindo
  retomada sem novas chamadas dos nós já concluídos.
