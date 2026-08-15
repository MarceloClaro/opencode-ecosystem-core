# evo-56 — R425: Pacote final de submissão RBEP

## Objetivo

Gerar, por script, o pacote ZIP final de submissão à RBEP/INEP com todos
os artefatos necessários: manuscrito (DOCX/PDF/MD), carta ao editor,
relatório de revisão, proveniência numérica e manifesto SHA-256.

## Mudanças

1. `specs/SPEC-935-R425-pacote-submissao.md` — especificação com 6
   critérios de aceitação (estrutura, manifest, integridade, exclusão de
   temporários, testes, registro evolutivo).
2. `scripts/empacotar_submissao.py` — offline; monta o ZIP em
   `outputs/submission/ARTIGO_RBEP_SUBMISSAO_submissao_<DATA>.zip` com:
   - `01_manuscrito/` (DOCX 16 tabelas + PDF 20p + MD canônico)
   - `02_carta/` (CARTA_AO_EDITOR.md)
   - `03_revisao/` (peer_review_r422.md)
   - `04_dados/` (9 JSONs de proveniência R412–R423)
   - `README_SUBMISSAO.md` (instruções, checklist, nota de conduta sem
     overclaim) e `MANIFEST_SUBMISSAO.json` (sha256 por arquivo).
   - Grava também o MANIFEST_SUBMISSAO.json solto (versionável).
3. `tests/test_r425_pacote_submissao.py` — 8 testes: existência,
   estrutura obrigatória, pastas, ausência de temporários, integridade
   SHA-256 (5+ arquivos), README sem overclaim, proveniência presente,
   DOCX com autoria+ORCID.
4. `.gitignore` — `outputs/submission/*.zip` ignorado (artefato
   regenerável; política do repo: PDFs/CSVs/zips não versionados).

## Verificação

- Pacote: 270,5 KiB, 9 arquivos + manifest.
- Suíte R408–R425: **377 testes passed** (8 novos).
- Doctor: 10/12 pass, 0 failed (warns pré-existentes).

## Lições

- O pacote de submissão deve ser gerado por script (reprodutível) e
  auditável via manifest SHA-256; o ZIP é regenerável e não vai ao git,
  mas o script, a spec, o teste e o manifest solto ficam versionados.
- O README do pacote repete a nota de conduta anti-overclaim: "candidato
  a submissão" — documentos voltados a humanos mantêm as mesmas regras.
- Testes de DOCX dentro de ZIP exigem leitura via io.BytesIO, não Path.
