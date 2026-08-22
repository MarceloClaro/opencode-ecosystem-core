---
spec_id: SPEC-935-R436
component: rag.enhanced_search_rag
title: Buscas Unificadas + RAG Aprimorado + Referências ABNT Auditáveis
version: 1.0.0
status: green
test_file: tests/test_r436_enhanced_search_rag.py
---

# SPEC-935-R436 — Buscas Unificadas, RAG Aprimorado e Referências ABNT Auditáveis

## Meta
- **Ciclo**: R436
- **Antecessor**: R435 (98/9.8) — harness universal; agora completa-se o tripé busca→RAG→referência
- **Alvo**: 9.9 (99) — busca meta-agregada, RAG com expansão/citação/temporal e auditoria ABNT determinística
- **Módulo**: `rag/enhanced_search_rag.py` + integração no orquestrador

## Diagnóstico atual
- **Buscas**: `research/searchers.py` tem 6 providers (Arxiv, SemanticScholar, Crossref, OpenAlex, EuropePMC, Scielo) via `MultiSearcher`, mas cada um é chamado isolado; sem deduplicação por DOI/título, sem scoring unificado, sem cache, sem busca local (RAG index) + web (antigravity) no mesmo ranking.
- **RAG**: `rag/scientific.py` (ScientificRAG, NBR grounding) e `rag/evolved.py` (AdaptiveRetriever + CitationGraph + OutlineSynthesizer) são funcionais, mas sem expansão de consulta (sinônimos), sem decaimento temporal (artigos recentes não são priorizados), sem verificação de alucinação por citação obrigatória, e sem integração com buscas externas.
- **Referências**: `12_agente_auditoria_bibliografica_abnt` existe como agente, mas não há auditor programático: ABNT NBR 6023:2018, detecção de DOI/ano/autor ausente, duplicata por título normalizado, e formato BibTeX não são verificados deterministicamente.

## Arquitetura R436

```
                 UnifiedSearcher ──────────────────────────────────┐
                 │  MultiSearcher (6 providers) + RAG local + web  │
                 │  dedup DOI/título, scoring 0.55lex+0.35sem+temporal+cite, cache
                 └──────────────┬──────────────────────────────────┘
                                ▼
                    EnhancedRAG ───────────────────────┐
                    │ ScientificRAG + RAGEvolved       │
                    │ + query_expansion (sinônimos)    │
                    │ + temporal_decay (half-life 5a)  │
                    │ + citation_graph expansion       │
                    │ + grounding_evaluator + métricas │
                    └───────────┬──────────────────────┘
                                ▼
                    ReferenceAuditor ────────────────┐
                    │ ABNT/APA/BibTeX, DOI/ano/autor │
                    │ duplicata (título norm), link  │
                    └───────────┬────────────────────┘
                                ▼
                    UnifiedSearchRAG (fachada) + orquestrador
```

### C1 — UnifiedSearcher (`enhanced_search_rag.py`)
| Método | Contrato |
|---|---|
| `search(query, limit=10, providers=None, use_cache=True)` | Busca em `MultiSearcher` (ou searchers injetados), RAG local (se indexado) e web (injetável); deduplica por `doi` ou `titulo_normalizado`; score unificado `0.55*lexical + 0.35*semantic + 0.07*temporal + 0.03*cite`; cache em memória com TTL 300s; publica `search.completed` no MetaBus |
| `temporal_score(year)` | `0.07 * exp(-0.1386*(current_year - year))` (half-life 5 anos, clamp [0,0.07]) |
| `deduplicate(records)` | Remove duplicatas por `doi.lower()` ou `titulo_normalizado` (lower, sem acentos, pontuação) |
| `clear_cache()` | Limpa cache |

Invariante: sem provider disponível → retorna lista vazia, não erro; injeção de `searchers` permite TDD determinístico.

### C2 — EnhancedRAG (`enhanced_search_rag.py`)
Envolve `ScientificRAG` + `RAGEvolved`:

