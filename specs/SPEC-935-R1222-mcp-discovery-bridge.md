# SPEC-935-R1222 — Compatibilidade de descoberta MCP e plugin WSL com status direto

- **Status**: proposto; RED em execução.
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
- Não declarar `chatgpt_chat` verificado sem chamada manual no Chat.

## Contrato

1. `make_discover_result(request_id)` deve produzir uma resposta JSON-RPC com:
   - `resultType="complete"`;
   - `supportedVersions=["2025-11-25"]`;
   - `capabilities` contendo `tools`, `resources` e `prompts`;
   - `_meta["io.modelcontextprotocol.serverInfo"]` com `name="ecosystem-network"` e `version="1.28.1"`;
   - `ttlMs=0` e `cacheScope="private"`.
2. `process_line(line, send)` deve:
   - responder `server/discover` sem encaminhar ao filho;
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

- Pendente.
