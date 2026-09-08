# SPEC-017 — Subsistema Research: Busca e Extração Acadêmica

```yaml
spec_id: SPEC-017
title: Research — busca Open Science, downloads OA, PDF→MD, fichamentos e resenhas ABNT/APA
status: implemented
version: 2.0.0
depends_on: [SPEC-001, SPEC-005, SPEC-010, SPEC-016, SPEC-935-R468]
open_science_priority:
  - OpenAlex
  - Unpaywall
  - Europe PMC
  - arXiv
  - SciELO
  - Semantic Scholar openAccessPdf
modules:
  - research/searchers.py     # buscadores multiplataforma
  - research/downloader.py    # download apenas por rotas OA/repositório/preprint
  - research/pdf2md.py        # conversão PDF → Markdown
  - research/fichamento.py    # fichamentos, resenhas, ABNT/APA/BibTeX
  - research/hub.py           # ResearchHub (pipeline unificado)
```

## Requisitos

| ID | Requisito | Critério de aceitação |
| --- | --- | --- |
| REQ-017.1 | Busca federada em plataformas de artigos científicos: arXiv, OpenAlex, Crossref, Semantic Scholar, Europe PMC/PubMed e SciELO | `MultiSearcher.search()` retorna `PaperRecord` normalizados e deduplicados por DOI/título |
| REQ-017.2 | Busca em repositórios de código e dados: GitHub e Kaggle | Registros com `extra.type` ∈ {repository, dataset} listados em `repositorios.md` |
| REQ-017.3 | Download de PDFs com prioridade Open Science: URL já classificada OA → OpenAlex por DOI → Unpaywall por DOI (quando e-mail configurado) → Europe PMC por DOI | `PaperDownloader.download()` salva apenas PDFs válidos em `pesquisa/pdfs/`, registra método, SHA-256 e fundamento de acesso |
| REQ-017.4 | Conversão automática PDF→Markdown de TODOS os PDFs baixados, salvos na subpasta de produção de pesquisa | `Pdf2Markdown.convert()` gera `.md` com frontmatter YAML em `pesquisa/md/` (backends: pymupdf4llm → pdftotext → pypdf) |
| REQ-017.5 | Fichamento em três camadas de CADA artigo (bibliográfico, citação, crítico) com criticidade ao tema de pesquisa | `FichamentoWriter.fichamento()` gera arquivo em `pesquisa/fichamentos/` com aderência 0–10, pontos fortes, limitações e lacunas |
| REQ-017.6 | Resenha crítica de CADA artigo em texto corrido acadêmico vinculada ao tema | `FichamentoWriter.resenha()` gera arquivo em `pesquisa/resenhas/` com veredicto de leitura |
| REQ-017.7 | Referências em ABNT NBR 6023:2018 e APA 7ª edição, mais citações NBR 10520:2023 e BibTeX | `referencias_abnt.md`, `referencias_apa.md` e `referencias.bib` gerados |
| REQ-017.8 | Pasta única de produção: pesquisa integrável à pasta do `produce_scientific_work` (SPEC-016) | `ResearchHub(production_folder=...)` anexa `pesquisa/` à pasta existente |
| REQ-017.9 | Manifest auditável com checksums SHA-256 | `RESEARCH_MANIFEST.json` com resumo, downloads, normas e hashes |
| REQ-017.10 | Integração ao orquestrador | `orch.research_search()` e `orch.research()` com reflexão metacognitiva registrada no Global Workspace |
| REQ-017.11 | Nenhum executor destinado a contornar paywall integra o runtime ativo de pesquisa | downloader usa stdlib + resolvers Open Science; ausência de cópia aberta é reportada como falha explícita |
| REQ-017.12 | Crossref é usado para DOI/metadados, não presumido como autorização de download | `pdf_url` oriundo de `source=crossref` não é baixado automaticamente sem classificação OA adicional |

## Invariantes

- **INV-017.1** — Nenhuma dependência obrigatória fora da stdlib para busca/download; `pymupdf4llm` e LLMs permanecem aprimoramentos opcionais.
- **INV-017.2** — Todo PDF salvo DEVE iniciar com `%PDF-`; HTML, landing pages e paywalls são rejeitados.
- **INV-017.3** — Referências ABNT em ordem alfabética; 100% de correspondência entre artigos fichados e referências.
- **INV-017.4** — O fichamento crítico DEVE declarar a aderência ao tema (0–10) e o veredicto de leitura.
- **INV-017.5** — O downloader só promove rotas classificadas como `open_access`, `repository`, `preprint` ou equivalentes de fontes OA conhecidas.
- **INV-017.6** — DOI, URL de publisher ou HTTP 200 isoladamente NÃO comprovam acesso aberto.
- **INV-017.7** — Cada download aceito registra SHA-256, tamanho, método/resolvedor e validação de magic bytes.
- **INV-017.8** — Ausência de cópia aberta não autoriza fallback para mecanismo de evasão de acesso.

## Ciclo TDD

- RED: `tests/test_research.py` + `tests/test_research_open_science_v42.py`.
- GREEN: implementação em `research/`.
- REFACTOR: consolidar ranking, deduplicação e integração com a supercamada científica v4.x.

## Compatibilidade e histórico

Registros antigos em `evolution/`, `VALIDATION_*.md` e specs legadas podem citar mecanismos usados em versões anteriores. Esses registros são preservados como histórico e não definem o runtime v2 desta SPEC.
