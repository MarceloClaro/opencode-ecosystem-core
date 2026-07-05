# SPEC-SCI-037: Workflow Skill Creator
Version: 1.0.0 | Status: verified | TDD: verified | Domain: science

## Objective
Distills a completed user workflow or interaction into a reusable agent

## Acceptance Criteria
- [x] CT-1: available
- [x] CT-2: available is true
- [x] CT-3: generate method returns dict
- [x] CT-4: generate has status
- [x] CT-5: generate has skill name
- [x] CT-6: generate has skill md
- [x] CT-7: generate has script py
- [x] CT-8: generate has timestamp
- [x] CT-9: generate with custom params
- [x] CT-10: skill md contains title

## Engine
scripts/skill_generator.py -> SkillGenerator

## Test File
tests/test_skill_gen.py
