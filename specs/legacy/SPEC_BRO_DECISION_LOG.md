# SPEC-BRO-DLG: Decision Log
Version: 1.0.0 | Domain: broomva

## Objective
Captures a decision with context, alternatives considered, and rationale, then links it to the relevant project doc in the vault. Creates a searchable decision record.

## Acceptance Criteria
- [x] CT-1: SKILL.md exists with complete YAML frontmatter
- [x] CT-2: category: broomva declared
- [x] CT-3: version field present
- [x] CT-4: kind field present
- [x] CT-5: Frontmatter has description field with decision-log workflow references

## Test File
skills/broomva/tests/test_decision_log.py
