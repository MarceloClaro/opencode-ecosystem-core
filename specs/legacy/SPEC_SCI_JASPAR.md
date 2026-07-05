# SPEC-SCI-015: Jaspar Database
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Query the JASPAR database for Transcription Factor (TF) binding profiles

## Acceptance Criteria
- [x] CT-1: import jaspar api
- [x] CT-2: jaspar url defined
- [x] CT-3: client instantiated
- [x] CT-4: valid formats defined
- [x] CT-5: validate matrix id valid
- [x] CT-6: validate matrix id invalid raises
- [x] CT-7: dict to yaml returns string
- [x] CT-8: dict to yaml with list
- [x] CT-9: class:TestJASPARImports
- [x] CT-10: class:TestJASPARClient

## Engine
scripts/jaspar_api.py

## Test File
tests/test_jaspar.py
