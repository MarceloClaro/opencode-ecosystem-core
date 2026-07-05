# SPEC-BRO-CTE: Content Engine
Version: 1.0.0 | Domain: broomva

## Objective
Full-stack AI content studio orchestrating visual DNA compilation, cinematic generation, browser-automated tool execution, and multi-platform distribution into a unified content pipeline. Tests validate the compile-dna.py and compose-video.py scripts.

## Acceptance Criteria
- [x] CT-1: SKILL.md with complete frontmatter (name, category, version, kind)
- [x] CT-2: category: broomva declared
- [x] CT-3: compile-dna.py imports and key functions exist (discover_entities, compile_brand, compile_character, compile_style, run_lint, hash_file)
- [x] CT-4: compose-video.py imports and key functions exist (parse_storyboard, load_brand_dna, inject_brand_into_prompt, write_manifest, stitch_clips)
- [x] CT-5: compile-dna.py hash_file produces deterministic SHA-256
- [x] CT-6: compile-dna.py discover_entities detects test directory structure
- [x] CT-7: compose-video.py parse_storyboard returns correct shot count

## Test File
skills/broomva/content-engine/tests/test_content_engine.py

## Engine
scripts/compile-dna.py, scripts/compose-video.py
