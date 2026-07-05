# SPEC-SCI-014: InterPro Database
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Classificacao de familias e dominios proteicos via API InterPro (assinaturas Pfam, PROSITE, SMART, etc.)

## Acceptance Criteria
- [x] CT-1: available
- [x] CT-2: search returns dict
- [x] CT-3: empty query handled
- [x] CT-4: search by accession returns dict
- [x] CT-5: search by protein returns dict
- [x] CT-6: class:TestInterPro

## Engine
scripts/interpro_client.py -> InterProClient

## Test File
tests/test_interpro.py
