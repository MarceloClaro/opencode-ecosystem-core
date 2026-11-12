# Upstream: `opencode_console` 403 e elegibilidade MCP

**Issue:** [anomalyco/opencode#59806](https://github.com/anomalyco/opencode/issues/59806)
**Estado observado:** aberto; reaberto em 2026-11-03.
**Versão testada:** OpenCode `2.2.7` (Linux, serviço/CLI), workspace com papel
`owner`.
**Spec local:** `specs/SPEC-935-R1110-opencode-console-proxy.md`.

## Sintoma

O fluxo OAuth do MCP conclui com HTTP 200 e refresh token, mas o primeiro POST
autenticado em `https://opencode.ai/console/mcp` recebe:

```json
{"error":"forbidden","message":"The Console MCP is not enabled for this workspace."}
```

O erro sugere que o workspace não habilitou o Console MCP. Neste caso, o mesmo
workspace e o mesmo membro **são elegíveis** quando o token de membro da
integração `opencode` é usado. O problema está no token emitido para o MCP, não
na ausência de habilitação do workspace.

## Evidência nova (diagnóstico reproduzível)

O Console expõe `GET https://opencode.ai/console/api/mcp/eligibility`. O script
local `scripts/opencode_console_eligibility.py` compara as duas credenciais sem
imprimir tokens, e-mail ou IDs:

```text
member    eligible=True  status=200 role=owner workspace=Default permissions=11
mcp_oauth eligible=False status=200 role=None workspace=None permissions=0
```

O mesmo padrão aparece no endpoint MCP:

| Credencial | `POST /console/mcp` (initialize) | `/api/mcp/eligibility` |
|---|---|---|
| Token de membro da integração `opencode` | **200**, `serverInfo.name=opencode_console` | `eligible=true`, caller com papel `owner` |
| Token OAuth emitido para o MCP | **403** “not enabled for this workspace” | `eligible=false`, sem caller/papel/workspace |

Acrescentar `x-opencode-org-id` ao request do token OAuth **não altera** o
resultado. O token não é expirado: a troca OAuth retornou 200, refresh token
presente, `expiresIn=2591999` (~30 dias), e a credencial estava ativa no banco.

## Interpretação

O token OAuth do MCP é aceito pelo authorization server, mas não é reconhecido
como um caller elegível para o workspace no endpoint de elegibilidade. O
resource server então devolve 403 com uma mensagem genérica de “workspace não
habilitado”, que induz o operador a procurar uma configuração de workspace
quando a falha é de vínculo/escopo do token.

O token de membro da integração `opencode` carrega o contexto do workspace
(`Default`) e é aceito tanto pela elegibilidade quanto pelo endpoint MCP. Isso
separa “workspace sem MCP” de “token MCP sem vínculo de workspace”.

## Correções propostas

### Servidor (preferencial)

1. Fazer o token OAuth do MCP herdar/derivar o caller e o workspace do membro
   que autorizou o fluxo, como já ocorre com o token de membro.
2. Se o token não puder ser vinculado, retornar um erro específico — por
   exemplo `401 token_not_workspace_bound` — em vez de
   `403 The Console MCP is not enabled for this workspace`.
3. Incluir em `/api/mcp/eligibility` um campo `reason`/`caller` explícito para
   tokens OAuth, distinguindo `workspace_mcp_disabled` de
   `token_not_workspace_bound`.

### Cliente (mitigação de UX)

1. Antes de conectar, chamar `/api/mcp/eligibility` com o token OAuth e
   apresentar um erro acionável quando `eligible=false`, em vez de tentar
   reconectar em loop.
2. Se o fluxo OAuth permitir escolher workspace, garantir que a seleção seja
   explícita e que o token resultante seja vinculado ao workspace escolhido.
3. Não silenciar o 403: mostrar o estado `failed`/`needs_auth` com a mensagem
   do servidor e um link para a página de MCP do Console.

## Reprodução

```bash
cd /home/marceloclaro/opencode-ecosystem-core
.venv/bin/python scripts/opencode_console_eligibility.py
```

O script lê as credenciais ativas do banco local do OpenCode, consulta
`/api/mcp/eligibility` com cada uma e imprime apenas `eligible`, status, papel,
nome do workspace e contagem de permissões. Tokens, e-mail e IDs são redigidos.

## Workaround local (não é correção upstream)

O proxy `scripts/opencode_console_proxy.py` (SPEC-935-R1110) escuta em
`127.0.0.1:8765`, lê o token de membro a cada requisição e injeta o
`Authorization` no upstream. Ele mantém as 11 ferramentas do Console MCP sem
gravar segredo no `opencode.json`, mas não corrige o vínculo do token OAuth.

## Limites

- Não há acesso aos logs internos do resource server; a claim exata que falta
  no token OAuth não foi inspecionada.
- O endpoint `/api/mcp/eligibility` é interno e pode mudar sem aviso.
- A evidência é de um workspace/membro; não se afirma generalidade para todos
  os planos ou regiões.
- Nenhuma correção upstream foi merged; a issue permanece aberta.
- O workaround local depende da validade do token de membro e do processo do
  proxy.
