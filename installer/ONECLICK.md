# Instalador one-click — bibliotecas, CLIs e ambiente

Este é o caminho de conveniência. O instalador **não** baixa mídia, não
publica, não autentica e não embute chaves. O padrão é diagnóstico.

```bash
./install.sh --check                 # não altera nada
./install.sh --check --json          # inventário legível por máquina
./install.sh --apply --yes           # instala apenas npm/pip/uv/venv
./install.sh --apply --yes --group media
./install.sh --apply --yes --only codex,nlm,remotion
```

`--apply` sem `--yes` é recusado. `apt`, `sudo` e scripts oficiais
(`curl ... | bash`) **nunca** são executados automaticamente; o instalador
imprime o comando revisável. Isso evita transformar um clique em execução
cega de bytes de rede.

## O que é instalado automaticamente

| Grupo | Itens |
|---|---|
| `base` | Python venv + `requirements.txt`, npm do `.opencode` quando aplicável |
| `core-cli` | `opencode`, `claude`, `gemini` (npm) |
| `optional` | `codex`, `reasonix` (npm); `agy`, `goose`, `plandex` ficam manuais |
| `media` | `ollama` manual; `remotion` já scaffoldado; `ffmpeg`, `tesseract` via apt |
| `science` | `colab`, `kaggle`, `nlm` (uv/pip); `minizinc` via apt |

## Um clique no desktop

Há dois lançadores de exemplo:

- `installer/INSTALAR-TUDO.desktop` — abre o terminal no diagnóstico;
- `installer/APLICAR-INSTALACAO.desktop` — pede a palavra `APLICAR` antes de
  rodar `--apply --yes`.

Eles contêm o caminho absoluto
`/home/marceloclaro/opencode-ecosystem-core`; se o checkout mudar, edite
`Exec=` e `Path=`. Em ambientes sem área de trabalho, use o terminal.

## Bibliotecas e repositórios

- Bibliotecas Python: `.venv` + `requirements.txt` (grupo `base`).
- Bibliotecas Node do OpenCode: `npm install --ignore-scripts` em `.opencode`
  quando `package.json` existir; o instalador não baixa scripts de ciclo de vida.
- Repositórios externos: não são clonados silenciosamente. Use um diretório
  separado e confira licença/commit:
  ```bash
  git clone --depth 1 <URL> external/<nome>
  ```
  O catálogo de referência está em `reports/r1043/toolchain.json` e
  `docs/VIDEO_EDITOR_TOOLCHAIN_R1043.md`.

## Backup pesado (fora do Git)

O Git não recebe mídia, modelos nem a biblioteca local. Para copiar esses
artefatos para um disco externo:

```bash
./installer/oneclick/backup-heavy.sh /mnt/backup/opencode --dry-run
./installer/oneclick/backup-heavy.sh /mnt/backup/opencode
```

O script cria `opencode-heavy-<UTC>.tar.zst`, exclui `node_modules` e grava o
SHA-256 ao lado. Ele não apaga nem move os originais. Verifique o espaço livre:
o conteúdo atual é de aproximadamente 17 GB antes da compressão.

## Segurança e limites

- Sem `sudo` automático; sem `curl | bash` automático; sem tokens em arquivo.
- Versões npm podem mudar; o catálogo fixa o pacote, não o hash do tarball.
  Para instalação com hash e commit, use `installer/linux/install.sh`, que é
  fail-closed e exige `ECOSYSTEM_REF` e SHA-256.
- `--check` só prova presença/versão no PATH atual; não prova autenticação,
  execução, qualidade ou disponibilidade do provedor.
- `remotion` exige aceite de host e aprovação de render separada.
- `codex` pode existir apenas como interop Windows; o check Linux pode falhar
  mesmo com a CLI instalada no Windows.

## Recibos

Cada `--apply` grava:

- `reports/installer/oneclick-<UTC>.log`
- `reports/installer/oneclick-<UTC>.json`

O recibo separa `already_ok`, `installed`, `manual`, `blocked` e `failed`.
