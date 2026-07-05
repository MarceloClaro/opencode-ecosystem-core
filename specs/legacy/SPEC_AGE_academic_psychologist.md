# SPEC-AGE-005: PsychologistEngine
Version: 1.0.0 | Status: verified | TDD: verified | Domain: academic

## Objective
Agente psicologo para perfilagem de personagens ficticios usando Big Five (OCEAN) + teoria do apego + hierarquia de defesas de Vaillant. Inclui disclaimer anti-diagnostico e analise de dinamicas relacionais.

## Acceptance Criteria
- [x] CT-1: `test_big_five_profile_returns_all_five` — Todos os 5 traços (openness, conscientiousness, extraversion, agreeableness, neuroticism) com `direction` e `percentile`
- [x] CT-2: `test_attachment_style_detected_anxious` — Detecta apego ansioso com keywords de abandono e reassurance
- [x] CT-3: `test_defense_mechanism_identified_denial` — Identifica `denial` como mecanismo de defesa com `confidence` e `evidence`
- [x] CT-4: `test_not_reduced_to_diagnosis` — profile_character inclui `disclaimer` contendo aviso anti-diagnostico

## Engine
<scripts/psychologist_engine.py> -> PsychologistEngine

## Test Results
All CTs PASSED
