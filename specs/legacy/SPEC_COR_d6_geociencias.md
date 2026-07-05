# SPEC-COR-D6: Geociencias e Modelagem Climatica (CORA-Eval)
Version: 1.0.0 | Status: verified | TDD: verified

## Objective
Suite TDD para D6 do CORA-Eval — classificacao de rochas, conversao de temperatura e camadas atmosfericas.

## Acceptance Criteria
- [x] CT-1 (N1-01): Classificacao de Rochas — Granito (ignea intrusiva), Basalto (ignea extrusiva), Calcario (sedimentar quimica), Marmore (metamorfica nao foliada), ciclo das 3 familias representado
- [x] CT-2 (N1-02): Conversao de Temperatura — 0C=273.15K, 373.15K=100C, 100C=212F, 32F=0C, roundtrip K<->C consistente
- [x] CT-3 (N1-03): Camadas Atmosfericas — 5km=Troposfera, 30km=Estratosfera, 70km=Mesosfera, 400km(ISS)=Termosfera, 12km(tropopausa)=Estratosfera

## Test File
tests/test_d6_geociencias.py
