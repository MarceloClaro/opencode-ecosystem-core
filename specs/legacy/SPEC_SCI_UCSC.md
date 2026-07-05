# SPEC-SCI-033: Ucsc Conservation And Tfbs
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Fetch Evolutionary Conservation scores (phyloP, phastCons) and Transcription

## Acceptance Criteria
- [x] CT-1: import get conservation
- [x] CT-2: ucsc api url defined
- [x] CT-3: client instantiated
- [x] CT-4: parse coordinate valid
- [x] CT-5: parse coordinate single pos
- [x] CT-6: parse coordinate invalid raises
- [x] CT-7: get conservation data returns dict
- [x] CT-8: get conservation data has track keys
- [x] CT-9: import get tfbs
- [x] CT-10: client instantiated

## Engine
scripts/ -> get_conservation.py, get_tfbs.py, list_tracks.py

## Test File
tests/test_ucsc.py
