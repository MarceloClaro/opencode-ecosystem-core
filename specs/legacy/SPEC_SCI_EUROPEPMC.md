# SPEC-SCI-018: Europe PMC Literature Search
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Acesso a API Europe PMC para busca de literatura biomedica, artigos completos e datasets suplementares

## Acceptance Criteria
- [x] CT-1: client instantiated
- [x] CT-2: base url set
- [x] CT-3: search returns dict
- [x] CT-4: search has hit count
- [x] CT-5: empty input handled
- [x] CT-6: fetch article returns dict
- [x] CT-7: fetch references returns dict
- [x] CT-8: fetch citations returns dict
- [x] CT-9: fetch grants returns dict
- [x] CT-10: search result type core

## Engine
scripts/europepmc_client.py -> EuropePMCClient

## Test File
tests/test_europepmc.py
