# SPEC-SCI-024: Protein Sequence Msa
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Performs multiple sequence alignment of proteins with EBI Clustal Omega

## Acceptance Criteria
- [x] CT-1: prepare payload returns bytes
- [x] CT-2: prepare payload contains email
- [x] CT-3: prepare payload contains sequences
- [x] CT-4: importable
- [x] CT-5: class:TestMSAPayload
- [x] CT-6: class:TestMSAConstants

## Engine
scripts/msa_align.py

## Test File
tests/test_msa.py
