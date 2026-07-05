# SPEC-AGE-04: Sprint Prioritizer
Version: 1.0.0 | Status: verified | TDD: verified | Domain: product

## Objective
Agile sprint prioritization engine. Calculates RICE scores, performs MoSCoW classification, plans sprint capacity with buffers, and resolves task dependency ordering.

## Acceptance Criteria
- [x] CT-1: RICE score calculation validates negative reach and zero effort inputs
- [x] CT-2: MoSCoW classification assigns Must Have, Should Have, Could Have, Won't Have
- [x] CT-3: Sprint capacity planning computes effective capacity with buffer and max commitment
- [x] CT-4: Dependency resolution performs topological sort and rejects circular dependencies

## Engine
<scripts/sprint_prioritizer_engine.py> -> SprintPrioritizer

## Test Results
All CTs PASSED
