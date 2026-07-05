# SPEC-AGE-003: HistorianEngine
Version: 1.0.0 | Status: verified | TDD: verified | Domain: academic

## Objective
Agente historiador para validacao de autenticidade historica em worldbuilding. Detecta anacronismos com >85% de precisao, corrige mitos historicos populares, e avalia claims com contra-evidencia.

## Acceptance Criteria
- [x] CT-1: `test_potatoes_in_pre_columbian_europe` — Detecta batatas na Europa medieval como anacronismo high/medium severity
- [x] CT-2: `test_period_authenticity_report_medieval` — Relatorio `medieval_europe` tem confidence_level `high` e lista `known_unavailable`
- [x] CT-3: `test_claim_evaluation_returns_structure` — evaluate_claim retorna `verdict`, `confidence`, `claim`
- [x] CT-4: `test_confidence_levels_stated` — Todo finding de anacronismo tem `confidence` float no intervalo 0.0–1.0

## Engine
<scripts/historian_engine.py> -> HistorianEngine

## Test Results
All CTs PASSED
