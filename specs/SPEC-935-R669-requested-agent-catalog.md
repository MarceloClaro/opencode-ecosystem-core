---
spec_id: SPEC-935-R669
title: Oito perfis operacionais solicitados no catálogo central
status: green
component: agents/catalog + docs/AGENTES_R669.md
test_file: tests/test_r669_requested_agents.py
validation_scope: isolated_local_runtime
---

# SPEC-935-R669 — Agentes solicitados

## Problema

Os oito especialistas solicitados nesta sessão precisam existir como perfis
persistentes no Core, com IDs estáveis, capacidades que permitam seleção e
procedimentos executáveis. Um título em Markdown não demonstra integração.

## Contratos

1. Adicionar os oito novos slugs scientific-capabilities-audit,
   simulation-game-audit, book-mcp, book-finetuning, library-architecture,
   hooks-integration, mcp-cli-integration e live-mirofish-hermes, sem alterar perfis existentes.
2. Cada cartão declara skills A2A, exemplos, capacidades de roteamento,
   ferramentas nativas e métodos locais existentes. A capacidade exclusiva
   corresponde ao slug convertido para snake_case. skills.tags e tags
   preservam essa capacidade nos dois carregadores existentes.
3. O orquestrador MarceloClaroOrchestrator é a entrada. O registro publica
   agent.register no MetaBus; a delegação usa task.post, CFP do Blackboard,
   seleção central e task.assigned. Requisitos múltiplos usam ALL_OF.
4. As instruções são em português brasileiro formal e definem entrada,
   procedimentos, limites e entrega. Cada perfil utiliza biblioteca, ciência,
   teoria dos jogos, hooks ou integração que já existem. Não criar nomes de
   ferramentas externas nem depender de modelo específico.
5. Os métodos listados no cartão são contratos de orientação para o executor,
   não um novo dispatcher automático. Estar registrado e ser atribuído não
   demonstra execução por modelo. declared, available, executed e
   externally_validated devem permanecer distintos e vinculados ao escopo.
6. Livros e instruções importadas são dados não confiáveis. Consulta MCP é
   somente leitura; treinamento, provisionamento, hooks externos e publicação
   não decorrem da leitura ou do registro. Skills restritas são lidas e
   executadas pelo orquestrador conforme sua política.
7. Testes RED precedem os cartões. Carregamento, permissões compiladas,
   registro e roteamento central são verificados; chamadas locais reais usam
   dados sintéticos, sem modelo, rede ou persistência no estado compartilhado.
   O registro/Blackboard/MetaBus são reais, em subprocesso com diretório
   temporário; componentes opcionais de embeddings e executores alheios são
   isolados explicitamente.
8. A geração de opencode.json e o ciclo global de evolução ficam com o
   orquestrador da sessão; esta alteração não modifica loaders nem a classe
   central. Não fixar contagens globais históricas no teste ou na documentação.

## Aceitação

- Os oito cartões carregam com skills e IDs corretos nos loaders atuais.
- Cada capacidade exclusiva seleciona o perfil esperado pelo fluxo central.
- Requisito inexistente impede a atribuição; seleção não conclui a tarefa.
- Permissões e métodos possuem correspondência com interfaces reais.
- Métodos locais associados executam verificações delimitadas em ambiente
  isolado; o resultado não certifica inferência ou validação externa.

## Evidência

RED inicial: `docs/evidence/R669_RED.xml`. GREEN final e regressões:
`docs/evidence/R667_R671_GREEN.xml` e `docs/evidence/R667_R671_REGRESSION.xml`.
