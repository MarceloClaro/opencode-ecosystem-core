# SPEC-SCI-029: Quickgo Database
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Query the QuickGO and Evidence & Conclusion Ontology (ECO) REST API. Use this

## Acceptance Criteria
- [x] CT-1: make request go search
- [x] CT-2: make request returns list or dict
- [x] CT-3: make request bad input handles error
- [x] CT-4: base url
- [x] CT-5: module has search functions
- [x] CT-6: class:TestQuickGOMakeRequest
- [x] CT-7: class:TestQuickGOConstants

## Engine
scripts/quickgo_tool.py

## Test File
tests/test_quickgo.py
