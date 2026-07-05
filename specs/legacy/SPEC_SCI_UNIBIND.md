# SPEC-SCI-034: Unibind Database
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Queries the UniBind database for experimentally validated transcription factor

## Acceptance Criteria
- [x] CT-1: import unibind api
- [x] CT-2: api prefix defined
- [x] CT-3: client instantiated
- [x] CT-4: make request function exists
- [x] CT-5: write output function exists
- [x] CT-6: make request returns data
- [x] CT-7: make request has results
- [x] CT-8: list species returns dict
- [x] CT-9: list collections returns dict
- [x] CT-10: list tfs returns dict

## Engine
scripts/unibind_api.py

## Test File
tests/test_unibind.py
