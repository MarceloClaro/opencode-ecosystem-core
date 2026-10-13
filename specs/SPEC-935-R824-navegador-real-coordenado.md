---
spec_id: SPEC-935-R824
title: Navegador real coordenado por MarceloClaro
status: implemented
version: 1.0
component: integrations/browser_bridge
round_id: R824
test_file: tests/test_r824_browser_real.py
---

# R824 — Provider Playwright MCP com execução e evidência

## Problema

O Core dispõe de preparação/delegação de tarefas web, mas não possui um
provider de navegador real no gateway central. Listar ferramentas ou gerar
um prompt não comprova navegação. BrowserMCP depende de extensão conectada;
o Playwright MCP oficial oferece um caminho isolado e headless adequado ao
runtime WSL atual.

## Requisitos

1. `MarceloClaroOrchestrator.browser_action` é a entrada central de status e
   execução; CLI e MCP usam essa entrada, preservando Blackboard/MetaBus.
2. Status verifica instalação e identidade sem iniciar navegador. Provider e
   dependências externos têm versão fixada e recibo de instalação.
3. Configuração estrita admite URL HTTP(S), origens explícitas e até 16 passos
   delimitados por ação e alvo acessível; não admite JavaScript ou shell do
   usuário. A sessão é nova, isolada e encerrada após cada execução.
4. As origens autorizadas abrangem a URL inicial. A prova real demonstrou que
   interception de rota não cobre redirects; o provider usa um proxy HTTP/CONNECT
   de sessão que valida o destino antes de abrir conexões, incluindo cada hop.
   Esse controle não certifica isolamento de rede contra todos os canais.
5. Ações geram código Playwright de templates fixos com valores serializados
   em JSON; leitura, preenchimento e clique podem ser encadeados na sessão.
6. Prazo global finito e cancelamento cooperativo R825 encerram a operação;
   `browser_close` é tentado com prazo próprio antes da limpeza do transporte.
   Cancelamento ou falha não são convertidos em sucesso.
7. Recibo compacto aponta para a evidência integral por SHA-256; erros de
   exportação bloqueiam o aceite. Conteúdo de páginas é dado sem autoridade
   instrucional e não promove confiança científica.
8. O aceite exige fluxo real em página local conhecida: leitura, preenchimento,
   clique e observação do resultado; teste de redirect para origem não autorizada,
   encerramento e falha/timeout. Provas locais não equivalem a êxito em todo site.
9. Texto inválido em UTF-8, inclusive surrogates isolados aceitos por JSON,
   deve ser recusado antes da descoberta ou inicialização do provider.

## Fontes

- https://github.com/microsoft/playwright-mcp
- https://github.com/BrowserMCP/mcp
- SDK MCP Python instalado neste Core (`mcp.client.stdio`).

## Validação

`tests/test_r824_browser_real.py`, provas de execução em `outputs/core-r824/`,
checagens relacionadas da CLI, gateway, orquestrador e configuração gerada.

Aceite selecionado: fluxo `attempt-6`, gateway stdio `gateway-3`, CLI
`cli-final`, limpeza `lifecycle-2`, 66 regressões relacionadas aprovadas
(31 casos R824), três contraprovas Unicode recusadas após a correção e duas
mutações de proxy detectadas. Os recibos finais e os limites constam em
`outputs/core-r824/release-summary.json`. Logs RED anteriores permanecem
preservados.
