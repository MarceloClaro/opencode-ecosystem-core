# R1061 — relatório do storage-operator

**Status:** fluxo completo executado em `C:\Users\marce\Downloads`; upload
verificado e exclusão permanente realizada. Nada publicado, sem validação
externa.

## Resultado

| Etapa | Resultado |
|---|---|
| `C:` antes | 97,6% usado; 12.157.075.456 bytes livres |
| Downloads | 50 arquivos; 69.165.522 bytes |
| Manifesto | 30 entradas; 18 upload; 2 parciais; 9 `.gdoc`; 1 `desktop.ini` |
| Upload | 18 arquivos; 13.561.930 bytes; `gdrive:Downloads_2026-11-04_23-22-00` |
| Verificação | `rclone check --checksum --one-way` ok |
| Purge | 20 arquivos; 34.581.756 bytes |
| Restante | 9 `.gdoc` + `desktop.ini` (10 arquivos) |
| Remoto após purge | 18 arquivos |
| `C:` depois | 97,7% usado; 11.937.157.120 bytes livres |
| Testes | **15 passed** |

## O que foi protegido

- `.tmp.driveupload` foi excluído do manifesto: apagar essa pasta poderia
  interferir na sincronização do Google Drive.
- `.gdoc/.gsheet/.gslides` e `desktop.ini` foram mantidos, não enviados nem
  apagados.
- Segredos (`.env`, chaves, `id_rsa`, `*.kdbx`, etc.) são excluídos por padrão.
- O purge só ocorreu após `drive_verify` retornar `ok` e com token de uso único
  vinculado ao hash do manifesto.
- O manifesto local com nomes de arquivos pessoais **não foi versionado**;
  apenas o resumo agregado foi incluído.

## Limite principal

**O `C:` não foi resolvido.** Downloads tem apenas ~34 MB; a exclusão de
34,6 MB foi compensada por outras gravações do sistema, e o disco continuou em
~98%. O próximo passo é um inventário somente leitura dos grandes consumidores
do `C:` (fora de Downloads), sem apagar nada.

## Segurança

- O remote `gdrive` está em `~/.config/rclone/rclone.conf`, fora do repositório.
- A saída de `rclone config create` pode conter token; se o terminal for
  compartilhado, revogue o acesso em `myaccount.google.com/permissions` e
  reautorize.
- Dados pessoais foram enviados porque o operador autorizou; a base
  legal/consentimento é responsabilidade do operador.
- rclone 1.60.1 é antigo; validar antes de automações maiores.

## Próximo passo

1. Inventariar `C:` por diretório de topo e maiores arquivos, somente leitura.
2. Identificar caches/instaladores/duplicados com segurança.
3. Só então propor um novo manifesto com aprovação por lote.
