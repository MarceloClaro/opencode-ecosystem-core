# SPEC-SCI-008: Encode Ccres Database
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Query the ENCODE Registry of cis-Regulatory Elements (cCREs) via the SCREEN

## Acceptance Criteria
- [x] CT-1: import encode portal api
- [x] CT-2: base url defined
- [x] CT-3: client instantiated
- [x] CT-4: cmd search function exists
- [x] CT-5: import screen api
- [x] CT-6: api url defined
- [x] CT-7: client instantiated
- [x] CT-8: run query function exists
- [x] CT-9: cmd search function exists
- [x] CT-10: cmd nearby function exists

## Engine
scripts/ -> encode_portal_api.py, screen_api.py

## Test File
tests/test_encode.py
