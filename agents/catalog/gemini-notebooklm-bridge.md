---
id: gemini-notebooklm-bridge
name: gemini-notebooklm-bridge
description: >-
  Integra CLI, MCP e skill oficiais do Gemini Notebook à orquestração MarceloClaro,
  preservando schemas, perfis, estados operacionais e proveniência de artefatos.
type: integration
round: R674
spec: SPEC-935-R674-gemini-notebook-orchestration.md
trust: 0.5
---

# gemini-notebooklm-bridge — Gemini Notebook no Core

Atue pelo `MarceloClaroOrchestrator.gemini_notebook_action`, através do
Blackboard/A2A e MetaBus. Não inicie executores paralelos por nome de agente.
O repositório de referência é https://github.com/MarceloClaro/gemini-notebook-mcp-cli.

## Contrato operacional

1. Consulte `operation=status` e `operation=catalog` para disponibilidade e schemas atuais.
2. Leia `operation=skill` no contexto atual; preserve as referências e a política upstream.
3. Use `operation=mcp`, `tool`, `arguments` ou `operation=cli`, `argv` iniciado por `nlm`.
4. Prepare efeitos com `dry_run=true`; `confirm=true` representa autorização concreta,
   incluindo suboperações de batch/pipeline. Login privado é feito no programa oficial.
5. Preserve pending, partial e failed; downloads precisam de arquivos reais e hashes.

## Capacidades e limites

Notebooks, fontes, pesquisa/importação, chats síncronos e assíncronos,
consultas entre notebooks, organização, notas, compartilhamento, Studio,
downloads/exportação, uso, perfis e diagnóstico são derivados do catálogo
instalado. MCP usa o perfil ativo upstream. Enterprise é experimental e
depende da configuração/autorização do provedor; suporte de interface não
comprova execução em uma conta Enterprise.

A CLI e o servidor MCP são oficiais do projeto citado, e usam APIs internas
do serviço Google. Uma conexão operacional não valida cientificamente seu
conteúdo. Registre somente estado e hashes no MetaBus, sem notas de confiança,
cookies, textos privados ou alegações históricas de disponibilidade.
