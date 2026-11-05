# SPEC-1071 — Organização e distribuição do repositório

- **Status:** implementado localmente; publicação (push/tag) pendente de decisão
- **Data:** 2026-11-05
- **Escopo:** higiene do repositório, política de artefatos e pacote reproduzível

## 1. Contexto

O repositório acumulava 806 exclusões não commitadas (cache ASR de um piloto),
159 arquivos não rastreados (TCC, vídeo de banca e artigo Maria Socorro) e
artefatos de build de LaTeX/vídeo sem regra de ignore. O conteúdo rastreado é
enxuto (~57 MB), mas o diretório de trabalho chega a ~40 GB por causa de dados
locais ignorados.

## 2. Requisitos

- **R1.** Separar fontes de artefatos regeneráveis (áudio, segmentos, build).
- **R2.** Versionar os entregáveis finais (PDF, DOCX, MP4, SRT) de forma explícita.
- **R3.** Commits temáticos, sem misturar TCC, vídeo, artigo e infraestrutura.
- **R4.** Gerar um pacote de distribuição com fonte, entregáveis, manifesto e SHA-256.
- **R5.** Documentar instalação, verificação e publicação.

## 3. Critérios de aceitação

1. `git status` limpo após os commits, exceto artefatos ignorados.
2. `git check-ignore` confirma as regras para `segments/`, `build/`, `_TCC_COMPLETO.md`,
   `tcc_wrapper.pdf`, `*.dubbing-asr-large/` e `release/`.
3. PDFs, DOCX, MP4 e SRT dos entregáveis entram no índice.
4. `./scripts/distribuir.sh <versao>` produz `release/<versao>/` com tarball,
   entregáveis, `MANIFEST.md` e `SHA256SUMS.txt` verificável.
5. Nenhum segredo versionado (`.env*` permanece ignorado; exemplos são mantidos).

## 4. Evidências

- Commits: `chore(repo)`, `docs(tcc)` ×2, `docs(artigo)`, `chore(dist)`.
- `python3 -m marceloclaro.cli doctor`: 22/22 checks.
- `sha256sum -c release/<versao>/SHA256SUMS.txt`: todos OK.
- `git archive` inclui apenas arquivos rastreados no commit.

## 5. Limites

- O pacote não inclui dados locais ignorados (`.venv`, `.mci_state`, `research/`,
  `outputs/`, `external/`, `Panoramica_*`).
- Mídia regenerável (segmentos de vídeo, áudio intermediário de build) fica fora
  do tarball, mas o MP4 final e os MP3 por cena são versionados para reprodução
  offline.
- A publicação no GitHub (push, tag e release) exige decisão do mantenedor.
