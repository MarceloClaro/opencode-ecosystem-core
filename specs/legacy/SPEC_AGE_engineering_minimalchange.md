# SPEC-AGE-007: MinimalChangeEngine
Version: 1.0.0 | Status: verified | TDD: verified | Domain: engineering

## Objective
Motor de validacao de diffs minimos. Analisar patches/diffs para detectar scope creep, refatoracoes prematuras e mudancas cosmeticas desnecessarias. Opera offline com Python 3.12 stdlib.

## Acceptance Criteria
- [x] CT-1: `test_ct01_scope_check` — check_scope detecta arquivos fora do escopo declarado e valida quando escopo cobre todos os arquivos
- [x] CT-2: `test_ct02_premature_refactor_detection` — detect_premature_refactor identifica renames `get_all` e `process` como suspeitos
- [x] CT-3: `test_ct03_diff_entropy` — measure_entropy reporta files_changed=3, hunks_count>0, lines_added/removed>0, entropy_score 0–100
- [x] CT-4: `test_ct04_change_ratio` — validate_change_ratio distingue functional_changes de cosmetic_changes com ratio 0.0–1.0

## Engine
<scripts/minimalchange_engine.py> -> MinimalChangeEngine

## Test Results
All CTs PASSED
