# SPEC-SCI-025: Protein Sequence Similarity Search
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Searches for homologous protein sequences using MMseqs2 (fast, default) or

## Acceptance Criteria
- [x] CT-1: fasta columns
- [x] CT-2: parse a3m empty
- [x] CT-3: parse a3m with hits
- [x] CT-4: allowed databases
- [x] CT-5: human database available
- [x] CT-6: class:TestMMseqs2Parse
- [x] CT-7: class:TestBlastConstants

## Engine
scripts/ -> mmseqs2_search.py, uniprot_blast.py

## Test File
tests/test_similarity.py
