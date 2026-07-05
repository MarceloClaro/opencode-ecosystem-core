# SPEC-AGE-002: GeographerEngine
Version: 1.0.0 | Status: verified | TDD: verified | Domain: academic

## Objective
Agente geografo para validacao de geografia fisica em worldbuilding. Verifica consistencia climatica (Koppen), leis hidrologicas (rios nao bifurcam, fluxo declive abaixo), e viabilidade de assentamentos.

## Acceptance Criteria
- [x] CT-1: `test_geography_coherence_returns_report` — GeoReport retornado com region_name extraido e score float
- [x] CT-2: `test_river_doesnt_split` — Detecta bifurcacao de rio como violacao hidrologica
- [x] CT-3: `test_climate_latitude_rule_tropical` — Latitude 5.0 + coastal classifica como zona tropical valida
- [x] CT-4: `test_settlement_requires_water` — Assentamento sem fonte de agua marcado como inviavel com `freshwater` em `requirements_unmet`

## Engine
<scripts/geographer_engine.py> -> GeographerEngine

## Test Results
All CTs PASSED
