---
spec_id: SPEC-935-R677
title: Abstencao explicita para consulta bibliografica vazia
status: green
component: rag/book_library.py + integrations/ecosystem_mcp.py
test_file: tests/test_r677_empty_library_request.py
---

# SPEC-935-R677 — Solicitação vazia e ausência de suporte

## Problema observado

O texto fornecido pelo usuário contém task, topic e query vazios, inventário
ready e nenhuma evidência. No código atual, o prompt MCP já recusa task/topic
vazios antes da recuperação. A saída anexada não demonstra uma falha do MCP
atual nem permite identificar qual processo ou versão a produziu.

A consulta Python direta, usada por MarceloClaroOrchestrator.library_query,
aceita query vazia e consulta o inventário antes de retornar status=ready.
Esse estado descreve o índice e pode ser confundido com uma solicitação válida.
Esta correção deriva da inspeção do código e do caso fornecido; não é atribuída
a nenhum livro. Não há evidência bibliográfica recuperada no anexo.

## Contratos

1. Query vazia ou composta apenas por espaços Unicode retorna
   status=invalid_request, reason_code=empty_query, abstained=true,
   evidence_count=0 e evidence=[]. Não acessa o índice, inventário ou PDFs.
2. O resultado vazio explicita retrieval_executed=false,
   model_inference_executed=false e training_executed=false. Não inclui
   index_status inferido ou inventado; library_status continua disponível.
3. Consultas com texto válido e sem suporte mantêm a abstenção lexical e o
   estado real do índice. Limites e tipos inválidos continuam a gerar ValueError;
   o limite de termos é validado antes de acessar fontes.
4. MCP prompt/search e CLI continuam a recusar entradas vazias antes de
   construir o orquestrador. A prova inclui um servidor MCP novo, sem inferência.
5. Nenhuma evidência, citação ou melhora cognitiva é fabricada. MCP continua
   sendo interface de ferramentas/contexto; colaboração A2A permanece sob
   MarceloClaroOrchestrator. Não adicionar executor, tool ou agente para a guarda.

## Aceitação executável

- R677-EMPTY: Python e orquestrador se abstêm sem acesso a fontes/índice.
- R677-BOUNDARIES: prompt MCP, busca MCP e CLI rejeitam vazio antes do handler.
- R677-COMPATIBILITY: consulta válida sem suporte e prompt válido permanecem
  funcionais, com regressão R657/R658 e configuração OpenCode reproduzível.
- R677-PROTOCOL: rejeição de prompt vazio pelo protocolo MCP em processo novo;
  relatório separado da evidência sintética, sem execução de modelos ou treino.

Registrar RED/GREEN, hashes dos artefatos e ciclo de evolução sem score ou
validação científica externa. Esta guarda não recupera a tarefa perdida pelo
cliente e não estabelece a origem da saída histórica anexada.
