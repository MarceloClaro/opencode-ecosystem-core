# SPEC-SCI-020: Ncbi Sequence Fetch
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Retrieve protein and nucleotide sequences from NCBI databases using

## Acceptance Criteria
- [x] CT-1: parse single entry
- [x] CT-2: parse multiple entries
- [x] CT-3: parse empty returns empty list
- [x] CT-4: translate simple sequence
- [x] CT-5: translate longer sequence
- [x] CT-6: translate with unknown codon
- [x] CT-7: translate short sequence
- [x] CT-8: efetch returns fasta or none
- [x] CT-9: esearch returns tuple
- [x] CT-10: class:TestParseFasta

## Engine
scripts/ncbi_fetch.py

## Test File
tests/test_ncbi_fetch.py
