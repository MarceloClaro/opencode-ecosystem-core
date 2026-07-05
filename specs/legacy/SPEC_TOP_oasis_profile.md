# SPEC-TOP-011: OASIS Profile Generator
Version: 1.0.0 | Domain: simulation

## Objective
Geracao de perfis de agente IA a partir de entidades de grafo de conhecimento. Inspirado pelo OASIS Profile Generator do MiroFish-Offline. Schema validation, fallback heuristico, rastreabilidade por campo.

## Acceptance Criteria
- [x] CT-1: Heuristic profile has all required fields
- [x] CT-2: Valid profile passes validation
- [x] CT-3: Missing fields trigger validation errors
- [x] CT-4: Simulation config generated from profiles

## Assets
- scripts/generate_profiles.py
- tests/test_oasis_profile_gen.py
