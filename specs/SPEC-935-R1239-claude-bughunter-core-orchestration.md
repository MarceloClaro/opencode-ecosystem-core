---
spec_id: SPEC-935-R1239
title: Integrar Claude-BugHunter ao orquestrador por catálogo defensivo fechado
component: integrations.claude_bughunter_catalog
status: specified
test_file: tests/test_r1239_claude_bughunter_orchestration.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1239-CATALOG:
      - tests/test_r1239_claude_bughunter_orchestration.py::test_catalog_validates_pinned_provenance_and_exposes_only_safe_route
      - tests/test_r1239_claude_bughunter_orchestration.py::test_catalog_fails_closed_when_package_manifest_is_tampered
    R1239-ORCHESTRATION:
      - tests/test_r1239_claude_bughunter_orchestration.py::test_status_and_plan_are_exposed_through_marcelo_claro
      - tests/test_r1239_claude_bughunter_orchestration.py::test_cli_and_mcp_plan_dispatch_only_to_primary_orchestrator
    R1239-BURP-GATE:
      - tests/test_r1239_claude_bughunter_orchestration.py::test_official_burp_mcp_authorization_is_recorded_but_prerequisites_block_enablement
      - tests/test_r1239_claude_bughunter_orchestration.py::test_no_burp_server_or_target_testing_is_claimed
---

# SPEC-935-R1239 — Integração Claude-BugHunter no orquestrador

## Objetivo

Conectar o snapshot inerte R1236 ao Core por uma interface explícita e
fail-closed, sob MarceloClaro. O catálogo poderá expor apenas a skill local
original `claude-bughunter-safe`; não promoverá nomes, descrições, comandos,
índices ou instruções do snapshot upstream a rotas invocáveis.

O usuário autorizou o uso do servidor MCP oficial PortSwigger. A inspeção local
somente de leitura não encontrou Java, o proxy `mcp-proxy-all.jar` nem diretórios
Burp nas raízes pesquisadas. Portanto, esta alteração registrará a autorização e
o bloqueio por pré-requisitos ausentes; **não** gravará uma configuração MCP
quebrada nem afirmará que o servidor foi habilitado. A configuração será uma
etapa separada depois que os componentes locais existirem e forem identificados.

## Contrato do catálogo

1. Ler somente os manifestos locais `federation/claude-bughunter-package-r1236.json`
   e `federation/claude-bughunter-mcp-r1239.json`. Não abrir nem indexar arquivos
   do snapshot, inclusive `cbh/data/skill_index.json`.
2. Validar schema, repositório, commit fixado, SHA-256 do arquivo-fonte, raiz,
   contagens observadas, declarações de licença e estados inertes. Rejeitar
   manifesto malformado, divergente, com caminho externo ou com qualquer skill,
   comando, execução ou MCP upstream marcado como ativo.
3. Emitir somente um registro de rota, para a skill local
   `.opencode/skills/claude-bughunter-safe/SKILL.md`, com política defensiva e
   execução automática desabilitada. O manifesto de 341 arquivos pode ser
   validado estruturalmente; a API não expõe a lista integral de arquivos nem
   declara nova verificação em runtime dos hashes de conteúdo.
4. Qualquer status inválido ou ausente falha fechado. O handoff não é execução,
   não autoriza acesso a alvos e não altera permissões.

## Contrato de orquestração

- `CoreIntegrationService` oferece status do pacote e um plano explícito para
  `claude-bughunter-safe`.
- `MarceloClaroOrchestrator` continua como ponto de entrada; incorpora o status
  em `integration_status()` e expõe o plano sem executar instruções.
- A superfície MCP e o comando de integração encaminham status/plano ao mesmo
  orquestrador. A resposta distingue `instruction_only`, execução observada e
  disponibilidade; neste fluxo `executed=false` e
  `execution_verified=false`.
- Nenhuma skill ou comando upstream será registrado no OpenCode, no catálogo de
  agentes, no Blackboard ou no dispatcher.

## Burp MCP oficial: autorização e bloqueio técnico

- Provedor selecionado pelo usuário: PortSwigger oficial, transporte local stdio
  proxy para o servidor SSE Burp em `http://127.0.0.1:9876`.
- Autorização registrada: preparar/habilitar a integração oficial quando os
  componentes locais estiverem disponíveis. A autorização não cobre instalação
  de Burp/extensão/proxy, leitura de credenciais, inicialização do Burp,
  conexão MCP, chamadas a ferramentas ou requisições HTTP.
- Observação local read-only: `java`, proxy JAR e diretórios Burp não foram
  encontrados nas raízes pesquisadas (`~/.BurpSuite`, `~/.local`, `/opt`,
  `/usr/local`; busca de diretórios sob o home limitada a profundidade 4).
- A configuração MCP não será adicionada ou habilitada enquanto faltarem
  launcher e proxy previamente instalados. Não usar `type=remote` diretamente:
  a documentação OpenCode consultada descreve transporte remoto Streamable HTTP,
  enquanto o serviço PortSwigger documentado aqui fornece SSE e um proxy stdio.
- Não iniciar Burp, proxy, OpenCode ou qualquer servidor nesta tarefa. Não
  enviar requisições, executar scanners, testar alvos nem ler configuração ou
  ferramentas do Burp. A autorização para habilitar MCP não é autorização para
  testes dinâmicos; edição da configuração do Burp não foi autorizada.
- O plano reporta `authorization_granted=true`, `enabled=false`,
  `status=blocked_missing_local_runtime` e os componentes ausentes, sem
  afirmar disponibilidade operacional. Para continuar, o operador deverá
  instalar/configurar a extensão oficial e fornecer caminhos locais verificáveis;
  uma nova spec cobrirá a configuração client-side e seus testes.

## Critérios de aceitação executáveis

- `R1239-CATALOG`: manifesto e proveniência são validados; a única rota exposta é
  a skill Core defensiva; adulteração resulta em bloqueio.
- `R1239-ORCHESTRATION`: status e plano são acessíveis via MarceloClaro, CLI e
  MCP, sempre como plano instrucional não executado.
- `R1239-BURP-GATE`: registra-se a autorização específica, mas o MCP permanece
  sem configuração ativa enquanto faltarem pré-requisitos. Nenhum alvo é testado
  e nenhum servidor/configuração externa é iniciado.

## Verificação

- Criar testes antes da implementação e observar RED válido.
- Executar testes da R1239, regressão da R1235/R1236 e superfície de integração
  R662; validar par RED/GREEN, SpecVerifier, `git diff --check` e doctor.
- Não consultar rede, instalar dependências, iniciar servidores ou executar
  conteúdo do snapshot.

## Fora de escopo

- Expor/invocar automaticamente quaisquer instruções do Claude-BugHunter
  upstream.
- Instalar ou iniciar PortSwigger Burp Suite, sua extensão ou proxy MCP.
- Configurar credenciais, autorização de hosts, limites do scanner ou opções do
  projeto Burp.
- Enviar tráfego, testar aplicações/alvos ou tratar autorização de integração
  como autorização para avaliação dinâmica.
