# SPEC-AGE-004: NarratologistEngine
Version: 1.0.0 | Status: verified | TDD: verified | Domain: academic

## Objective
Agente narratologo para analise estrutural de narrativas em worldbuilding. Identifica ideia controladora (McKee), avalia arcos de personagem (want/need/lie), classifica estrutura narrativa e verifica convencoes de genero.

## Acceptance Criteria
- [x] CT-1: `test_controlling_idea_found_explicit` — Extrai ideia controladora de texto com `theme: ...` explicito
- [x] CT-2: `test_character_has_want_need_lie` — assess_character retorna `want`, `need`, `lie` nao vazios
- [x] CT-3: `test_structure_identified_hero_journey` — Detecta estrutura Hero's Journey com `structure_type` nao nulo
- [x] CT-4: `test_genre_conventions_tragedy` — check_genre_conventions para `tragedy` retorna `required_conventions_met` e `adherence_score`

## Engine
<scripts/narratologist_engine.py> -> NarratologistEngine

## Test Results
All CTs PASSED
