---
spec_id: SPEC-011
title: "Suite D9 — Desenho Experimental e Metodologia"
version: "1.0"
tdd_suite: "evaluations/tests/test_d9_metodologia.py"
dependencies: [SPEC-001]
ct_count: 8
---

# SPEC-011 — Suite D9

## Objetivo
Criar suite TDD para D9 (Desenho Experimental e Metodologia), atualmente
em N3 sem teste automatizado proprio.

## CTs

| CT | Descricao | Tipo |
|:--:|-----------|:----:|
| D9-1 | ANOVA one-way — F significativo quando grupos tem medias diferentes | Estatistica |
| D9-2 | Teste t — rejeita H0 quando diferenca > 2 desvios padrao | Estatistica |
| D9-3 | Randomizacao — grupos nao diferem antes do tratamento (p > 0.05) | Metodo |
| D9-4 | Tamanho de efeito — Cohen's d > 0.8 para diferenca grande | Metodo |
| D9-5 | Poder estatistico — 1-β > 0.8 para n=30, d=0.5 | Metodo |
| D9-6 | Normalidade — Shapiro-Wilk detecta nao-normalidade em dados exponenciais | Diagnostico |
| D9-7 | Propagacao de erros — Δz = √((∂z/∂x)²Δx² + (∂z/∂y)²Δy²) | Metrologia |
| D9-8 | Delineamento fatorial 2² — efeitos principais e interacao calculados | Delineamento |
