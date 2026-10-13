# SPEC-980 — Ampliação da Base: Sucupira, PubMed, arXiv, CAPES e Brasileiras

```yaml
spec_id: SPEC-980
title: Consulta federada legal em 8 bases além de Crossref/OpenAlex/Unpaywall
status: green
component: research/fontes_expandidas.py + research/searchers.py
test_file: tests/test_r980_fontes_expandidas.py
validation_scope: local_runtime
```

## Contexto

A base atual cobre Crossref/OpenAlex/Unpaywall + arXiv/EuropePMC/SciELO parcial via `research/searchers.py`. O usuário exige ampliação como Sucupira e plataformas PubMed, arXiv, CAPES e outras brasileiras, mantendo gate OA e auditoria SPEC-977/978.

Fontes oficiais levantadas em 2026-10-11:
- Sucupira Observatório público: `https://apigw-proxy.capes.gov.br/observatorio/data/observatorio/ies?search=...&page=0&size=10` + facetas/query; sem chave.
- Dados Abertos CAPES (CKAN): `https://dadosabertos.capes.gov.br/api/3/action/package_search?q=...`; Catálogo de Teses: `https://catalogodeteses.capes.gov.br/`.
- PubMed E-utilities: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=...&retmode=json` + `esummary/efetch`; sem chave, com `mailto` e `User-Agent`.
- arXiv Atom: `http://export.arxiv.org/api/query?search_query=all:...`; público.
- SciELO: `https://search.scielo.org/?q=...` + OAI `https://search.scielo.org/oai/scielo-oai.php`; público.
- LILACS/BVS: `https://pesquisa.bvsalud.org/portal/?q=...` + iAHx XML; público.
- OasisBR/BDTD (IBICT): `https://oasisbr.ibict.br/` + `https://bdtd.ibict.br/` via OAI; público.
- Portal de Periódicos CAPES: `https://www.periodicos.capes.gov.br/` exige login institucional — **fail-closed**, só rota institucional, nunca bypass.
- Alinhamento CAPES: Ofício Circular 30/2026-DAV usa OpenAlex via ORCID como fonte de importação — nossa base OpenAlex permanece canônica.

## Requisitos

| ID | Requisito | Critério de aceitação |
|----|-----------|----------------------|
| R-980.1 | Módulo federado | `research/fontes_expandidas.py` com `buscar_todas(query, limit, runners)` que agrega sem duplicar DOI e preserva `fonte` por registro |
| R-980.2 | PubMed | `buscar_pubmed` via E-utilities com `retmode=json`; retorna PMID, título, autores, ano, DOI quando houver; falha de rede retorna `[]` com erro registrado |
| R-980.3 | arXiv | `buscar_arxiv` via Atom; retorna `arxiv_id`, título, autores, ano, `pdf_url`; respeita `limit` |
| R-980.4 | SciELO/LILACS/OasisBR/BDTD | Buscadores por OAI/portal público; retornam título, fonte, URL landing e OA quando indicado; sem credencial |
| R-980.5 | Sucupira + Dados Abertos | `buscar_sucupira_observatorio` via `search`+paginação e `buscar_capes_dados_abertos` via CKAN; retornam programas/teses/datasets com `fonte` e URL pública |
| R-980.6 | Portal CAPES fail-closed | `consultar_portal_capes` nunca tenta login/bypass; retorna `status=unavailable` + rota institucional |
| R-980.7 | Gate preservado | Todo registro com `pdf_url` só é baixável se `is_download_allowed` permitir; registro fechado indica rota; sci-hub bloqueado em todas as fontes |
| R-980.8 | Proveniência | Cada registro com `fonte`, `url_consulta`, `data_consulta`, `hash_resposta`; deduplicação por DOI normalizado |

## Invariantes

- INV-980.1: Nenhuma credencial embutida; e-mail institucional via env quando exigido.
- INV-980.2: Stdlib-only no núcleo (`urllib`, `json`, `xml`, `re`, `hashlib`).
- INV-980.3: Respeito a `retmax`/`size`/`limit`; sem varredura massiva.
- INV-980.4: Portal CAPES nunca consultado com bypass.

## Fora de escopo

- Integração OAI-PMH CAPES completa (GoPG) e importação automática para Sucupira; credenciais institucionais do usuário; tradução DeCS/MeSH automática.

## Validação

Unitário hermético com runners falsos + 1 prova real amostral por fonte pública (PubMed, arXiv, Sucupira, CKAN) com `limit<=3`, sem download integral.
