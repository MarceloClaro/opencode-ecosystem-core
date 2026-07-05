# SPEC-SCI-012: GTEx Database
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Consulta ao Genotype-Tissue Expression (GTEx) para dados de expressao genica tecido-especifica

## Acceptance Criteria
- [x] CT-1: available
- [x] CT-2: search returns dict
- [x] CT-3: empty query handled
- [x] CT-4: get median expression returns dict
- [x] CT-5: get isoform expression returns dict
- [x] CT-6: class:TestGTEx

## Engine
scripts/gtex_client.py -> GTExClient

## Test File
tests/test_gtex.py
