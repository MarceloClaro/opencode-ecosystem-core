---
name: evo-4-scihub-pipeline
description: "Skill auto-gerada pelo Manus Evolve — Round 3. Padroes: Sci-Hub MCP, arXiv API, academic paper search, multi-source paper download. Score: 88/100"
evolved: true
round: 3
source: "manus-evolve-plugin"
---

# Evo-4: Pipeline Integrado de Busca e Download de Artigos

## Plano Original
Integrar multiplas fontes de busca academica (Sci-Hub MCP + arXiv API + Semantic Scholar) em um pipeline unificado com fallback automatico e download de PDFs.

## Acoes Executadas
- scihub: search_scihub_by_keyword, download_scihub_pdf, get_paper_metadata
- academic_search: busca arXiv com 8 papers retornados em segundos
- fetch: validacao de URLs e metadados cruzados entre fontes
- code-runner: academic_search.py com funcoes search_arxiv e download_arxiv_pdf
- memory: registro de papers encontrados para evitar re-busca

## Reflexoes & Aprendizados
- Sci-Hub esta sob Cloudflare — acesso programatico instavel, usar como fallback
- arXiv API e 100% funcional, gratuita e sem rate limit — fonte primaria
- Semantic Scholar requer API key para uso sustentavel (>100 req/5min)
- Download direto de PDF do arXiv via arxiv.org/pdf/{id}.pdf

## Melhores Praticas Extraidas
1. Sempre tentar arXiv primeiro (gratuito, ilimitado, estavel)
2. Sci-Hub como fallback quando arXiv nao tem o paper (DOI de journal fechado)
3. Cache de resultados para evitar chamadas repetidas a APIs rate-limited
4. Validar DOI com fetch antes de tentar download para evitar tempo perdido

## Score de Evolucao
88/100
