# SPEC-SCI-026: PubChem Database
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
API PubChem para consulta de compostos quimicos, bioatividades, estruturas moleculares e propriedades

## Acceptance Criteria
- [x] CT-1: available
- [x] CT-2: search returns dict
- [x] CT-3: empty query handled
- [x] CT-4: search by cid returns dict
- [x] CT-5: search bioactivities returns dict
- [x] CT-6: class:TestPubChem

## Engine
scripts/pubchem_client.py -> PubChemClient

## Test File
tests/test_pubchem.py
