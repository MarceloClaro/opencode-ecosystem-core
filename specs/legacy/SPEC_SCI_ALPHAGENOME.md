# SPEC-SCI-002: Alphagenome Single Variant Analysis
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Analyzes genetic variant effects on gene expression (RNA-seq), chromatin

## Acceptance Criteria
- [x] CT-1: standard bases
- [x] CT-2: mixed case
- [x] CT-3: empty string
- [x] CT-4: simple text
- [x] CT-5: special characters
- [x] CT-6: short words filtered
- [x] CT-7: exact match
- [x] CT-8: no match
- [x] CT-9: empty query
- [x] CT-10: class:TestReverseComplement

## Engine
scripts/analyze_ism.py -> ColoredSashimi

## Test File
tests/test_alphagenome.py
