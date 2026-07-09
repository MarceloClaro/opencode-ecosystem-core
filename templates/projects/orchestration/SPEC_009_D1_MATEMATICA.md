---
spec_id: SPEC-009
title: "Suite D1 — Raciocinio Matematico Formal"
version: "1.0"
tdd_suite: "evaluations/tests/test_d1_matematica.py"
dependencies: [SPEC-001]
ct_count: 8
---

# SPEC-009 — Suite D1

## Objetivo
Criar suite TDD para D1 (Raciocinio Matematico Formal), unica dimensao
em N4 sem teste automatizado proprio (depende apenas do teste exaustivo).

## CTs

| CT | Descricao | Tipo |
|:--:|-----------|:----:|
| D1-1 | Teorema de Pitagoras — prova algebrica verifica identidade a²+b²=c² | Algebra |
| D1-2 | Soma de Gauss — n(n+1)/2 verificado para n=1..1000 | Series |
| D1-3 | Fatorial — definicao recursiva confere com math.factorial ate 20 | Recursao |
| D1-4 | Fibonacci — formula fechada de Binet confere com iteracao ate n=30 | Sequencias |
| D1-5 | Numeros primos — crivo de Eratostenes bate com lista conhecida ate 100 | Teoria dos Numeros |
| D1-6 | MDC — algoritmo de Euclides confere com math.gcd para 1000 pares | Teoria dos Numeros |
| D1-7 | Identidade trigonometrica — sin²θ+cos²θ=1 para 1000 angulos aleatorios | Trigonometria |
| D1-8 | Derivada — (x^n)' = n·x^(n-1) via definicao de limite com h=1e-7 | Calculo |
