# Pesquisador Universal v4.2 — Native Scientific Runtime

A v4.2 move o caminho essencial para dentro do OpenCode Ecosystem Core.

```text
marceloclaro
  └─ scientific_lab v4.2
      ├─ research/articles  [NATIVO]
      ├─ review             [NATIVO]
      ├─ evidence           [NATIVO]
      ├─ mesh/mission       [fallback v4.1 verificado]
      ├─ living/synthesis   [fallback v4.1 verificado]
      ├─ grade/causal       [fallback v4.1 verificado]
      └─ federation/prod    [fallback v4.1 verificado]
```

## Busca e download

```bash
python -m marceloclaro.scientific_lab research search "tema" --workspace .
python -m marceloclaro.scientific_lab research harvest "tema" --workspace . --max-downloads 10
```

A ordem padrão privilegia literatura científica e fontes abertas: OpenAlex, Europe PMC, SciELO, arXiv, Semantic Scholar e CORE; Crossref/PubMed são usados sobretudo para descoberta/metadados. O downloader só persiste PDF se a rota aberta for verificável e os primeiros bytes forem `%PDF-`.

## Revisão sistemática

```bash
python -m marceloclaro.scientific_lab review init --project-id PRJ-001 --title "Título" --question "Pergunta" --human --approved-by R1
python -m marceloclaro.scientific_lab review ingest --manifest 01_sources/metadata/search-....json
python -m marceloclaro.scientific_lab review screen --protocol-id SRP-PRJ-001 --study STUDY-... --stage full_text --reviewer R1 --decision include --reason "..." --human
python -m marceloclaro.scientific_lab review prisma --protocol-id SRP-PRJ-001 --human-verified
```

## Evidence Graph

`verified` exige arquivo-fonte hashado e decisão humana; mineração/automação só deve criar candidatos. O grafo mantém `candidate_edges_are_not_evidence_until_verified`.

## Pesquisador ponta a ponta (R1051)

O subcomando `research project` encadeia tema, contrato de recuperação,
protocolo, busca, deduplicação, triagem assistida, evidências literais, gate
metacognitivo, análise descritiva, auditoria, manuscrito e checklist humano.

```bash
python -m marceloclaro.scientific_lab research project \
  --theme "tema" --out projects/tema-r1051 --dry-run
```

O pacote fica file-first e inclui `08_manifest/project-manifest.json` com
hashes. O pipeline não usa credenciais e não publica. Claims de metadados são em
nível de resumo indexado; o corpus opcional é validado literalmente contra o
texto fornecido. Ver
[`SCIENTIFIC_RESEARCH_PIPELINE_R1051.md`](SCIENTIFIC_RESEARCH_PIPELINE_R1051.md).

O R1052 acrescenta texto integral local, aprovação humana explícita, leitura das
decisões de `review.screen`, verificação de retratações/correções no Crossref,
download opcional apenas por rota aberta e `research refresh` sem refazer a
busca. Ver
[`SCIENTIFIC_RESEARCH_PIPELINE_R1052.md`](SCIENTIFIC_RESEARCH_PIPELINE_R1052.md).

O R1053 acrescenta meta-análise fixa/aleatória, I²/Q/tau², intervalo de
predição, risco de viés e GRADE human-gated, além do pacote de submissão
Markdown/LaTeX/DOCX com checklist e declarações. Ver
[`SCIENTIFIC_RESEARCH_PIPELINE_R1053.md`](SCIENTIFIC_RESEARCH_PIPELINE_R1053.md).

O R1054 acrescenta extração automática de efeitos como rascunho auditável,
sugestões automáticas de RoB/GRADE, perfil PLOS ONE, submissão fail-closed,
gate de validação externa/aceite e validação numérica BCG contra referência
REML pública. Ver
[`SCIENTIFIC_RESEARCH_PIPELINE_R1054.md`](SCIENTIFIC_RESEARCH_PIPELINE_R1054.md).

## Limite da v4.2

Não alegamos que todos os 88 contratos da v4.1 foram internalizados. O objetivo desta release é remover a dependência externa do caminho essencial e manter os módulos avançados em fallback verificável até migração posterior.
