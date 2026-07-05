# SPEC-AGE-03: Product Manager
Version: 1.0.0 | Status: verified | TDD: verified | Domain: product

## Objective
Product lifecycle decision engine. Evaluates opportunity assessments with RICE scoring, validates roadmap items, calculates sprint health snapshots, and evaluates scope change requests.

## Acceptance Criteria
- [x] CT-1: Opportunity assessment returns BUILD, KILL, EXPLORE, or DEFER based on RICE score
- [x] CT-2: Roadmap item validation rejects missing owner and invalid time horizon
- [x] CT-3: Sprint health calculates velocity, completion percentage, and carried-over tasks
- [x] CT-4: Scope change evaluation decides ACCEPT, REJECT, or DEFER by priority and alignment

## Engine
<scripts/product_manager_engine.py> -> ProductManager

## Test Results
All CTs PASSED
