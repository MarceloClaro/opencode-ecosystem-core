# SPEC-SCI-011: gnomAD Database
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Acesso ao Genome Aggregation Database (gnomAD) para frequencias populacionais de variantes geneticas

## Acceptance Criteria
- [x] CT-1: available
- [x] CT-2: search returns dict
- [x] CT-3: empty query handled
- [x] CT-4: search by gene returns dict
- [x] CT-5: search by rsid returns dict
- [x] CT-6: class:TestGnomAD

## Engine
scripts/gnomad_client.py -> GnomADClient

## Test File
tests/test_gnomad.py
