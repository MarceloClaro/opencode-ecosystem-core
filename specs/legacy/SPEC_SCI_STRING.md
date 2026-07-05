# SPEC-SCI-032: STRING Database
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
API STRING para consulta de redes de interacao proteina-proteina com scores de confianca e anotacoes funcionais

## Acceptance Criteria
- [x] CT-1: available
- [x] CT-2: available is true
- [x] CT-3: search returns dict
- [x] CT-4: search has status
- [x] CT-5: empty input
- [x] CT-6: empty input error
- [x] CT-7: search interactions returns dict
- [x] CT-8: search interactions has status
- [x] CT-9: result has source
- [x] CT-10: class:TestStringClient

## Engine
scripts/string_client.py -> StringClient

## Test File
tests/test_string.py
