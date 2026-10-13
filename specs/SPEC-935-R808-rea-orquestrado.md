---
spec_id: SPEC-935-R808
title: REA local coordenado por MarceloClaro e revisão do ecossistema
component: integrations/rea_bridge, marceloclaro/orchestrator, integrations/ecosystem_mcp
status: implemented
round_id: R808
test_file: tests/test_r808_rea_bridge.py
---

# SPEC-935-R808 — REA coordenado

## Objetivo

Integrar o projeto solicitado https://github.com/MarceloClaro/rea à execução
local do Core. MarceloClaro permanece a entrada de coordenação e registra
observações no MetaBus. A revisão do ecossistema cobre diagnóstico estrutural,
configuração reproduzível, rede, workflows, MCP e suíte de regressão.

## Decisão arquitetural

Usar adaptador de processo/MCP com runtime isolado em
`~/.local/share/opencode-core/rea`, sem incorporar o repositório externo ao Git
do Core. `REA_SOURCE_DIR` permite outra instalação explícita. Não substituir
Reversa Universal: REA inspeciona aplicações e artefatos; Reversa conserva seu
papel existente de análise e planejamento. A entrada coordenada expõe catálogo,
identidade de sessão e análise estática JavaScript. A configuração OpenCode
oferece também o servidor REA completo, com comando reproduzível e instruções
para chamar a ponte coordenada nas operações disponíveis.

Alternativas avaliadas: copiar fontes para o Core aumenta o custo de atualização;
usar somente `npx @latest` não fixa proveniência nem comprova disponibilidade.
O checkout isolado conserva licença, commit e versão e permite execução real.

## Contratos de aceite

1. Adaptador descobre runtime e versão sem iniciar aplicações alvo; ausência,
   erro de protocolo, resposta isError e timeout nunca viram sucesso.
2. Catálogo provém de initialize/tools/list do servidor instalado, e identidade
   de `binary_session`; disponibilidade de catálogo não comprova providers.
3. Análise usa `analyze_javascript_application` com caminho local explícito,
   timeout finito, chamada sem shell e preserva a resposta Evidence completa.
   A interface coordenada admite somente operações estáticas documentadas;
   execução de processos, navegador e instalação não são efeitos implícitos.
4. Orquestrador expõe `rea_action(config)` e registra observação com origem,
   estado e hash; não atribui validação externa ou promove confiança a partir
   da conclusão operacional. MCP `ecosystem_rea` chama esse método.
5. CLI `python3 -m marceloclaro.cli rea` admite status, catalog, session e
   analyze; `/rea` orienta o agente primário. Gerador e `opencode.json` devem
   coincidir, incluindo alterações anteriores existentes no catálogo.
6. Testes herméticos precedem implementação; subprocessos simulados são
   identificados como tal. Uma análise real, handshake MCP e testes de regressão
   são registrados separadamente em outputs/rea-r808.
   Para contexto finito, `rea_*` fica oculto por padrão nos agentes. O gateway
   conserva resposta integral em `.opencode/rea/evidence/<sha256>.json` e
   entrega resumo com origem, estatísticas e limites; `catalog` entrega nomes
   e remete aos schemas completos no arquivo. CLI e adaptador conservam a
   resposta integral. Resumo não altera autoridade ou confiança da Evidence.
7. Revisão registra achados, testes executados e limitações. Não declarar todos
   os componentes saudáveis quando houver falhas, skips ou dependências ausentes.
   O launcher de `arxiv-mcp` deve usar a resolução de `uvx` já adotada por
   `fetch`, pois a conexão real identificou instalação existente fora do PATH.

## Plano de implementação

1. Instalar/compilar checkout externo e verificar identidade e ferramentas.
2. Criar testes RED e adaptador MCP com limites e respostas rastreáveis.
3. Conectar orquestrador, CLI, gateway MCP e gerador OpenCode; executar GREEN.
4. Executar análise real coordenada, reproduzir configuração e suíte do Core;
   corrigir regressões demonstradas pertinentes e revisar os resultados.
5. Documentar uso, relatório de revisão e ciclo de evolução sem alegação externa.

## Limites

Análise nativa depende de provider externo compatível. Não instalar ferramentas
licenciadas nem assumir autenticação de executores. Execução MCP demonstra
conectividade local; testes internos não equivalem a auditoria externa.
