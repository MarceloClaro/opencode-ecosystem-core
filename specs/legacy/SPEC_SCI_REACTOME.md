# SPEC-SCI-030: Reactome Database
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
API Reactome para consulta de vias biologicas, reacoes bioquimicas e interacoes moleculares curadas manualmente

## Acceptance Criteria
- [x] CT-1: available
- [x] CT-2: search returns dict
- [x] CT-3: empty query handled
- [x] CT-4: search by gene returns dict
- [x] CT-5: get pathway details returns dict
- [x] CT-6: class:TestReactome

## Engine
scripts/reactome_client.py -> ReactomeClient

## Test File
tests/test_reactome.py
