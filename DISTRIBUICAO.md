# Distribuição do OpenCode Ecosystem Core

Este documento descreve o que é versionado, o que é regenerável e como produzir
um pacote verificável do ecossistema.

## 1. O que vai no repositório

O repositório guarda **fontes e entregáveis**, não o estado local de execução.

| Categoria | Exemplos | Política |
|---|---|---|
| Código e configuração | `marceloclaro/`, `mcp/`, `agents/`, `opencode.json` | versionado |
| Especificações e docs | `specs/`, `docs/`, `README.md`, `ARCHITECTURE.md` | versionado |
| Dados oficiais pequenos | `artigos/**/dados/*.csv`, `*.json` | versionado |
| Entregáveis | TCC PDF/DOCX, vídeo MP4, `legendas.srt`, artigos em PDF | versionado |
| Fontes de build | `.md`, `.tex`, `build_tcc.py`, scripts | versionado |
| Áudio por cena | `video_banca/audio/*.mp3`, `*.srt` | versionado (reprodução offline) |
| Segmentos de vídeo | `video_banca/segments/` | ignorado (regenerável) |
| Build LaTeX/vídeo | `_TCC_COMPLETO.md`, `tcc_wrapper.pdf`, `build/` | ignorado |
| Estado local | `.venv/`, `.mci_state/`, `research/`, `outputs/`, `external/` | ignorado |
| Segredos | `.env`, `.env.litellm` | ignorado; só `.example` é versionado |

O conteúdo rastreado soma aproximadamente **1,14 GB em 13,2 mil arquivos**, incluindo
podcasts, apresentações e binários de evidência históricos. O diretório de trabalho
chega a ~40 GB por causa de dados locais ignorados. Por isso o pacote de distribuição
tem dois modos: **leve** (padrão) e **completo**.

## 2. Gerar o pacote

```bash
cd /home/marceloclaro/opencode-ecosystem-core

# pacote leve (~250 MB): código, docs, specs, artigos e entregáveis
./scripts/distribuir.sh v1.1.0

# pacote completo (~780 MB): inclui podcasts, apresentações e binários históricos
./scripts/distribuir.sh v1.1.0 --completo
```

Saída em `release/v1.1.0/`:

```
opencode-ecosystem-core-v1.1.0.tar.gz   fonte rastreada no HEAD
entregaveis/                            PDF, DOCX, MP4 e SRT
opencode-ecosystem-core-v1.1.0-entregaveis.zip
MANIFEST.md                             commit, data, versão, modo e tamanhos
SHA256SUMS.txt                          hashes de todos os arquivos
```

O tarball é gerado a partir de `git ls-files` (working tree limpo = HEAD), portanto
**não inclui** arquivos ignorados nem alterações não commitadas.

No modo leve ficam de fora, apenas do tarball:

- `livro-core/output/` (podcasts e vídeos);
- `odonto/preservado/` e `odonto/submission_package*`;
- `docs/evidence/` (binários de evidência);
- `validacao_externa/`, `.backups/`, `manuscrito_porescrito799_R522/`;
- `templates/projects/` (instaladores);
- extensões `m4a`, `mp3`, `mp4`, `wav`, `xdv`, `pptx`, `msi` e `zip`.

Esses arquivos continuam versionados no repositório; a exclusão vale só para o
pacote. Os entregáveis finais (TCC, vídeo e artigos) vão em `entregaveis/`.

## 3. Verificar

```bash
cd release/v1.1.0
sha256sum -c SHA256SUMS.txt
```

Todos os arquivos devem responder `OK`. O `MANIFEST.md` registra o commit exato
usado na geração.

## 4. Instalar a partir da fonte

```bash
tar -xzf opencode-ecosystem-core-v1.1.0.tar.gz
cd opencode-ecosystem-core-v1.1.0
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m marceloclaro.cli doctor
```

O `doctor` deve encerrar com `checks_failed: 0`. Para a suíte de testes:

```bash
pytest -q
```

## 5. Publicar no GitHub

O repositório usa o remote `MarceloClaro/opencode-ecosystem-core`.

```bash
# 1. revisar o que será enviado
git log --oneline origin/main..HEAD
git diff --stat origin/main..HEAD

# 2. enviar a branch atual
git push origin codex/core-prontidao-rea

# 3. criar a tag e enviá-la
git tag -a v1.1.0 -m "OpenCode Ecosystem Core v1.1.0"
git push origin v1.1.0
```

Depois, na interface do GitHub, criar o *release* `v1.1.0` anexando
`opencode-ecosystem-core-v1.1.0.tar.gz`, o ZIP de entregáveis e o
`SHA256SUMS.txt`. O `gh` CLI não está disponível neste ambiente; a publicação
de release deve ser feita pela web ou por token pessoal.

## 6. O que não é distribuído

- Dados locais de pesquisa e caches (`.mci_state/`, `research/`, `outputs/`).
- Ambientes virtuais e dependências instaladas (`.venv/`).
- Repositórios externos clonados (`external/`, `Panoramica_*`, `LiteRT-LM-main/`).
- Segredos e credenciais (`.env`, `.env.litellm`).
- Segmentos intermediários de vídeo e builds de LaTeX.

## 7. Reprodutibilidade dos artigos

Cada pasta de artigo mantém seus próprios relatórios:

- `artigos/TCC_MARCELO_AUTISMO_AH_SD/`: `RELATORIO_DADOS.md`, `RELATORIO_DOI.md`,
  `SHA256SUMS.txt`, `dados/` e `build_tcc.py`;
- `artigos/ARTIGO_MARIA_SOCORRO_TEA/`: `RELATORIO_*.md`, `TCC/RELATORIO_DOI_TCC.md`,
  `SHA256SUMS.txt` e `dados/`.

Os vídeos e PDFs são entregáveis finais; suas fontes e scripts permanecem no
repositório para regeneração.
