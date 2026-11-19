---
spec_id: SPEC-935-R1226
title: Propagar status R1224 aos consumidores MCP ativos
status: green
validation_scope: local_runtime
component: OpenCode v2 MCP lifecycle + integrations/chatgpt_tunnel_full_mcp.py + integrations/ecosystem_mcp_tunnel.py
test_file: tests/test_r1222_mcp_discovery_bridge.py
---

# SPEC-935-R1226 — Propagar status R1224 aos consumidores MCP ativos

- **Status:** executada e validada nas superfícies locais; interface ChatGPT externa não observável por esta sessão
- **Data:** 2026-11-19
- **Origem:** pedido explícito para resolver a pendência, auditar e tornar o novo status visível no Chat.
- **Escopo:** renovar somente os consumidores `ecosystem-network` do OpenCode v2 e o túnel MCP completo gerenciado, que ainda mantêm processos anteriores à mudança R1224.

## Problema observado

- A CLI local entrega `readiness.state=CONFIG_ONLY`.
- A ferramenta MCP ativa `ecosystem_integration_status` continua sem `readiness`.
- O processo local `integrations.ecosystem_mcp` (PID observado 829562) e o filho do túnel (PID 719491) foram iniciados antes da alteração.
- O túnel gerenciado informa `polling_confirmado`, mas esse sinal sozinho não atesta catálogo/invocação no cliente.

## Plano controlado

1. Desconectar e reconectar somente `ecosystem-network` por API MCP do OpenCode v2; não reiniciar o serviço global nem os outros 32 MCPs.
2. Parar e iniciar somente o túnel completo gerenciado por `integrations.chatgpt_tunnel_full_mcp`, com o `--confirm` exigido pelo runner. A operação usa a chave somente por referência `file:`; não imprime nem lê seu conteúdo.
3. Fazer handshake MCP novo no bridge local, listar ferramentas e chamar `ecosystem_integration_status` pelo transporte stdio; confirmar presença de `readiness`, `CONFIG_ONLY`, `executed=false` e `execution_verified=false`.
4. Verificar novamente o polling do túnel e registrar os limites: sem chamada do cliente ChatGPT, não declarar descoberta/invocação no UI remoto como comprovada.

## Critérios de aceitação

1. A sessão MCP OpenCode reconectada retorna `readiness.state=CONFIG_ONLY` e os estágios não sondados.
2. O MCP completo inicia handshake, lista as 26 ferramentas esperadas e sua chamada real de status retorna o campo R1224.
3. O túnel volta a `polling_confirmado` com PID novo e timestamp recente; nenhum outro túnel com o mesmo ID é iniciado.
4. Nenhuma configuração, credencial, permissão, plugin externo ou serviço global é modificado.
5. O relatório separa evidência local/túnel de visibilidade efetivamente confirmada na interface do ChatGPT.

## Critérios de aceitação executáveis

- `R1226-LOCAL-MCP` A reconexão direcionada do OpenCode MCP propaga o retorno R1224 na sessão ativa.
- `R1226-BRIDGE-CATALOG` O bridge novo lista as 26 ferramentas e executa a ferramenta de status com readiness CONFIG_ONLY.
- `R1226-TUNNEL` O runner gerenciado volta a polling_confirmado em PID novo, sem tocar credenciais/configuração.
- `R1226-CLIENT-BOUNDARY` O relatório distingue evidência do MCP/túnel da invocação não observada na UI ChatGPT externa.

## Reversão / limites

- Se o túnel não voltar a polling, não iniciar outro processo fora do runner; registrar o estado e parar.
- A reconexão de um único MCP pode produzir uma breve indisponibilidade desse servidor, autorizada pelo pedido do operador; não reiniciar o serviço OpenCode inteiro.
- A interface ChatGPT/plug-in não é controlada pela sessão local. Se o ChatGPT mantiver cache/estado de conexão antigo, será necessária ação de refresh/reconexão no cliente; não alegar visibilidade antes de uma chamada real no Chat.

## Evidências e auditoria

- **MCP OpenCode v2:** usando a API oficial `POST /api/experimental/mcp/{server}/disconnect` e `/connect`, com `location.directory=/home/marceloclaro/opencode-ecosystem-core`, foi renovado somente `ecosystem-network`. O processo mudou de PID `829562` para `839995`; os 33 MCPs aparecem `connected` depois da operação.
- **Chamada pela ferramenta da sessão atual:** `ecosystem_integration_status` agora retorna `status=config_checked`, `readiness.state=CONFIG_ONLY`, `executed=false`, `execution_verified=false`, `configured_mcp_count=33` e `issues_count=0`.
- **Túnel gerenciado:** PID anterior `719476` foi encerrado pelo runner, e o novo PID `840190` usa `integrations.ecosystem_mcp_tunnel`. O primeiro retorno de `start --confirm` foi `aguardando_polling` com `readyz=true`; em seguida, o health local registrou sucesso e `consecutive_failures=0`. Status posterior: `polling_confirmado`, último poll `2026-11-19T09:21:45.345032783Z`.
- **Bridge/MCP completo em processo novo:** handshake MCP `2025-11-25`; `tools/list` retornou 26 ferramentas, incluindo `ecosystem_integration_status`, `ecosystem_run`, `ecosystem_workflow` e `ecosystem_browser`. Chamada real ao status retornou `CONFIG_ONLY` e as quatro fases em `not_probed`; `executed=false` e `execution_verified=false`.
- **Smoke test:** a primeira execução obteve a resposta correta, mas um assert local esperava nome de servidor incorreto (`opencode-ecosystem-core` em vez de `ecosystem-network`); corrigido somente o assert e repetido com sucesso. Não foi uma falha do MCP.
- **Regressão:** suíte focal `.venv/bin/python -B -m pytest -q tests/test_r662_integration_surface.py tests/test_r640_ecosystem_surface.py tests/test_r1090_chatgpt_status_mcp.py tests/test_r1222_mcp_discovery_bridge.py` → `40 passed`; `git diff --check` passou.
- **Auditoria de limites:** configuração/inventário, conexão do OpenCode, tool list/call do bridge novo e polling do túnel estão observados. Não foi realizada chamada pelo UI ChatGPT externo; logo, sua cache/visibilidade final permanece sem prova nesta sessão. O conteúdo está disponível no MCP local e no bridge recém-iniciado, mas o cliente externo pode exigir refresh/reconexão.
- **Inspeção do desktop:** `desktop_status` e `desktop_list_apps` foram tentados em modo somente leitura; ambos reportaram `binary_not_found` (`agent-desktop` ausente). Portanto, não foi possível confirmar ou operar a janela do ChatGPT/Desktop por acessibilidade.
- **Revisão independente:** a solicitação a `ecosystem_run` foi bloqueada sem atribuição de agente (`Nenhum agente interno elegível`); portanto, a auditoria registrada é do orquestrador e dos testes, não parecer externo.
- **Registro evolutivo:** `R1227` registrado com score interno `7.5` (`legacy=true`, não é validação externa). Reflexão MetaBus `828bb42b-a3c2-41d6-a44e-950416cc8575` registrada com score interno `0.6`; ledger atualizado pela EMA para `0.56045`. O score é metacognitivo heurístico e não promove evidência de visibilidade externa.
