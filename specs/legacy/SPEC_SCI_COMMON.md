# SPEC-SCI-031: Science Skills Common
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
a unified HTTP client with rate limiting, retries, and exponential backoff

## Acceptance Criteria
- [x] CT-1: import
- [x] CT-2: http client class exists
- [x] CT-3: http error class exists
- [x] CT-4: http response class exists
- [x] CT-5: instantiated
- [x] CT-6: has base url
- [x] CT-7: has hostname
- [x] CT-8: fetch json returns data
- [x] CT-9: fetch text returns string
- [x] CT-10: fetch bytes returns bytes

## Engine
scripts/test_http_client.py -> against

## Test File
tests/test_http.py
