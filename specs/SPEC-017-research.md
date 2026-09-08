# SPEC-017 — Subsistema Research: Busca e Extração Acadêmica

```yaml
spec_id: SPEC-017
title: Research — busca, download OA, PDF→MD, fichamentos e resenhas ABNT/APA
status: implemented
version: 2.0.0
depends_on: [SPEC-001, SPEC-005, SPEC-010, SPEC-016, SPEC-935-R469]
modules:
  - research/searchers.py
  - research/downloader.py
  - research/pdf2md.py
  - research/fichamento.py
  - research/hub.py
```

## Requisitos

| ID | Requisito | Critério de aceitação |
| --- | --- | --- |
| REQ-017.1 | Busca federada em arXiv, OpenAlex, Crossref, Semantic Scholar, Europe PMC/PubMed, SciELO e CORE | `MultiSearcher.search()` retorna `PaperRecord` deduplicados por DOI/título |
| REQ-017.2 | Repositórios de código/dados permanecem separados de artigos | `extra.type` repository/dataset nunca é enviado ao downloader de artigos |
| REQ-017.3 | Download somente por rota open access/repositório/preprint verificada | `PaperDownloader.download()` não contorna paywall/login e valida `%PDF-` |
| REQ-017.4 | Resolução OA por DOI | OpenAlex é consultado; Unpaywall é opcional quando e-mail está configurado; Europe PMC é fallback biomédico |
| REQ-017.5 | Provenance do download | SHA-256, bytes, método, URL resolvida e base de direitos são registrados no resultado/receipt |
| REQ-017.6 | Conversão PDF→Markdown | `Pdf2Markdown.convert()` gera Markdown com frontmatter |
| REQ-017.7 | Fichamento/resenha e referências | ABNT NBR 6023:2018, NBR 10520:2023, APA 7 e BibTeX |
| REQ-017.8 | Pasta única de produção | `ResearchHub(production_folder=...)` anexa `pesquisa/` à produção |
| REQ-017.9 | Manifest auditável | `RESEARCH_MANIFEST.json` contém resumo e hashes |
| REQ-017.10 | Integração ao orquestrador e Scientific Lab | `orch.research()` e `python -m marceloclaro.scientific_lab research ...` |

## Invariantes

- **INV-017.1** — Nenhum mecanismo de contorno de paywall é executado pelo Core.
- **INV-017.2** — Todo PDF persistido começa com `%PDF-`; HTML/landing page é rejeitado.
- **INV-017.3** — DOI/URL de publisher não constitui por si só autorização de download.
- **INV-017.4** — Ausência de cópia OA é reportada como `not_verified_open`, nunca como “artigo inexistente”.
- **INV-017.5** — Download válido registra SHA-256 e base de acesso (`open_access`, `repository`, `preprint`, `public_domain` ou `user_authorized`).
- **INV-017.6** — Claims científicos não são promovidos automaticamente por busca, contagem de citações ou download.

## Ciclo TDD

- suíte histórica: `tests/test_research.py`;
- hardening OA e integração nativa: `tests/test_scientific_lab_v42_native.py`;
- SPEC de evolução: `SPEC-935-R469-pesquisador-universal-v42-native-runtime.md`.
