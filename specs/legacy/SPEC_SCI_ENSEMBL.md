# SPEC-SCI-009: Ensembl Genome Browser
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
API do Ensembl para consulta de genomas anotados: genes, transcritos, variantes e homologia comparativa

## Acceptance Criteria
- [x] CT-1: available
- [x] CT-2: search returns dict
- [x] CT-3: empty query handled
- [x] CT-4: get gene returns dict
- [x] CT-5: get variant returns dict
- [x] CT-6: class:TestEnsembl

## Engine
scripts/ensembl_client.py -> EnsemblClient

## Test File
tests/test_ensembl.py
