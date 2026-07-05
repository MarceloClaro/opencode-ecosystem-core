# SPEC-SCI-013: Human Protein Atlas Database
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Use when you want to retrieve semi-quantitative protein expression and

## Acceptance Criteria
- [x] CT-1: import hpa cli
- [x] CT-2: base url search defined
- [x] CT-3: base url xml defined
- [x] CT-4: client instantiated
- [x] CT-5: resolve ensembl id
- [x] CT-6: search hpa
- [x] CT-7: get subcellular location
- [x] CT-8: search unknown returns empty
- [x] CT-9: class:TestHPAImports
- [x] CT-10: class:TestHPAClient

## Engine
scripts/hpa_cli.py

## Test File
tests/test_hpa.py
