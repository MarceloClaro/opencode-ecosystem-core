# SPEC-SCI-019: Literature Search Openalex
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Query the OpenAlex scholarly database for research papers, authors,

## Acceptance Criteria
- [x] CT-1: valid short id
- [x] CT-2: valid openalex url
- [x] CT-3: valid doi url
- [x] CT-4: invalid entity id
- [x] CT-5: build url without api key
- [x] CT-6: build url with api key
- [x] CT-7: entity types
- [x] CT-8: base url
- [x] CT-9: class:TestOpenAlexValidation
- [x] CT-10: class:TestOpenAlexUtils

## Engine
scripts/openalex_cli.py

## Test File
tests/test_openalex.py
