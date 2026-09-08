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

## Limite da v4.2

Não alegamos que todos os 88 contratos da v4.1 foram internalizados. O objetivo desta release é remover a dependência externa do caminho essencial e manter os módulos avançados em fallback verificável até migração posterior.
