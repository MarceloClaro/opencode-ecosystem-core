# SPEC-965: DataKnowledgeHub — Descoberta Unificada de Dados e Conhecimento

**Round**: R52
**Data**: 2026-07-25
**Status**: Implementado — 16 fontes integradas, 44/44 testes passando
**Score**: 0.92

## Objetivo

Criar um hub unificado de busca de dados, datasets e conhecimento
para alimentar a orquestração do ecossistema com fontes reais,
permitindo calibração de confiança, roteamento por domínio e
produção de pesquisa de ponta com embasamento factual.

## Lacunas Atuais

| Domínio | Situação | O que falta |
|---|---|---|
| **Dados financeiros** | Zero | yfinance, BCB/SGS, FRED, World Bank, Alpha Vantage |
| **Dados oficiais BR** | Apenas Datajud CNJ | IBGE/SIDRA, IPEA, dados.gov.br |
| **Datasets científicos** | Parcial (HuggingFace, data.gov, Kaggle) | Zenodo, DataCite, UCI, Figshare, Mendeley Data |
| **Conhecimento geral** | Zero | Wikipedia, ConceptNet, Google Scholar, Wikidata |
| **Busca federada** | Inexistentes como serviço unificado | Roteamento automático por domínio da consulta |

## Arquitetura

```
skills/tooling/data_knowledge_hub/
├── __init__.py           # DataKnowledgeHub (fachada unificada)
├── base.py               # DataSource (classe base abstrata)
├── financial.py          # FinancialDataSource (yfinance, BCB, FRED, World Bank)
├── official.py           # OfficialDataSource (IBGE/SIDRA, IPEA, dados.gov.br)
├── knowledge.py          # KnowledgeDataSource (Wikipedia, ConceptNet, Wikidata, Google Scholar)
├── datasets.py           # DatasetDataSource (Zenodo, DataCite, UCI, Figshare)
├── router.py             # DomainRouter (roteia consulta para fonte ideal)
└── templates/            # Templates de resposta formatada
    ├── financial_report.md.j2
    ├── dataset_citation.md.j2
    └── knowledge_fact.md.j2
```

## Fontes por Domínio

### Financeiro (financial.py)
| Fonte | API | Autenticação | Dados |
|---|---|---|---|
| yfinance | `yfinance` | Gratuita | Ações, ETFs, índices, câmbio |
| BCB/SGS | `api.bcb.gov.br/sgs` | Gratuita | SGS (2.000+ séries) — SELIC, IPCA, PIB, câmbio |
| FRED | `api.stlouisfed.org/fred` | Chave gratuita | 800K+ séries macroeconômicas EUA |
| World Bank | `api.worldbank.org/v2` | Gratuita | Indicadores globais (PIB, população, educação) |
| Alpha Vantage | `alphavantage.co` | Chave gratuita | Ações, câmbio, cripto, indicadores técnicos |

### Oficial Brasil (official.py)
| Fonte | API | Autenticação | Dados |
|---|---|---|---|
| IBGE/SIDRA | `servicodados.ibge.gov.br/api/v3` | Gratuita | PNAD, PINTEC, censo, IPCA, séries históricas |
| IPEA/Ipeadata | `ipeadata.gov.br/api` | Gratuita | Séries macroeconômicas, sociais, regionais |
| dados.gov.br | `dados.gov.br/api/3/action` (CKAN) | Gratuita | Catálogo de dados abertos do governo federal |
| Datajud (já existe) | `api-publica.datajud.cnj.us.br` | Chave | Dados processuais TJs estaduais |

### Conhecimento (knowledge.py)
| Fonte | API | Autenticação | Dados |
|---|---|---|---|
| Wikipedia | `wikipedia-api` | Gratuita | Artigos, sumários, categorias |
| Wikidata | `query.wikidata.org/sparql` | Gratuita | Grafos de conhecimento estruturado |
| ConceptNet | `api.conceptnet.io` | Gratuita | Rede semântica de conceitos |
| Google Scholar | `scholarly` | Gratuita (anti-bot frágil) | Citações, artigos, autores |

### Datasets Científicos (datasets.py)
| Fonte | API | Autenticação | Dados |
|---|---|---|---|
| Zenodo | `zenodo.org/api` | Gratuita (token opcional) | 300K+ datasets de pesquisa |
| DataCite | `api.datacite.org` | Gratuita | 30M+ DOIs de dados de pesquisa |
| UCI ML Repo | `archive.ics.uci.edu` | Gratuita | 600+ datasets ML clássicos |
| Figshare | `api.figshare.com/v2` | Gratuita | 3M+ itens de pesquisa |

## Integração com o Ecossistema

```
Consulta do usuário
    │
    ▼
DomainRouter (classifica domínio: financeiro, oficial, conhecimento, dataset)
    │
    ├─ financeiro    → FinancialDataSource (yfinance + BCB + FRED + World Bank)
    ├─ oficial       → OfficialDataSource (IBGE + IPEA + dados.gov.br)
    ├─ conhecimento  → KnowledgeDataSource (Wikipedia + Wikidata + ConceptNet)
    ├─ dataset       → DatasetDataSource (Zenodo + DataCite + UCI + Figshare)
    │
    ▼
Resultado unificado (score, fonte, dados, metadados)
    │
    ▼
LLMReductionLayer (conta como LLM call evitada)
    │
    ▼
Orquestrador (calibra roteamento com confiança baseada em dados reais)
```

## Critérios de Aceitação

- [x] DomainRouter classifica domínio com 46 regras regex em < 1ms
- [x] FinancialDataSource busca cotações (yfinance), séries BCB (SGS), indicadores FRED, World Bank, Alpha Vantage
- [x] OfficialDataSource busca dados IBGE (SIDRA), IPEA (Ipeadata), dados.gov.br (CKAN)
- [x] KnowledgeDataSource busca Wikipedia (pt/en), Wikidata (SPARQL), ConceptNet, Google Scholar
- [x] DatasetDataSource busca datasets em Zenodo, DataCite, UCI, Figshare
- [x] DataKnowledgeHub unifica todas as 16 fontes em interface única
- [x] Integração com LLMReductionLayer como 6º componente
- [x] Cache com TTL por tipo de dado (financeiro: 1h, conhecimento: 24h, dataset: 7d)
- [x] Modo offline com dados mockados para cada uma das 16 fontes

## Métricas Esperadas

| Métrica | Antes | Depois |
|---|---|---|
| Fontes de dados | 16 (só acadêmicas) | 26 (+10 financeiras, oficiais, conhecimento) |
| Domínios cobertos | Apenas acadêmico | Financeiro + Oficial + Conhecimento + Dataset |
| Latência busca federada | N/A (não existia) | < 2s por consulta |
| Chamadas LLM evitadas | ~162/dia | ~200/dia (+38 de busca de dados) |
