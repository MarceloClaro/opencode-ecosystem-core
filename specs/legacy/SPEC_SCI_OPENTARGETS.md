# SPEC-SCI-022: Open Targets Database
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
API Open Targets Platform para associacoes entre alvos terapeuticos, doencas e farmacos com evidencias curadas

## Acceptance Criteria
- [x] CT-1: available
- [x] CT-2: search returns dict
- [x] CT-3: empty query handled
- [x] CT-4: search by disease returns dict
- [x] CT-5: search results has status
- [x] CT-6: class:TestOpenTargets

## Engine
scripts/opentargets_client.py -> OpenTargetsClient

## Test File
tests/test_opentargets.py
