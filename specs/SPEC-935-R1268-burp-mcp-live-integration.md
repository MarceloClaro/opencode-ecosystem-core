---
spec_id: SPEC-935-R1268
title: Integração local do BApp Burp MCP oficial com OpenCode
component: integrations.burp_mcp_live
status: specified
test_file: tests/test_r1268_burp_mcp_live_integration.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1268-ENDPOINT:
      - tests/test_r1268_burp_mcp_live_integration.py::test_burp_server_uses_exact_loopback_streamable_http_endpoint
    R1268-DENY:
      - tests/test_r1268_burp_mcp_live_integration.py::test_burp_tool_calls_are_denied_in_project_permissions
    R1268-PERSIST:
      - tests/test_r1268_burp_mcp_live_integration.py::test_config_generator_preserves_burp_server_and_deny_rule
---

# SPEC-935-R1268 — BApp oficial Burp MCP e configuração OpenCode

## Objetivo

Concluir, mediante autorização explícita do usuário, a integração local do
BApp oficial PortSwigger MCP com Burp Community e o OpenCode Ecosystem Core.
Compilar somente o repositório oficial `PortSwigger/mcp-server` no commit
`291034081160bc944b6df3eccd60c6fc99b477e1`, carregar o artefato no Burp pela
interface gráfica com aprovações locais de uso único e configurar o projeto
OpenCode para o endpoint Streamable HTTP oficial.

## Escopo, proveniência e restrições

- Código-fonte upstream: `https://github.com/PortSwigger/mcp-server`, commit
  `291034081160bc944b6df3eccd60c6fc99b477e1`; assinatura observada: ausente.
- Manifesto BApp declara versão 1.4.0, Community e Pro; licença upstream GPL-3.0.
- Build documentado: `./gradlew embedProxyJar`; saída esperada
  `build/libs/burp-mcp-all.jar`.
- Checkout, Gradle user home, JDK/toolchain e artefatos de build ficam em
  `/tmp/opencode`; não instalar dependências globalmente.
- Endpoint único permitido: `http://127.0.0.1:9876/mcp`. Não aceitar bind em
  `0.0.0.0`, endereço LAN, portproxy ou hostname externo.
- Cada clique/tipagem de GUI usa token de aprovação local, de uso único, criado
  pelo operador desktop; não usar automação de mouse, shell ou X11 para
  contornar o gate.
- Depois de carregar o BApp, não editar as configurações do Burp. Se o listener
  não estiver exclusivamente em `127.0.0.1:9876`, parar sem configurar o
  OpenCode.
- Validação de protocolo limitada a `initialize`/handshake e `tools/list`.
  Nenhuma chamada `tools/call`, requisição a alvo, leitura de proxy history,
  scanner, alteração de configuração ou outro efeito será executado.
- Na configuração OpenCode, negar todas as ferramentas do servidor `burp_*`
  durante esta validação, mantendo apenas a conexão/catalogação MCP.

## Critérios de aceitação executáveis

- `R1268-ENDPOINT`: a configuração do projeto usa o tipo remoto Streamable
  HTTP e exatamente `http://127.0.0.1:9876/mcp`; o servidor não está desativado.
- `R1268-DENY`: as permissões do projeto negam `burp_*`, sem regra de aprovação
  automática ou permissão ampla para executar ferramentas Burp.
- `R1268-PERSIST`: a geração de configuração preserva a entrada MCP aninhada e
  as regras locais `permissions`, evitando que regenerar `opencode.json` remova
  a proteção.

## Gates operacionais (evidência fora da suíte unitária)

1. Conferir HEAD exato, manifesto e licença antes de executar Gradle; usar
   `GRADLE_USER_HOME` isolado em `/tmp/opencode` e Gradle sem daemon.
2. Confirmar hash/manifesto do JAR construído e carregá-lo somente pela UI do
   Burp. Se a UI ou aprovação única não estiver disponível, interromper.
3. Observar `ss -ltnp` com o único listener MCP em `127.0.0.1:9876` antes de
   editar a configuração OpenCode.
4. Validar sintaxe e geração do `opencode.json`; efetuar somente a negociação
   MCP e `tools/list`, registrando método, endpoint, resultado e número de
   ferramentas, sem chamar nenhuma delas.
5. Confirmar que não houve tráfego dirigido a alvos nem chamadas `tools/call`.

## Verificação e limites

O ciclo de software deve registrar RED por falha de asserção antes da mudança,
GREEN após a configuração/implementação e passar o SpecVerifier. Os gates de
instalação e handshake são observações operacionais locais, não revisão externa
nem validação de segurança do Burp, do BApp ou de qualquer alvo.
