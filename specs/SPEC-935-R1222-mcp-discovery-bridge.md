# SPEC-935-R1222 — Compatibilidade de descoberta MCP e plugin WSL com status direto

- **Status**: implementado; GREEN local; chamada real no Chat executada em 18/11/2026; verificação limitada ao tool call, não à execução de tarefas do orquestrador.
- **Data**: 2026-11-18
- **Origem**: health do túnel R1218 permaneceu `components.mcp.tools_list.ok=false` embora o servidor local liste 26 ferramentas; plugin `opencode-ecosystem-core@marceloclaro-core-global` não expõe ferramenta própria invocável no ChatGPT Chat.
- **Escopo**: (1) responder `server/discover` no stdio do túnel sem modificar `tunnel-client` nem `app.asar`; (2) preparar pacote de plugin WSL capaz de mapear uma conexão MCP registrada no ChatGPT para uma ferramenta direta.

## Problema

O runtime do túnel recebe requisições `server/discover` do cliente OpenAI. O FastMCP `1.28.1` interpreta esse método como `tools/call`, `tools/list`, `resources/read` ou `resources/subscribe` e responde com erro de validação. Por isso a descoberta termina em `state=initialized`, mas `tools_list.ok=false` e `tool_names=[]`. Paralelamente, o plugin WSL instalado contém `mcpServers`, mas não contém o mapping `apps`/`.app.json` observado no plugin de status funcional; presença de arquivo de configuração não prova exposição de ferramenta no Chat.

## Decisão

Adicionar um bridge stdio delgado à frente do MCP completo:

1. Responder `server/discover` localmente com `resultType=complete`, `supportedVersions=["2025-11-25"]`, capacidades declaradas e `_meta.io.modelcontextprotocol.serverInfo`.
2. Não anunciar suporte a `2026-07-28`; o bridge é uma ponte de compatibilidade, não uma implementação do protocolo moderno.
3. Encaminhar integralmente todos os outros métodos JSON-RPC para `integrations.ecosystem_mcp`, preservando as 26 ferramentas e o protocolo `2025-11-25`.
4. Atualizar o runner R1218/R1220 para iniciar o bridge por padrão.
5. Estender o gerador de plugin ChatGPT/Codex com opção explícita `--app-id`, que grava `.app.json` e adiciona `apps` aos manifestos. Sem `--app-id`, nenhum mapping é inventado.
6. Manter `ecosystem_integration_status` como ferramenta de diagnóstico read-only; a chamada real no Chat continua sendo a única prova de roteamento.

## Não-objetivos

- Não modificar `~/.codex/config.toml`, auth, modelos, provedores ou permissões.
- Não modificar `tunnel-client`, `app.asar`, `00-ATIVAR.cmd`, atalhos ou credenciais.
- Não ler/imprimir/copiar `runtime.key`; o runner continua usando apenas `file:<caminho>`.
- Não gerar `asdk_app_...` localmente nem alegar que um ID inventado foi registrado no ChatGPT.
- Não declarar `chatgpt_chat` verificado sem chamada manual no Chat; chamada registrada em 18/11/2026, com escopo limitado ao `tools/call` de diagnóstico.

## Contrato

1. `make_discover_result(request_id)` deve produzir uma resposta JSON-RPC com:
   - `resultType="complete"`;
   - `supportedVersions=["2025-11-25"]`;
   - `capabilities` contendo `tools`, `resources` e `prompts`;
   - `_meta["io.modelcontextprotocol.serverInfo"]` com `name="ecosystem-network"` e `version="1.28.1"`;
   - `ttlMs=0` e `cacheScope="private"`.
2. `process_line(line, send_to_child, send_to_client=None)` deve:
   - responder `server/discover` ao cliente sem encaminhar ao filho;
   - encaminhar qualquer outro JSON-RPC, incluindo `initialize`, `notifications/initialized` e `tools/list`;
   - encaminhar linhas inválidas sem levantar exceção no bridge.
3. `python -B -m integrations.ecosystem_mcp_tunnel` deve:
   - responder `server/discover`;
   - aceitar `initialize` com `protocolVersion="2025-11-25"`;
   - listar exatamente as 26 ferramentas do MCP completo.
4. `integrations/chatgpt_tunnel_full_mcp.py` deve usar o bridge por padrão em `MCP_MODULE`, `build_mcp_command()` e `validate_core()`.
5. `integrations/chatgpt_plugin.py::build_plugin()` deve aceitar `app_id=None`; quando informado, criar `.app.json` com `{"apps": {NAME: {"id": app_id}}}` e incluir `apps` nos manifestos; quando ausente, não criar o arquivo.
6. O pacote gerado deve continuar sem segredos e com `installed=false`, `executed=false`.

