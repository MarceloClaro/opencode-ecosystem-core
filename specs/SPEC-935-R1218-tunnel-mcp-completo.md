# SPEC-935-R1218 — Túnel ChatGPT com MCP completo

- **Status**: implementado; runtime iniciado com `polling_confirmado`, verificação no chat ainda manual
- **Data**: 2026-11-18
- **Origem**: decisão explícita do operador pela opção 3 (“MCP completo”), com aceitação de risco para navegador/download/execução externa.
- **Escopo**: expor ao chat via Secure MCP Tunnel o módulo completo `integrations.ecosystem_mcp`, sem modificar o pacote `tunnel-client`, a configuração do Codex, auth, modelos ou permissões.

## Problema

O atalho `OpenCode Ecosystem Tunnel (WSL)` usa `integrations/chatgpt_status_mcp.py`, que registra somente `ecosystem_integration_status`. Isso não satisfaz a integração ativa pedida pelo operador. O módulo completo `integrations.ecosystem_mcp` registra 26 ferramentas, incluindo superfícies com `destructiveHint=true` e `openWorldHint=true`.

## Não-objetivos

- Não promover confiança por registro/configuração.
- Não ler, imprimir ou copiar o conteúdo de `runtime.key`.
- Não alterar `~/.codex/config.toml`, plugins, MCPs locais do Codex, modelos ou provedores.
- Não patchear `launcher.py`, `core_process` ou o binário vendored.
- Não habilitar `--log.http-raw-unsafe` nem `--tracing.enabled`.

## Contrato

1. O runner `integrations/chatgpt_tunnel_full_mcp.py` deve operar em três ações:
   - `status`: somente leitura; nunca inicia processo.
   - `plan`: padrão; imprime o plano sanitizado sem iniciar processo ou abrir rede.
   - `start`: exige `--confirm`; inicia o binário vendored com `--mcp.command` apontando para `.venv/bin/python -B -m integrations.ecosystem_mcp`.
   - `stop`: encerra somente o PID registrado cuja linha de comando contenha o ID do túnel e o binário gerenciado.
2. O ID do túnel é `tunnel_6af9e26d203c8191ab67eb7e9aa3d805`.
3. A chave de execução é referenciada apenas como `file:<caminho>`; o arquivo deve ser regular, pertencer ao usuário, ter modo `0600` e não ser lido pelo runner.
4. O bundle oficial `tunnel-client-runtime-v0.0.21-linux-amd64.zip` deve ter SHA-256 `fa53182b766aeaceb652d86aee291c48daf7b90b5d73586dba370f4c1801325e` antes da extração.
5. O estado do runner fica em `/home/marceloclaro/.local/state/opencode-core-tunnel-full` com modo `0700`; logs e arquivos de PID com modo `0600`.
6. O comando MCP deve usar ambiente mínimo e sanitizado (`PATH`, `LANG`, `HOME`) e diretório de trabalho igual à raiz do Core.
7. O túnel deve usar `https://api.openai.com`, `--health.listen-addr=127.0.0.1:0`, `--log.http-raw-unsafe=false`, `--tracing.enabled=false`, `--mcp.oauth-discovery=disabled`.
8. Nenhuma ação pode modificar `config.toml` do Codex.
9. O smoke final de Chat permanece `verificação manual` até o operador confirmar a ferramenta em uma conversa Chat.

## Critérios de aceitação

- Testes RED anteriormente às implementação.
- `status` sem PID ativo retorna `parado` e não toca rede.
- `plan` não cria processo e não imprime conteúdo da chave.
- `start` sem `--confirm` falha fechado.
- `start` com chave permissiva falha fechado.
- `start` com hash do bundle divergente falha fechado.
- `stop` recusa PID que não pertença ao binário gerenciado/túnel.
- Comando final contém `integrations.ecosystem_mcp`, não `chatgpt_status_mcp`.
- `doctor` continua `verification: installation_only` e nenhuma alegação de ativação no chat é feita sem confirmação humana.

## Validação observada

- RED: importação do runner ausente, seguida de implementação e GREEN com `13 passed`.
- `plan`: plano sanitizado, sem processo, sem rede e sem leitura da chave.
- `start --confirm`: PID `578646`, `readyz=true`, posteriormente `polling_confirmado` com último poll `2026-11-18T05:55:37.058039313Z`.
- Correção de compatibilidade: o health v0.0.21 publica `details.observed_at`; o status passou a aceitar `last_success` ou `observed_at`.
- `runtime.key` permaneceu com modo `0600` e foi passado apenas como referência `file:<caminho>`.
- `~/.codex/config.toml` não foi modificado.
