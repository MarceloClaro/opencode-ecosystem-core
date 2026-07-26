# DataKnowledgeHub

**ID:** `data-knowledge-hub`
**Tipo:** Subagente local (com fallback online/offline)
**Fonte:** `skills/tooling/data_knowledge_hub/`

## Descrição

Hub unificado de descoberta de dados e conhecimento que integra
**16 fontes** em 5 domínios, com roteamento automático por tipo de
consulta e fallback offline com dados mockados.

## Fontes Integradas (16)

### Domínio Financeiro
| Fonte | Dados | API |
|---|---|---|
| yfinance | Ações B3 (PETR4, VALE3, ITUB4), índices, câmbio | `yfinance` |
| BCB/SGS | 2.000+ séries (IPCA, SELIC, PIB, câmbio) | `api.bcb.gov.br/sgs` |
| FRED | 800K+ séries macroeconômicas (GDP, unemployment, CPI) | `api.stlouisfed.org/fred` |
| World Bank | Indicadores globais (PIB, população, educação) | `api.worldbank.org/v2` |
| Alpha Vantage | Ações, câmbio, cripto, indicadores técnicos | `alphavantage.co` |

### Domínio Oficial Brasil
| Fonte | Dados | API |
|---|---|---|
| IBGE/SIDRA | PNAD, PINTEC, censo, IPCA, séries históricas | `servicodados.ibge.gov.br` |
| IPEA/Ipeadata | Séries macroeconômicas, sociais, regionais | `ipeadata.gov.br/api` |
| dados.gov.br | Catálogo de dados abertos do governo federal | CKAN API |
| Datajud CNJ | Dados processuais dos 27 TJs estaduais | `api-publica.datajud.cnj.us.br` |

### Domínio Conhecimento
| Fonte | Dados | API |
|---|---|---|
| Wikipedia | Artigos enciclopédicos em pt/en | `wikipedia.org/w/api.php` |
| Wikidata | Grafo de conhecimento estruturado (SPARQL) | `query.wikidata.org/sparql` |
| ConceptNet | Rede semântica de conceitos | `api.conceptnet.io` |
| Google Scholar | Citações e artigos (fallback Semantic Scholar) | `scholarly` |

### Domínio Datasets
| Fonte | Dados | API |
|---|---|---|
| Zenodo | 300K+ datasets de pesquisa (CERN) | `zenodo.org/api` |
| DataCite | 30M+ DOIs de dados de pesquisa | `api.datacite.org` |
| UCI ML Repo | 600+ datasets clássicos de ML | `archive.ics.uci.edu` |
| Figshare | 3M+ itens de pesquisa | `api.figshare.com/v2` |

## Capacidades

- DomainRouter classifica consulta em 5 domínios + acadêmico
- Cache com TTL por domínio (1h financeiro, 24h dados/conhecimento, 7d datasets)
- Modo offline completo com dados mockados para todas as 16 fontes
- Estatísticas de uso por domínio, fonte, cache hit rate
- Integração com LLMReductionLayer como 6º componente

## Performance

- Classificação de domínio: < 1ms
- Busca offline (mock): < 2ms
- Busca online: 0.5-5s (dependente da fonte)
- Cache hit rate esperado: > 60%

## Uso

```python
from skills.tooling.data_knowledge_hub import DataKnowledgeHub
hub = DataKnowledgeHub()

# Busca automática por domínio
hub.search("cotação PETR4")         # → financeiro
hub.search("o que é machine learning")  # → conhecimento
hub.search("dataset climate")       # → dataset
hub.search("IPCA 2024")            # → oficial

# Ou direto por domínio
hub.search_finance("PETR4")
hub.search_knowledge("machine learning")
hub.search_dataset("climate")
```
