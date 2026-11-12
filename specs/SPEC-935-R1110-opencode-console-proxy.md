# SPEC-935-R1110 — Proxy local seguro para o `opencode_console`

**Orquestrador:** marceloclaro · **Estado:** implementado e testado localmente;
a correção definitiva continua sendo upstream (`anomalyco/opencode#59806`).

## Objetivo e limites

Manter as ferramentas do MCP `opencode_console` disponíveis sem o HTTP 403
causado pelo token OAuth emitido pelo fluxo MCP, sem gravar segredo no
`opencode.json` e sem depender de override em memória que se perde a cada
`config.updated`.

O proxy escuta somente em loopback, lê o token de membro da integração
`opencode` no banco local do OpenCode a cada requisição, injeta o header
`Authorization: Bearer ...` e encaminha o transporte Streamable HTTP para
`https://opencode.ai/console/mcp`. O token não é persistido nem registrado em
log pelo proxy. O proxy é uma ponte local, não uma fronteira de segurança do
sistema operacional e não corrige o bug upstream.

## Contrato de segurança

1. O listener padrão é `127.0.0.1:8765`. Cliente fora de loopback e header
   `Host` que não seja `127.0.0.1`, `localhost` ou `[::1]` são recusados com
   HTTP 403.
2. O token é lido de `~/.local/share/opencode/opencode.db`, tabela
   `credential`, `integration_id='opencode'`, `active=1`, registro mais
   recente. A leitura é somente leitura (`mode=ro`) e não altera o banco.
3. Token ausente, inválido ou com expiração em menos de 60 s produz HTTP 401
   com mensagem para executar `/connect`; nenhuma chamada ao upstream é feita.
4. O proxy encaminha método, corpo e headers relevantes (`Content-Type`,
   `Accept`, `Mcp-Session-Id`, `MCP-Protocol-Version`, `Last-Event-ID`),
   substitui o `Authorization` e usa `Accept-Encoding: identity`. Respostas
   JSON e SSE são repassadas em streaming; headers hop-by-hop não são
   repassados.
5. Erros HTTP do upstream são repassados com status e corpo. Falha de rede vira
   HTTP 502; timeout vira HTTP 504. O proxy não inventa sucesso.
6. O `opencode.json` aponta para `http://127.0.0.1:8765/mcp` com
   `"oauth": false`; nenhum token, refresh token ou chave é escrito no arquivo.
7. O token nunca aparece em resposta, log ou mensagem de erro. O `--check`
   imprime apenas status, nome do servidor e trecho sanitizado de erro.
8. O proxy relê o banco a cada requisição: depois de `/connect`, o novo token é
   usado sem reiniciar o proxy. Se o token expirar, o operador precisa renovar
   a credencial; o proxy não faz refresh próprio.

## Aceites testáveis (RED → GREEN → REFACTOR)

- **R1110-1:** `read_member_token` seleciona a credencial ativa mais recente,
  aceita token válido e rejeita credencial ausente, JSON inválido, token vazio
  e expiração próxima.
- **R1110-2:** POST no proxy injeta `Authorization: Bearer <token>` no upstream
  e repassa corpo SSE/JSON sem alterar o conteúdo.
- **R1110-3:** credencial ausente ou expirada retorna 401 e não chama o
  upstream.
- **R1110-4:** erro HTTP do upstream (ex.: 403) é repassado com status e corpo.
- **R1110-5:** o token de teste não aparece no corpo da resposta nem no log
  capturado.
- **R1110-6:** `opencode mcp list` mostra `opencode_console connected` com a
  config do proxy; `get_context` confirma workspace e papel. Verificação
  manual no host, não repetível em CI sem a credencial real.

## Estratégia de migração

1. Subir o proxy em loopback e validar com `--check`.
2. Trocar a entrada `opencode_console` de `disabled: true` para
   `url: http://127.0.0.1:8765/mcp` e `oauth: false`.
3. Recarregar a config e conferir `opencode mcp list`.
4. Instalar a unit systemd de usuário para reinício automático.
5. Preservar o fallback `disabled: true` documentado; se o proxy ou o token
   falharem, o servidor pode ser desativado sem editar segredo.

## Evidência observada (12/11/2026)

- Antes do proxy: token OAuth do MCP → HTTP 403 “The Console MCP is not enabled
  for this workspace”; token de membro da integração `opencode` → HTTP 200 com
  `serverInfo.name = opencode_console`.
- O override em memória conectava 11 ferramentas, mas era perdido em
  `config.updated` (09:10, 13:27 e 14:54 UTC).
- O proxy usa a mesma credencial de membro que respondeu 200, sem gravar o
  token no config. A disponibilidade contínua depende do processo do proxy e da
  validade da credencial; não há garantia de disponibilidade futura do upstream.
- Após a implantação: `--check` → HTTP 200 (`server=opencode_console`);
  `mcp list` → `opencode_console connected`; `get_context` → workspace
  `Default`, role `owner`; 13 testes R1110 passaram. O proxy foi reiniciado e a
  config foi recarregada sem perder a conexão.

## Evidência upstream (issue #59806)

- `GET https://opencode.ai/console/api/mcp/eligibility` com o token de membro
  da integração `opencode`: HTTP 200, `eligible=true`, caller `owner` no
  workspace `Default`.
- O mesmo endpoint com o token OAuth emitido para o MCP: HTTP 200,
  `eligible=false`, sem caller/papel/workspace.
- `POST https://opencode.ai/console/mcp` com o token de membro: HTTP 200 e
  `serverInfo.name=opencode_console`; com o token OAuth: HTTP 403 “not enabled
  for this workspace”; com o token OAuth + `x-org-id`: HTTP 403 “The console
  refused access to the workspace.” O header correto é `x-org-id`, não
  `x-opencode-org-id`.
- `packages/core/src/console-access.ts` mostra que o token de membro envia
  `x-org-id` a partir de `metadata.orgID`; a credencial OAuth do MCP não possui
  `orgID`. O header melhora o roteamento, mas o servidor ainda recusa o token
  por falta de autorização de workspace.
- Diagnóstico reproduzível: `scripts/opencode_console_eligibility.py` (5 testes
  herméticos; não imprime tokens, e-mail ou IDs).
- Dossiê com hipótese, correções propostas e limites:
  `docs/upstream/opencode-59806-mcp-eligibility.md`.
- A issue permanece aberta; nenhuma correção upstream foi merged. A evidência
  separa “workspace sem MCP” de “token MCP sem vínculo de workspace”.
