# SPEC-935-R1061 — storage-operator com manifesto, checksum e exclusão verificada

**Status:** implementação autorizada; OAuth do Drive pendente de consentimento.
**Objetivo:** gerir espaço em raízes allowlisted e enviar arquivos ao Google
Drive com manifesto, checksum, verificação remota e exclusão permanente apenas
do que foi verificado.

## 1. Escopo

- Raiz autorizada inicial: `/mnt/c/Users/marce/Downloads`
  (`C:\Users\marce\Downloads`).
- Relatório de espaço e inventário somente leitura.
- Manifesto com caminho relativo, tamanho, mtime, SHA-256, sensibilidade e
  decisão de inclusão/exclusão.
- Upload via `rclone` para pasta remota
  `<nome-da-raiz>_<AAAA-MM-DD_HH-MM-SS>`.
- Verificação remota por `rclone check`/`lsjson` antes de permitir exclusão.
- Exclusão permanente somente por manifesto aprovado e verificado; nunca por
  glob, diretório recursivo ou “limpeza automática”.

**Fora de escopo:** apagar pastas de sistema, limpar `C:\Windows`, operar
Windows apps, instalar/atualizar rclone, publicar, ou excluir arquivos que não
estejam no manifesto verificado.

## 2. Arquitetura

```
storage_scan (read-only) → drive_plan (manifesto + SHA-256)
      → approve upload (HMAC do manifesto) → rclone copy
      → rclone check/lsjson → verify receipt
      → approve purge (HMAC do manifesto verificado) → unlink por arquivo
```

O operador não aceita `rm -rf`, não segue symlink, não sai da raiz e não apaga
diretório. O binário `rclone` é chamado com argv em lista e `shell=False`.

## 3. Contrato das ferramentas

| Ferramenta | Efeito | Gate |
|---|---|---|
| `storage_report` | `df` e totais da raiz | somente leitura |
| `storage_scan` | inventário por arquivo/diretório | somente leitura; raiz allowlisted |
| `drive_plan` | cria manifesto e pasta remota planejada | não envia; não apaga |
| `drive_upload` | `rclone copy` do manifesto | aprovação vinculada ao hash do manifesto |
| `drive_verify` | `rclone check` + `lsjson` | somente leitura remota |
| `storage_purge` | `unlink` dos arquivos do manifesto | manifesto verificado + aprovação |

## 4. Política de caminhos

- `realpath` deve permanecer sob a raiz allowlisted.
- Rejeitar `..`, caminho absoluto, symlink, dispositivo, FIFO, socket e
  diretório no purge.
- Rejeitar nomes que casem com padrões de segredo: `.env`, `*.key`, `*.pem`,
  `id_rsa*`, `*.kdbx`, `*.pfx`, `*.p12`, `credentials*`, `token*`.
- Arquivos `.crdownload`, `.part`, `.tmp` entram como candidatos a limpeza,
  mas **não** são enviados.
- Dados pessoais podem ser enviados porque o operador autorizou; o manifesto
  marca `sensitive: true` para PDFs, imagens e documentos. O log não lê
  conteúdo, apenas nome/tamanho/hash.

## 5. Manifesto

```json
{
  "schema_version": "1.0",
  "root": "/mnt/c/Users/marce/Downloads",
  "remote": "gdrive",
  "remote_path": "Downloads_2026-11-05_23-30-00",
  "created_at": "...",
  "files": [
    {"relpath": "x.pdf", "size": 123, "mtime": 0, "sha256": "...",
     "sensitive": true, "upload": true, "delete": true, "reason": null}
  ],
  "excluded": [],
  "totals": {"files": 1, "bytes": 123},
  "manifest_sha256": "..."
}
```

`manifest_sha256` cobre o JSON canônico sem o próprio campo. A aprovação de
upload/purge usa esse hash.

## 6. Aprovação e exclusão

- Token HMAC local, preso ao host, com operador declarado, TTL ≤ 300 s e nonce
  de uso único.
- `drive_upload` exige token de upload; `storage_purge` exige token de purge.
- `storage_purge` recusa se o manifesto não tiver verificação remota `ok`,
  se o hash de algum arquivo local tiver mudado ou se o caminho não for regular.
- A exclusão é **um `unlink` por arquivo do manifesto**, com recibo por arquivo.
- Falha em qualquer arquivo interrompe o lote e preserva os demais.

## 7. Aceitação (TDD)

1. path traversal, symlink e raiz fora da allowlist são negados;
2. padrões de segredo são excluídos do upload;
3. manifesto é determinístico e o hash muda se um arquivo mudar;
4. upload usa `--checksum`, `--files-from`, sem `--delete` e `shell=False`;
5. purge sem aprovação, com hash errado, manifesto não verificado ou arquivo
   alterado é negado;
6. purge válido remove somente os arquivos do manifesto;
7. token de upload não serve para purge e vice-versa;
8. nenhuma senha/token aparece em log ou manifesto.

## 8. Piloto

1. `storage_report` e `storage_scan` reais em Downloads.
2. `drive_plan` real; revisar manifesto (34 MB, 16 PDFs, 9 GDocs, 2 parciais).
3. OAuth único do rclone para o Drive.
4. `drive_upload` para `Downloads_<data_hora>`, com checksum.
5. `drive_verify`; só então `storage_purge` dos arquivos verificados.
6. Registrar hashes, tamanho, pasta remota e limites; não publicar.

## 9. Riscos e limites

- Exclusão permanente é irreversível; o manifesto e a verificação são a única
  barreira.
- Dados pessoais exigem base legal/consentimento; o operador declarou
  autorização, mas a responsabilidade permanece dele.
- `C:` está em 98%; Downloads (34 MB) não resolve o problema. O relatório deve
  apontar os grandes consumidores sem apagá-los.
- rclone 1.60 é antigo; verificar compatibilidade OAuth/Drive antes do upload.
- Nenhuma validação externa, publicação ou promessa de recuperação de espaço.

## 10. Resultado real (2026-11-05)

| Item | Resultado |
|---|---|
| `C:` antes | 97,6% usado; 12.157.075.456 bytes livres |
| Downloads | 50 arquivos; 69.165.522 bytes |
| Manifesto | 30 entradas: 18 upload, 2 parciais, 9 atalhos `.gdoc`, 1 `desktop.ini` |
| Upload | 18 arquivos; 13.561.930 bytes; `gdrive:Downloads_2026-11-04_23-22-00` |
| Verificação | `rclone check --checksum --one-way` ok |
| Purge | 20 arquivos; 34.581.756 bytes |
| Restante | 9 `.gdoc` + `desktop.ini` (10 arquivos) |
| Remoto após purge | 18 arquivos |
| `C:` depois | 97,7% usado; 11.937.157.120 bytes livres |
| Testes | **15 passed** |

**Conclusão:** o fluxo de upload + verificação + exclusão funcionou, mas
Downloads (34 MB) não é o gargalo do `C:`; a exclusão não aumentou o espaço
livre de forma perceptível. É necessário um inventário separado dos grandes
consumidores do `C:` antes de qualquer nova limpeza.

O manifesto local contém nomes de arquivos pessoais e **não foi versionado**;
apenas o resumo agregado foi incluído. O token OAuth não está no repositório.
Nada foi publicado e não há validação externa.
