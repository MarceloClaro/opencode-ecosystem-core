# SPEC-017 — Subsistema Research: Busca e Extração Acadêmica

```yaml
spec_id: SPEC-017
title: Research — buscadores, downloads, PDF→MD, fichamentos e resenhas ABNT/APA
status: implemented
version: 1.0.0
depends_on: [SPEC-001, SPEC-005, SPEC-010, SPEC-016]
inspirations:
  - https://github.com/Oxidane-bot/scihub-cli
  - https://github.com/Oxidane-bot/paper-download-mcp
modules:
  - research/searchers.py     # buscadores multiplataforma
  - research/downloader.py    # download de PDFs (scihub-cli + OA direto)
  - research/pdf2md.py        # conversão PDF → Markdown
  - research/fichamento.py    # fichamentos, resenhas, ABNT/APA/BibTeX
  - research/hub.py           # ResearchHub (pipeline unificado)
```

## Requisitos

| ID | Requisito | Critério de aceitação |
| --- | --- | --- |
| REQ-017.1 | Busca federada em plataformas de artigos científicos: arXiv, OpenAlex, Crossref, Semantic Scholar, Europe PMC (PubMed) | `MultiSearcher.search()` retorna `PaperRecord` normalizados e deduplicados por DOI/título |
| REQ-017.2 | Busca em repositórios de código e dados: GitHub e Kaggle | Registros com `extra.type` ∈ {repository, dataset} listados em `repositorios.md` |
| REQ-017.3 | Download de PDFs com roteamento em duas camadas: scihub-cli (multi-fonte: OpenAlex, Europe PMC, arXiv, Unpaywall, Sci-Hub) quando instalado; fallback stdlib com validação de magic bytes `%PDF-` | `PaperDownloader.download()` salva PDFs válidos em `pesquisa/pdfs/` |
| REQ-017.4 | Conversão automática PDF→Markdown de TODOS os PDFs baixados, salvos na subpasta de produção de pesquisa | `Pdf2Markdown.convert()` gera `.md` com frontmatter YAML em `pesquisa/md/` (backends: pymupdf4llm → pdftotext → pypdf) |
| REQ-017.5 | Fichamento em três camadas de CADA artigo (bibliográfico, citação, crítico) com criticidade ao tema de pesquisa | `FichamentoWriter.fichamento()` gera arquivo em `pesquisa/fichamentos/` com aderência 0–10, pontos fortes, limitações e lacunas |
| REQ-017.6 | Resenha crítica de CADA artigo em texto corrido acadêmico vinculada ao tema | `FichamentoWriter.resenha()` gera arquivo em `pesquisa/resenhas/` com veredicto de leitura |
| REQ-017.7 | Referências em ABNT atualizado (NBR 6023:2018) e APA 7ª edição, mais citações NBR 10520:2023 e BibTeX para os templates LaTeX | `referencias_abnt.md` (alfabética), `referencias_apa.md` e `referencias.bib` gerados |
| REQ-017.8 | Pasta única de produção: pesquisa integrável à pasta do `produce_scientific_work` (SPEC-016) | `ResearchHub(production_folder=...)` anexa `pesquisa/` à pasta existente |
| REQ-017.9 | Manifest auditável com checksums SHA-256 | `RESEARCH_MANIFEST.json` com resumo, downloads, normas e hashes |
| REQ-017.10 | Integração ao orquestrador | `orch.research_search()` e `orch.research()` com reflexão metacognitiva registrada no Global Workspace |

## Invariantes

- **INV-017.1** — Nenhuma dependência obrigatória fora da stdlib; scihub-cli, pymupdf4llm e LLM são aprimoramentos opcionais.
- **INV-017.2** — Todo PDF salvo DEVE iniciar com `%PDF-` (rejeitar HTML de paywall).
- **INV-017.3** — Referências ABNT em ordem alfabética; 100% de correspondência entre artigos fichados e referências.
- **INV-017.4** — O fichamento crítico DEVE declarar a aderência ao tema (0–10) e o veredicto de leitura.
- **INV-017.5** — Uso ético: o downloader prioriza fontes de acesso aberto (OA); Sci-Hub só é acionado via scihub-cli instalado explicitamente pelo usuário.

## Ciclo TDD

- RED: `tests/test_research.py` escrito contra esta spec.
- GREEN: implementação em `research/`.
- REFACTOR: consolidação do ranking por aderência no `CriticalAnalyzer` (compartilhado entre hub e orquestrador).
