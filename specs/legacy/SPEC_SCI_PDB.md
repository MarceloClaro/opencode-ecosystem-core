# SPEC-SCI-023: RCSB PDB Database
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Acesso ao Protein Data Bank (RCSB PDB) para busca e download de estruturas 3D de proteinas e acidos nucleicos

## Acceptance Criteria
- [x] CT-1: available
- [x] CT-2: search returns dict
- [x] CT-3: empty query handled
- [x] CT-4: get structure returns dict
- [x] CT-5: search by molecule returns dict
- [x] CT-6: class:TestPDB

## Engine
scripts/pdb_client.py -> PDBClient

## Test File
tests/test_pdb.py
