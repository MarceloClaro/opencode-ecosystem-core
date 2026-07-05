# SPEC-SCI-003: Chembl Database
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Query the ChEMBL database for bioactive molecules, drug targets, bioactivity

## Acceptance Criteria
- [x] CT-1: build url molecule search
- [x] CT-2: build url with resource id
- [x] CT-3: normalize activity valid nm
- [x] CT-4: normalize activity converts um
- [x] CT-5: unit conversion table
- [x] CT-6: molecule is searchable
- [x] CT-7: endpoint map entries
- [x] CT-8: class:TestChemblBuild
- [x] CT-9: class:TestChemblNormalize
- [x] CT-10: class:TestChemblConstants

## Engine
scripts/chembl_api.py

## Test File
tests/test_chembl.py
