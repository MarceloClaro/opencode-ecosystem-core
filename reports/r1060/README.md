# R1060 — relatório do desktop-operator

**Status:** implementação concluída e testada; piloto real **parcialmente
bloqueado** por bug upstream. Não publicado, sem validação externa.

## Entregue

- MCP local `desktop-operator` com exatamente seis ferramentas.
- Allowlist de apps fechada por padrão; `snapshot/click/type` exigem app
  autorizado.
- Aprovação humana de uso único para `click/type`, HMAC local, TTL ≤ 300 s,
  vínculo a comando+app+ref+hash do texto.
- Negação explícita de clipboard, screenshot, launch, mouse/teclado físico,
  `--headed`, `--force`, `--trace`, sessões e debug.
- Redação de e-mail, CPF, CNPJ, cartão, bearer, hex/base64 longos e chaves
  sensíveis; limite de 256 KiB com JSON válido.
- Ambiente de subprocesso reduzido, sem segredos do processo pai.
- Perfil `desktop-operator` registrado no catálogo; MCP registrado no
  `opencode.json`.
- 40 testes locais com binário falso; nenhum teste usa o app real.

## Evidência

| Evidência | Resultado |
|---|---|
| `pytest tests/test_r1060_desktop_operator.py -q` | **41 passed** |
| `desktop_status` via MCP | ok, acessibilidade `granted` |
| `desktop_list_apps` sem apps | ok, lista vazia |
| `desktop_list_apps` com `gtk3-demo` | `ACTION_NOT_SUPPORTED` / `native_window_unproven` |
| `desktop_snapshot` com app fora da allowlist | negado (`app_not_allowed`) |
| `desktop_snapshot` com app real | **não executado** — bloqueio upstream |
| `desktop_click` real | **não executado** — bloqueio upstream |
| Aprovação real consumida | nenhuma |

## Bug upstream

`vercel-labs/agent-desktop#435` (aberto em 2026-11-01): em Ubuntu 26.04 /
GNOME Shell 50.1 / Wayland, todos os comandos de inventário e snapshot falham
com `native_window_unproven`. O mesmo erro foi reproduzido neste host em
WSLg e em Xvfb+Openbox, com `gtk3-demo` e `zenity`. `status` continua saudável,
o que mascara a falha se apenas o status for testado.

## Limitações

- O wrapper não corrige o adapter; a falha é do binário upstream.
- A aprovação local não é assinatura criptográfica de identidade humana.
- Prompt injection via texto de interface permanece possível; snapshots são
  dados, não instruções.
- Nenhum app de produção, credencial, e-mail ou terminal foi operado.
- Não há validação perceptual, jurídica ou de segurança ofensiva.
- O `opencode.json` foi editado de forma conservadora; regenerações futuras do
  gerador podem remover entradas federadas inativas — comportamento
  pré-existente, não introduzido por este ciclo.

## Próximo passo

Aguardar correção upstream ou testar em ambiente suportado. Só então executar
snapshot + uma ação semântica + novo snapshot, com aprovação humana e app
descartável.
