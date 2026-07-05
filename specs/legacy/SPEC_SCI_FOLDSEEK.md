# SPEC-SCI-010: Foldseek Structural Search
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Performs 3D structural searches of proteins against various databases (PDB,

## Acceptance Criteria
- [x] CT-1: allowed databases not empty
- [x] CT-2: max alignment hits
- [x] CT-3: build multipart payload returns bytes
- [x] CT-4: build multipart missing file
- [x] CT-5: class:TestFoldseekConstants
- [x] CT-6: class:TestFoldseekPayload

## Engine
scripts/search.py

## Test File
tests/test_foldseek.py
