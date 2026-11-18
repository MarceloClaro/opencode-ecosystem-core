# SPEC-935-R1220 — Persistência Windows do túnel MCP completo

- **Status**: concluído; GREEN 23 testes (R1218+R1220), `.cmd` e dois atalhos criados, túnel permanece `polling_confirmado`.
- **Data**: 2026-11-18
- **Origem**: operador respondeu `faça` após oferta de criar atalho/serviço persistente para o túnel MCP completo.
- **Escopo**: tornar o runtime R1218 reiniciável e persistente no Windows por atalho de desktop + entrada de Startup, usando apenas o runner gerenciado do Core.

## Problema

O runtime R1218 está ativo e com `polling_confirmado`, porém depende de comando WSL manual. O atalho existente (`00-ATIVAR.cmd`) ainda ativa apenas a fachada `chatgpt_status_mcp`, que expõe uma única ferramenta. É necessário um caminho idempotente de ativação do MCP completo sem mexer no cliente ChatGPT, no pacote `tunnel-client`, na configuração do Codex ou em credenciais.

## Decisão

Adicionar ao runner `integrations/chatgpt_tunnel_full_mcp.py` a ação `ensure --confirm`, idempotente, e gerar dois atalhos Windows apontando para um `.cmd` que chama essa ação via WSL:

- Desktop: `C:\Users\marce\OneDrive\Área de Trabalho\OpenCode Ecosystem Tunnel - MCP Completo (WSL).lnk`
- Startup: `C:\Users\marce\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\OpenCode Ecosystem Tunnel - MCP Completo (WSL).lnk`
- Launcher: `C:\Users\marce\AppData\Local\OpenCodeEcosystemCore\Tunnel-v0.0.21\00-ATIVAR-MCP-COMPLETO.cmd`

## Não-objetivos

- Não alterar `00-ATIVAR.cmd` existente, o atalho antigo, `launcher.py` ou `app.asar`.
- Não alterar `~/.codex/config.toml`, auth, modelos, provedores ou permissões.
- Não criar Task Scheduler, serviço Windows ou daemon systemd.
- Não ler, imprimir ou copiar `runtime.key`; o `.cmd` apenas referencia o runner, que usa `file:<caminho>`.
- Não alegar que o Chat exibe ferramentas; verificação no chat continua manual.

## Contrato

1. `ensure --confirm` deve:
   - retornar `2` sem `--confirm`, sem efeito;
   - com `polling_confirmado`, não iniciar novo processo e retornar `0`;
   - com `aguardando_polling`/`aguardando_listener`, não duplicar processo e retornar status atual;
   - com `parado`, chamar `start` com o mesmo conjunto de validações;
   - recusar PID registrado que não pertença ao túnel gerenciado.
2. `render_launcher_cmd()` deve produzir script `.cmd` com `wsl.exe --distribution Ubuntu --cd <raiz> --exec <.venv python> -B -m integrations.chatgpt_tunnel_full_mcp ensure --confirm`.
3. `render_shortcut_setup_ps1()` deve produzir script PowerShell que cria/atualiza somente os dois atalhos declarados, com `WorkingDirectory` na raiz do túnel e janela minimizada no Startup.
4. A ação `install-windows` deve ser `dry-run` por padrão; efeitos reais exigem `--confirm`.
5. Nenhum artefato gerado pode conter conteúdo de chave, token, cookie ou caminho de segredo além da referência já existente ao arquivo `0600`.
6. O usuário continua responsável por confirmar no chat que as ferramentas apareceram.

## Critérios de aceitação

- RED antes da implementação.
- `ensure` sem confirm: `2`, sem `Popen`.
- `ensure` com túnel ativo: `0`, sem `Popen`.
- `ensure` com túnel parado e confirm: inicia uma vez.
- Script `.cmd` contém `ensure --confirm` e não contém `runtime.key`.
- Script PowerShell cria exatamente os dois atalhos esperados e não menciona `config.toml`, `app.asar`, `auth` ou `chatgpt_status_mcp`.
- Após execução, os dois atalhos existem no Windows e apontam para o `.cmd` gerado.
- Estado atual do túnel permanece `polling_confirmado`.
- `doctor` permanece `installation_only`; nenhuma alegação de ativação no chat sem confirmação humana.

## Evidência R1220 (2026-11-18)

- RED inicial: `.FFFFFFFF` (`1 passed`, `8 failed`) com ações/helpers ausentes.
- GREEN final: `23 passed` para `tests/test_r1218_chatgpt_tunnel_full_mcp.py` + `tests/test_r1220_chatgpt_tunnel_persistente.py`.
- Correções durante GREEN:
  - `WorkingDirectory` dos atalhos passou a derivar da string Windows, preservando `C:\Users\marce\AppData\Local\OpenCodeEcosystemCore\Tunnel-v0.0.21`.
  - Saída do PowerShell passou a ser decodificada com `errors="replace"`, evitando `UnicodeDecodeError` em cp1252/cp850.
  - Script enviado por `-EncodedCommand` (UTF-16LE/base64), preservando `Área de Trabalho` sem depender de encoding de stdin.
- `install-windows --confirm` executado:
  - `launcher_existe=true`, `desktop_existe=true`, `startup_existe=true`, `powershell_exit=0`.
  - Tamanhos observados: `.cmd` 526 bytes; atalho desktop 1487 bytes; atalho Startup 1495 bytes.
- `ensure --confirm` reexecutado após a instalação: `tunel=polling_confirmado`, `mcp=integrations.ecosystem_mcp`, `pid=578646`, sem duplicação.
- Registro de evento: `atalhos_windows_instalados` em `/home/marceloclaro/.local/state/opencode-core-tunnel-full/eventos.jsonl`.
- Não alterados: `00-ATIVAR.cmd`, atalho antigo, `launcher.py`, `app.asar`, `~/.codex/config.toml`, auth/modelos/permissões.
