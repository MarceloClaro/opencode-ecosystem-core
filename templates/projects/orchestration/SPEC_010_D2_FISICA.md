---
spec_id: SPEC-010
title: "Suite D2 — Modelagem de Sistemas Fisicos"
version: "1.0"
tdd_suite: "evaluations/tests/test_d2_fisica.py"
dependencies: [SPEC-001]
ct_count: 8
---

# SPEC-010 — Suite D2

## Objetivo
Criar suite TDD para D2 (Modelagem de Sistemas Fisicos), atualmente
em N4 mas sem teste automatizado proprio.

## CTs

| CT | Descricao | Tipo |
|:--:|-----------|:----:|
| D2-1 | MRU — x = x₀ + v·t, verificar com 100 valores aleatorios de t | Cinematica |
| D2-2 | Queda livre — y = (1/2)g·t², erro < 1% vs integracao numerica | Dinamica |
| D2-3 | Conservacao de energia — E_ini = E_fin para pendulo simples | Conservacao |
| D2-4 | Analise dimensional — verificar que [F]=MLT⁻² em F=ma | V1 Dimensional |
| D2-5 | Lei de Hooke — F = -k·x, linearidade R² > 0.999 | Elasticidade |
| D2-6 | Periodo pendulo — T = 2π√(L/g), 5 valores de L verificados | Oscilacoes |
| D2-7 | Conservacao momento — m1v1+m2v2 = constante em colisao elastica | Conservacao |
| D2-8 | Lei dos gases — PV = nRT, 10 pontos PV vs T com R² > 0.99 | Termodinamica |
