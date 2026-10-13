# ADR-R824: Playwright MCP sob o orquestrador central

**Status:** Accepted for implementation; operacionalidade depende do aceite R824.
**Date:** 2026-10-12.
**Deciders:** Implementação no escopo de atualização autorizado pelo usuário.

## Contexto

O host executa o Core em WSL, com recursos locais limitados. O gateway central
precisa distinguir preparação de tarefa, instalação e execução real. Não há
uma extensão BrowserMCP conectada que possa ser considerada prova do Core.

## Decisão

Usar o [Playwright MCP oficial](https://github.com/microsoft/playwright-mcp)
como provider externo com versão fixada, sessão isolada e encerramento por
operação. Expor uma fachada de ações delimitadas pelo `marceloclaro`, em vez
de carregar todo o catálogo do browser em todos os agentes. Preservar o
framework atual e corrigir seus casos de cancelamento concretamente observados.

## Opções consideradas

| Opção | Adequação | Custo e limite |
|---|---|---|
| BrowserMCP | Útil para o Chrome do usuário e sessões existentes | Exige extensão e conexão; README relata dependências não publicadas para build isolado |
| Playwright MCP | Página e sessão reais sem extensão, adequado ao WSL | Requer instalação do browser e dependências; páginas geram dados não confiáveis |
| Prompts Antigravity existentes | Preservam a delegação ao harness | Preparação de prompt não demonstra execução de navegador |
| LangGraph / Agent Framework / Temporal | Referências úteis de persistência e cancelamento | Uma substituição completa duplicaria checkpoints e o agente primário já existentes |

## Consequências

O navegador isolado não herda logins do Chrome do usuário. Fluxos autenticados
devem ser implementados e testados separadamente. A allowlist upstream declara
que não cobre redirects; a primeira prova real confirmou duas requisições
indevidas mesmo com interception de rota. A fachada usa um proxy local
HTTP/CONNECT por sessão que valida destinos antes da conexão, também em cadeias
de redirects. Upload HTTP chunked e upgrade HTTP simples são recusados pelo
proxy; HTTPS segue por CONNECT. O controle não é apresentado como fronteira
universal de segurança. Artefatos podem conter conteúdo das páginas e precisam
ser tratados como dados da tarefa. O critério de aceite é execução observada,
com cancelamento e limpeza, e não quantidade de ferramentas anunciadas.
