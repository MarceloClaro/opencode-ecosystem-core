# SPEC-935-R1226 — Propagar status R1224 aos consumidores MCP ativos

- **Status:** especificada
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

## Reversão / limites

- Se o túnel não voltar a polling, não iniciar outro processo fora do runner; registrar o estado e parar.
- A reconexão de um único MCP pode produzir uma breve indisponibilidade desse servidor, autorizada pelo pedido do operador; não reiniciar o serviço OpenCode inteiro.
- A interface ChatGPT/plug-in não é controlada pela sessão local. Se o ChatGPT mantiver cache/estado de conexão antigo, será necessária ação de refresh/reconexão no cliente; não alegar visibilidade antes de uma chamada real no Chat.
