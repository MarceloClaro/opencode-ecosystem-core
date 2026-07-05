# SPEC-SCI-035: Uniprot Database
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Access protein metadata, function, taxonomy, and sequences across UniProtKB,

## Acceptance Criteria
- [x] CT-1: add params to url simple
- [x] CT-2: add params to url no params
- [x] CT-3: add params to url already has params
- [x] CT-4: get count returns int
- [x] CT-5: get entry returns data
- [x] CT-6: search proteins yields results
- [x] CT-7: class:TestUniProtUtils
- [x] CT-8: class:TestUniProtCount
- [x] CT-9: class:TestUniProtEntry

## Engine
scripts/uniprot_tools.py -> UniProtError

## Test File
tests/test_uniprot.py
