# SPEC-BRO-SCI: Social Intelligence
Version: 1.0.0 | Domain: broomva

## Objective
Autonomous social engagement + knowledge extraction loop for Moltbook and X/Twitter. Tests validate the engagement-loop.py decode_challenge verifier, scoring engine, and x_browser.py marketing-shape detector.

## Acceptance Criteria
- [x] CT-1: SKILL.md with complete frontmatter
- [x] CT-2: category: broomva declared
- [x] CT-3: engagement-loop.py decode_challenge solves known challenges correctly
- [x] CT-4: engagement-loop.py score_comment returns {novelty, specificity, relevance, total, promote}
- [x] CT-5: x_browser.py check_marketing_shape blocks proprietary nouns
- [x] CT-6: x_browser.py check_marketing_shape passes non-proprietary text
- [x] CT-7: x_twikit.py rate gate prevents exceeding write cap

## Test File
skills/broomva/social-intelligence/tests/test_social_intelligence.py

## Engine
scripts/engagement-loop.py, scripts/x_browser.py, scripts/x_twikit.py
