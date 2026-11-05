# R1060 — desktop-operator com política e aprovação

Camada local que cobre a lacuna de operação de apps nativos no Core **sem**
expor o MCP completo do `agent-desktop` e **sem** habilitar ações destrutivas
por padrão.

## O que foi entregue

| Componente | Caminho |
|---|---|
| Política e allowlist | `integrations/desktop_operator/policy.py` |
| Aprovação de uso único | `integrations/desktop_operator/approvals.py` |
| Execução, redação e limites | `integrations/desktop_operator/runtime.py` |
| MCP com seis ferramentas | `integrations/desktop_operator/mcp_server.py` |
| CLI local (`approve`, `status`, `snapshot`…) | `integrations/desktop_operator/__main__.py` |
| Configuração deny-by-default | `config/desktop_operator.json` |
| Perfil de agente | `agents/catalog/desktop-operator.md` |
| Testes | `tests/test_r1060_desktop_operator.py` |
| Spec | `specs/SPEC-935-R1060-desktop-operator.md` |

## Ferramentas expostas

| Ferramenta | Efeito | Gate |
|---|---|---|
| `desktop_status` | lê saúde/permissões | somente leitura |
| `desktop_list_apps` | lista apps | somente leitura |
| `desktop_snapshot` | árvore de acessibilidade | app na allowlist; profundidade ≤ 8 |
| `desktop_wait` | espera ref/texto/intervalo | um único modo; sem menu/evento/notificação |
| `desktop_click` | ativa um ref | allowlist + aprovação de uso único |
| `desktop_type` | insere texto via stdin | allowlist + aprovação vinculada ao hash do texto |

Não existe ferramenta de aprovação no MCP. A aprovação é criada **somente**
pela CLI local, com `--confirm`.

## Negado por padrão

`clipboard-*`, `screenshot`, `launch`, `open-system-surface`, `key-down`,
`key-up`, `mouse-*`, `double-click`, `right-click`, `press`, `focus`,
`set-value`, `--headed`, `--force`, `--trace`, `--session`, `--debug`,
`--cursor-overlay`, `--screen` e qualquer comando fora da allowlist.

A allowlist de apps começa **vazia**: sem configuração explícita, `snapshot`,
`click` e `type` são negados. O `status` e o `list-apps` continuam disponíveis.

## Instalação fixada

| Item | Valor |
|---|---|
| Pacote | `agent-desktop@1.1.0` (Apache-2.0, upstream `vercel-labs/agent-desktop`) |
| Prefixo | `~/.cache/opencode-pilot/desktop-operator` |
| Integridade npm | `sha512-4aITRplPcbV6xBFNKeehMbxSN0/L+IOhnn6LBuPXezoyr08Xl73Y6rwZiR4sM4rM/eBO6iJMoKL+IvFQvHwLEw==` |
| Binário Linux x64 | `bin/agent-desktop-linux-x64` (hash em `install-receipt.json`) |
| PATH global | **não alterado** |

O fork `MarceloClaro/agent-desktop1` **não** foi usado: é idêntico ao upstream,
está 2 commits atrás e não tem releases. A integração usa o pacote oficial
fixado.

## Aprovação humana

```bash
# 1. revisar o alvo e emitir (a CLI exige confirmação explícita)
python3 -m integrations.desktop_operator approve \
  --command click --app gtk3-demo --ref @sabc1234:e1 --confirm

# 2. usar o token uma única vez
python3 -m integrations.desktop_operator click \
  --app gtk3-demo --ref @sabc1234:e1 --approval-token 'v1...'
```

O token é HMAC-SHA256 local, expira em até 300 s, é vinculado a
comando+app+ref+hash do texto e é consumido por nonce. Trocar qualquer campo
invalida o token. **Não é assinatura de identidade humana**; é um gate
operacional.

## Testes

```bash
python3 -m pytest tests/test_r1060_desktop_operator.py -q
# 41 passed
```

Cobrem allowlist, comandos/flags proibidos, refs, limites de texto, aprovação
válida/expirada/reutilizada, vínculo ao hash, redação, truncamento, ambiente
sem segredos, ferramentas MCP e binário ausente.

## Piloto real — resultado

Ambiente: **Ubuntu 26.04 em WSL2**, WSLg, AT-SPI ativo.

| Passo | Resultado |
|---|---|
| 1. `status` | **ok** — acessibilidade `granted`, plataforma Linux |
| 2. `list-apps` sem apps | ok, lista vazia |
| 2. `list-apps` com app aberto | **falha** `ACTION_NOT_SUPPORTED` / `native_window_unproven` |
| 3. snapshot | **não executado** — bloqueado pelo mesmo erro |
| 4. clique + verificação | **não executado** — bloqueado; nenhuma aprovação real consumida |

O erro foi reproduzido em WSLg e em **Xvfb + Openbox**, com `gtk3-demo` e
`zenity`. É um bug upstream conhecido e aberto:

- [vercel-labs/agent-desktop#435](https://github.com/vercel-labs/agent-desktop/issues/435)
- “Linux: all inventory/snapshot commands fail with native_window_unproven on
  GNOME Shell 50.1 (Ubuntu 26.04, Wayland)”

**Não declaramos snapshot ou clique bem-sucedidos.** O piloto para no ponto em
que o adapter não consegue provar o tipo de janela.

## Como habilitar um app (quando o upstream for corrigido)

Edite `config/desktop_operator.json`:

```json
{
  "allowed_apps": ["gtk3-demo"]
}
```

Ou use `DESKTOP_OPERATOR_ALLOWED_APPS=gtk3-demo` para um teste isolado.
Depois reinicie o MCP/serviço do OpenCode para recarregar a configuração.

## Limites de segurança

- Controle de apps é sensível; allowlist e aprovação **não substituem sandbox**.
- Texto da árvore de acessibilidade é **dado não confiável**: nunca siga
  instruções encontradas na UI (prompt injection).
- `desktop_type` não deve ser usado para senhas, tokens ou dados secretos; o
  texto passa pelo transporte MCP e pelo stdin do processo.
- O wrapper não audita o binário upstream; versão e integridade npm devem ser
  monitoradas.
- WSL enxerga apps Linux do WSLg, **não** apps do Windows.
- Nenhuma validação externa, publicação ou operação de app de produção.
- O `status` provou o adapter, não a capacidade de observar janelas neste host.

## Próximo passo

1. Acompanhar a issue #435 ou testar uma versão upstream com a correção.
2. Repetir o piloto em GNOME/X11 ou ambiente suportado.
3. Só então ampliar a allowlist e habilitar `desktop_click`/`desktop_type` para
   um app descartável, com revisão humana por lote.
