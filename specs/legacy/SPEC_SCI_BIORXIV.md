# SPEC-SCI-017: bioRxiv / medRxiv Literature Search
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Busca de preprints em ciencias da vida (bioRxiv) e ciencias da saude (medRxiv) via API do Cold Spring Harbor Laboratory

## Acceptance Criteria
- [x] CT-1: available
- [x] CT-2: available is true
- [x] CT-3: search returns dict
- [x] CT-4: search has status
- [x] CT-5: empty input
- [x] CT-6: search by doi returns dict
- [x] CT-7: search by doi has status
- [x] CT-8: search by date returns dict
- [x] CT-9: search by date has status
- [x] CT-10: result has source

## Engine
scripts/biorxiv_client.py -> BiorxivClient

## Test File
tests/test_biorxiv.py