## Critérios de aceitação

- RED antes da implementação.
- Testes unitários do bridge passam.
- Teste end-to-end via subprocess responde `server/discover`, `initialize` e `tools/list` com 26 ferramentas.
- Testes R1218/R1220 continuam passando após a troca do módulo padrão.
- Testes R912 continuam passando com `app_id=None`.
- Novo teste confirma `.app.json` e `apps` somente quando `app_id` é fornecido explicitamente.
- `doctor` permanece sem falhas e sem elevação de confiança.
- Nenhuma alegação de ativação no Chat sem evidência de chamada real.

## Evidência R1222

- RED registrado antes da implementação: `ModuleNotFoundError: No module named 'integrations.ecosystem_mcp_tunnel'` e falhas em `MCP_MODULE`/`app_id`.
- GREEN final: `.venv/bin/python -B -m pytest -q tests/test_r1222_mcp_discovery_bridge.py tests/test_r912_chatgpt_plugin.py tests/test_r1218_chatgpt_tunnel_full_mcp.py tests/test_r1220_chatgpt_tunnel_persistente.py` → `46 passed`.
- Teste end-to-end via subprocess: `server/discover` responde `2025-11-25`, `initialize` negocia `2025-11-25`, `tools/list` devolve `26` ferramentas com `ecosystem_integration_status`.
- Runner padrão: `integrations/chatgpt_tunnel_full_mcp.py::MCP_MODULE = "integrations.ecosystem_mcp_tunnel"`; `validate_core()` exige o bridge; R1218/R1220 permanecem verdes.
- Gerador de plugin: `--app-id` e `--server-module` disponíveis; `.app.json` e `apps` surgem somente com ID explícito; ID inválido não cria diretório; ZIP inclui `.app.json`.
- Pacotes candidatos sem `app_id` (instalados/executados = `false`):
  - `/tmp/opencode/r1222/opencode-ecosystem-core-status-wsl.zip` SHA-256 `e872ec7307e2c0b843a22efad8e1320aa52a55f51e3c9ba8e4eeb19d7322bf9e` (`integrations.chatgpt_status_mcp`).
  - `/tmp/opencode/r1222/opencode-ecosystem-core-full-wsl.zip` SHA-256 `aae5b0b1586a4bee483cefcd86d42d8ab20a0b4e5afc00b00b66721e774784a5` (`integrations.ecosystem_mcp_tunnel`).
- Doctor pós-implementação: `overall=degraded`, `0 falhas`, `6 avisos`, `314 specs`, `860/860 ciclos` (inclui ciclo `R1222`, `score=8.7`), `29 entradas episódicas`, `337 agentes` — sem elevação de confiança.
- Runtime reiniciado explicitamente (`stop` + `start --confirm`): PID `719476`, health `http://127.0.0.1:38091`, `tunel=polling_confirmado`, `mcp=integrations.ecosystem_mcp_tunnel`.
- Health imediatamente após o reinício: `live=true`, `ready=true`, `control-plane=polling`, `mcp.state=not_observed`, `initialize_epoch=0`, `tools_list.ok=false`.
- Após a chamada real no Chat: health `mcp.status=ok`, `mcp.state=initialized`, `initialize_epoch=1`, `tools_list.ok=false`; log `08:42:26`/`08:42:36` registrou `dispatcher forwarded command to MCP server` e `CallToolRequest` processado às `08:42:27`.
- Chamada real no Chat: `ecosystem_integration_status` via plugin `OpenCode Core Status — Chat` respondeu `spec_id=SPEC-935-R662`, `status=config_checked`, `executed=false`, `execution_verified=false`, `issues=[]`, `mcp.configured_count=33`, `local_count=32`, `remote_count=1`.
- Comparação com chamada direta no Core WSL (`ecosystem-network_ecosystem_integration_status`): mesmos `spec_id`, `orchestrator`, `status`, `executed`, `execution_verified`, `issues` e contagens MCP; a resposta direta inclui ainda `components` (`agents=337`, `cli=39`, `plugins=75`, `skills=95`) e `ecosystems_present=[antigravity,chatgpt,claude,codex]`. A versão do Chat foi resumida na transcrição fornecida; não afirmar igualdade byte a byte.
- `executed=false` e `execution_verified=false` são semântica do diagnóstico, não falha do tool call: a resposta ter chegado ao Chat prova o roteamento ChatGPT → WSL → Core para esta ferramenta; não prova execução de tarefas nem conectividade operacional dos 33 MCPs.
- Pendente: provar execução dos plugins Desktop e Local e, se necessário, `tools_list.ok=true`; nenhuma dessas condições está provada nesta spec.
