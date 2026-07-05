# SPEC-TOP-DC: Data Collector Pipeline
Version: 1.0.0 | Domain: top-level | Status: active

## Objective
Coleta dados reais de APIs públicas (World Bank, IBGE) para calibrar simulacoes do ecossistema OpenCode. Gera DataFrames estruturados, correlacoes de Pearson, e cache local SQLite com fontes auditaveis.

## Architecture
```
World Bank API ←→ DataCollector.fetch_world_bank() ←→ SQLite Cache (wb_cache + fetch_log)
IBGE/PNAD     ←→ DataCollector.build_dataframe()   ←→ Correlation Engine
                                                         ↓
                                              Brazil Summary Report
```

## Data Sources
| Source | Indicators | Access |
|--------|-----------|--------|
| World Bank API | 23 (GDP, Gini, education, health, R&D, environment) | Public, no auth |
| IBGE/PNAD | 5 (population, urbanization, literacy, income, racial inequality) | Fixed values |

## Acceptance Criteria
- [x] CT-1: DataCollector init with custom SQLite path, World Bank indicators registry (23+), IBGE registry (5+)
- [x] CT-2: build_dataframe() returns structured dict with years + indicator columns
- [x] CT-3: get_brazil_summary() returns country, period, sources, indicators with trend (up/down/stable)
- [x] CT-4: compute_correlations() returns Pearson r with strength classification (forte/moderada/fraca)
- [x] CT-5: SQLite cache tables (wb_cache, fetch_log) created on init
- [x] CT-6: Graceful degradation when API offline (returns empty list, no crash)
- [x] CT-7: build_dataframe() resilient even without network
- [x] CT-8: Module importable without side effects

## Scripts
| File | Lines | Function |
|------|-------|----------|
| data_collector.py | ~300 | Core engine (DataCollector class) |
| causal_inference.py | ~400 | Granger causality + cross-correlation |
| monte_carlo.py | ~450 | Sobol-like sensitivity analysis |
| citation_finder.py | ~400 | Academic citation search |
| report_generator.py | ~1000 | Report generation |
| whatsapp_profiler.py | ~1100 | WhatsApp profile extraction |
| whatsapp_service.py | ~600 | WhatsApp service integration |

## Test Coverage
- Location: `skills/data-collector/tests/test_data_collector.py`
- Classes: 4 (Init, Methods, Cache, Available)
- Tests: 12+
