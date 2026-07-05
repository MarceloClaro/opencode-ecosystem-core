# SPEC-SCI-006: NCBI dbSNP Database
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Consulta a base NCBI dbSNP para identificacao de variantes geneticas por rs IDs e anotacoes associadas

## Acceptance Criteria
- [x] CT-1: available
- [x] CT-2: search returns dict
- [x] CT-3: empty query handled
- [x] CT-4: get variant returns dict
- [x] CT-5: search by gene returns dict
- [x] CT-6: class:TestDbSNP

## Engine
scripts/dbsnp_client.py -> DbSNPClient

## Test File
tests/test_dbsnp.py
