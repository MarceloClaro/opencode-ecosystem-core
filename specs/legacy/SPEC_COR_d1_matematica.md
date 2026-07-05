# SPEC-COR-D1: Raciocinio Matematico Formal (CORA-Eval)
Version: 1.0.0 | Status: verified | TDD: verified

## Objective
Suite TDD para D1 do CORA-Eval — validacao de raciocinio matematico formal em 8 dominios classicos.

## Acceptance Criteria
- [x] CT-1: Teorema de Pitagoras — triplas pitagoricas e geracao aleatoria (a^2 + b^2 = c^2)
- [x] CT-2: Soma de Gauss — formula n(n+1)/2 validada ate n=1000 com edge cases
- [x] CT-3: Fatorial — definicao recursiva vs math.factorial para n=0..20
- [x] CT-4: Fibonacci — formula de Binet vs iterativo para n=1..30 e valores conhecidos
- [x] CT-5: Primos — Crivo de Eratostenes: primos ate 100 e contagem ate 1000 (168)
- [x] CT-6: MDC — Algoritmo de Euclides vs math.gcd para 1000 pares aleatorios
- [x] CT-7: Trigonometria — Identidade sin^2 + cos^2 = 1 para 1000 angulos aleatorios
- [x] CT-8: Derivada — Regra da potencia (x^n)' = n x^(n-1) via derivada numerica central

## Test File
tests/test_d1_matematica.py
