# R1061 — storage-operator: espaço, upload e exclusão verificada

Implementação local para gerir a raiz autorizada e enviar ao Google Drive com
manifesto, checksum e exclusão somente após verificação remota.

## Entregue

| Componente | Caminho |
|---|---|
| Política de raízes/caminhos | `integrations/storage_operator/policy.py` |
| Manifesto SHA-256 | `integrations/storage_operator/manifest.py` |
| Inventário/`df` | `integrations/storage_operator/inventory.py` |
| Upload/verify/purge | `integrations/storage_operator/drive.py` |
| Aprovação HMAC | `integrations/storage_operator/approvals.py` |
| MCP com 7 ferramentas | `integrations/storage_operator/mcp_server.py` |
| CLI | `integrations/storage_operator/__main__.py` |
| Configuração | `config/storage_operator.json` |
| Testes | `tests/test_r1061_storage_operator.py` |
| Spec | `specs/SPEC-935-R1061-storage-operator.md` |

## Ferramentas

`storage_status` · `storage_report` · `storage_scan` · `drive_plan` ·
`drive_upload` · `drive_verify` · `storage_purge`

`drive_upload` e `storage_purge` exigem aprovação humana de uso único,
vinculada ao **hash do manifesto**. O MCP não emite aprovação.

## Regras de segurança

- Raiz allowlisted: `/mnt/c/Users/marce/Downloads`.
- Sem `..`, caminho absoluto, symlink, dispositivo ou diretório no purge.
- Segredos (`.env`, chaves, `id_rsa`, `*.kdbx`, etc.) são excluídos.
- `.tmp.driveupload` (sincronização do Drive) nunca é enviado nem apagado.
- `.gdoc/.gsheet/.gslides` e `desktop.ini` são mantidos, não enviados.
- `.crdownload/.part/.tmp` não são enviados; podem ser apagados como parciais.
- Upload com `rclone copy --checksum --files-from`, sem `--delete`.
- Verificação com `rclone check --checksum --one-way` antes do purge.
- Purge por `unlink` de cada arquivo do manifesto, com SHA-256 reconferido.
- Manifesto local com nomes de arquivos **não é versionado**; só o resumo.

## Resultado real

| Etapa | Resultado |
|---|---|
| `C:` antes | 97,6% usado · 12.157.075.456 bytes livres |
| Downloads | 50 arquivos · 69.165.522 bytes |
| Upload | **18 arquivos · 13.561.930 bytes** para `gdrive:Downloads_2026-11-04_23-22-00` |
| Verificação | `rclone check --checksum` ok; `verified: true` |
| Exclusão | **20 arquivos · 34.581.756 bytes** (18 enviados + 2 parciais) |
| Restante em Downloads | 10 arquivos: 9 atalhos `.gdoc` + `desktop.ini` |
| Remoto após purge | **18 arquivos** preservados |
| `C:` depois | 97,7% usado · 11.937.157.120 bytes livres |

**O `C:` não melhorou.** Downloads tem só ~34 MB; a exclusão de 34,6 MB foi
compensada por outras gravações do sistema. O problema de espaço está em outro
lugar e precisa de um inventário separado (fora deste escopo).

Evidências: `summary.json`, `upload-result.json`, `purge-result.json`,
`report-after.json`.

## Como operar

```bash
python3 -m integrations.storage_operator status
python3 -m integrations.storage_operator report
python3 -m integrations.storage_operator scan
python3 -m integrations.storage_operator plan

# revisar o manifesto e então:
python3 -m integrations.storage_operator approve \
  --command upload --manifest <manifest.json> --confirm
python3 -m integrations.storage_operator upload \
  --manifest <manifest.json> --approval-token 'v1...'

python3 -m integrations.storage_operator verify --manifest <manifest.json>

python3 -m integrations.storage_operator approve \
  --command purge --manifest <manifest.json> --confirm
python3 -m integrations.storage_operator purge \
  --manifest <manifest.json> --approval-token 'v1...'
```

## Limites

- O Drive foi autorizado via OAuth e o remote `gdrive` está no
  `~/.config/rclone/rclone.conf`; o token não é versionado.
- A saída do `rclone config create` pode conter token; se o terminal for
  compartilhado, revogue o acesso em `myaccount.google.com/permissions` e
  reautorize.
- Dados pessoais foram enviados porque o operador autorizou; a base
  legal/consentimento é responsabilidade do operador.
- rclone 1.60.1 é antigo; validar antes de automações maiores.
- Nenhuma validação externa, publicação ou promessa de recuperação do `C:`.