| Método | Contrato |
|---|---|
| `index(docs)` | Delega a `ScientificRAG.index` + indexa no `CitationGraph` |
| `query_expansion(query)` | Expande via `ScientificRAG.EXPANSION_DICT` (ex. "causal"→{"causal","casual?"…}) + sinônimos de `scientific.py` |
| `temporal_boost(evidence)` | Re-ranqueia `RetrievedEvidence` por `final_score + temporal_score(year)` |
| `retrieve_enhanced(query, top_k=5, expand=True, temporal=True, cite_expand=True)` | `query_expansion` → `RAGEvolved.retrieve_adaptive` ou `ScientificRAG.retrieve` → `temporal_boost` → `CitationGraph.expand_retrieval` → dedup → top_k |
| `answer_grounded(query, top_k=3)` | `retrieve_enhanced` + `ScientificRAG.answer` com `abstained` se `final_score<min_score`; inclui `groundedness`, `citation_coverage` |
| `metrics(evidence)` | `{groundedness, citation_coverage, temporal_spread, avg_year}` |

### C3 — ReferenceAuditor (`enhanced_search_rag.py`)
| Método | Contrato |
|---|---|
| `normalize_title(title)` | Lower, NFKD sem acentos, remove pontuação, colapsa espaços |
| `audit(references)` | Cada ref dict com `title, authors, year, source, doi?` → verifica `abnt_compliant` (autor+ano+título+fonte), `has_doi`, `year_valid` (1400≤ano≤current+1), `duplicate` (título normalizado), `completeness_score` 0-1; retorna `{total, valid, duplicates, incomplete, by_id:{id:{issues:[], score}}}` |
| `format_abnt(ref)` | `SOBRENOME, Nome. Título. Fonte, ano.` (heurística ABNT simplificada, determinística) |
| `format_bibtex(ref)` | `@article{key, title={}, author={}, year={}, journal={}}` |

### C4 — Fachada + Orquestrador
- `UnifiedSearchRAG` compõe os três, expõe `search`, `rag_query`, `audit`, `status`
- `MarceloClaroOrchestrator.search_rag_status()` → `EnhancedRAG` + `UnifiedSearcher` + `ReferenceAuditor` status
- `unified_search(query, limit, providers)` → `UnifiedSearcher.search`
- `rag_query(query, top_k, task_type)` → `EnhancedRAG.answer_grounded` com `ModelRouter` quando disponível
- `audit_references(references)` → `ReferenceAuditor.audit`

## Critérios de aceitação (teste R436)
1. AC1 — SPEC-935-R436 `green`.
2. AC2 — `UnifiedSearcher.search` com searchers injetados deduplica por DOI e retorna ranking temporal (ano recente > antigo para mesma lexical).
3. AC3 — `temporal_score(2026) > temporal_score(2010)` e `0≤score≤0.07`.
4. AC4 — `deduplicate` remove duplicata por `doi` case-insensitive e por `titulo_normalizado`.
5. AC5 — `EnhancedRAG.query_expansion` expande "causal" com sinônimos do dicionário.
6. AC6 — `retrieve_enhanced` retorna evidências re-ranqueadas com `final_score` boost temporal.
7. AC7 — `answer_grounded` com índice vazio abstém (`abstained True`); com docs retorna `groundedness≥0`.
8. AC8 — `metrics` calcula `citation_coverage` e `temporal_spread`.
9. AC9 — `ReferenceAuditor.audit` detecta `has_doi False`, `year_valid False`, `duplicate True` e `completeness_score`.
10. AC10 — `format_abnt` e `format_bibtex` geram saídas determinísticas com `title` e `year`.
11. AC11 — `UnifiedSearchRAG` fachada integra os três e `status()` é auditável.
12. AC12 — Orquestrador expõe `search_rag_status`, `unified_search`, `rag_query`, `audit_references` e `doctor` mantém 99 specs.

## Não objetivos
- Não chama APIs reais em teste (searchers injetados); produção usa `MultiSearcher` existente.
- Não substitui `12_agente_auditoria_bibliografica_abnt` — o auditor é determinístico, o agente permanece para revisão qualitativa.
- Não exige Whoosh local em teste; busca local é opcional.

## Score 99 — decomposição
R435 9.8 + busca unificada dedup+temporal 0.04 + RAG expansão/citação 0.03 + auditoria ABNT 0.03 = 9.9
