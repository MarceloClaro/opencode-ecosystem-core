# SPEC-AGE-010: DatabaseOptimizer
Version: 1.0.0 | Status: verified | TDD: verified | Domain: engineering

## Objective
Motor de analise de banco de dados. Analisar schemas SQL, detectar queries N+1, sugerir indices e identificar anti-padroes SQL. Opera offline com Python 3.12 stdlib.

## Acceptance Criteria
- [x] CT-1: `test_ct01_schema_analysis` — analyze_schema identifica >=3 tabelas, detecta type_warnings (ex: TEXT), score 0–100
- [x] CT-2: `test_ct02_n_plus_one_detection` — detect_n_plus_one encontra >=2 ocorrencias em loops com `loop_type` e `suggestion`
- [x] CT-3: `test_ct03_index_suggestions` — suggest_indexes gera DDL com `CREATE INDEX` para colunas em WHERE/JOIN/ORDER BY
- [x] CT-4: `test_ct04_antipattern_detection` — detect_antipatterns encontra `SELECT *` e `ORDER BY RAND()` como anti-padroes

## Engine
<scripts/dboptimizer_engine.py> -> DatabaseOptimizer

## Test Results
All CTs PASSED
