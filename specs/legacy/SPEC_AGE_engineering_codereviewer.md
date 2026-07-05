# SPEC-AGE-006: CodeReviewer
Version: 1.0.0 | Status: verified | TDD: verified | Domain: engineering

## Objective
Motor de revisao de codigo baseado em regras. Analisar codigo-fonte para detectar code smells, complexidade excessiva, padroes inseguros e duplicacao. Opera offline com Python 3.12 stdlib.

## Acceptance Criteria
- [x] CT-1: `test_ct01_cyclomatic_complexity` — Detecta funcao `calculate_total` excedendo COMPLEXITY_THRESHOLD em analyze_complexity
- [x] CT-2: `test_ct02_code_smells` — detect_smells identifica `god_function` ou `too_many_params` e `short_name`
- [x] CT-3: `test_ct03_security_issues` — detect_security_issues encontra `eval`, `os.system`, e `secret`/hardcoded com critical_count > 0
- [x] CT-4: `test_ct04_duplication` — detect_duplication identifica blocos duplicados com similarity >= 1.0 e lines >= 5

## Engine
<scripts/codereviewer_engine.py> -> CodeReviewer

## Test Results
All CTs PASSED
