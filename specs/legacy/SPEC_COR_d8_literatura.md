# SPEC-COR-D8: Revisao Sistematica de Literatura (CORA-Eval)
Version: 1.0.0 | Status: verified | TDD: verified

## Objective
Suite TDD para D8 do CORA-Eval — extracao de claims, contagem de citacoes e classificacao por area sobre corpus de 8 artigos reais.

## Acceptance Criteria
- [x] CT-1 (N1-01): Extracao de Claims — Afirmacoes principais extraidas de GAT, Black-Scholes e Nelson; todos os 8 artigos produzem claims > 10 caracteres
- [x] CT-2 (N1-02): Contagem de Citacoes — Farinelli=1, Black=1, Arnold=1 no corpus; corpus contem exatamente 8 papers
- [x] CT-3 (N1-03): Classificacao por Area — GAT classificado como Fisica/Matematica/Economia; Black-Scholes como Economia/Financas; Henon-Heiles como Fisica/Matematica; acuracia >= 75% sobre ground truth

## Test File
tests/test_d8_literatura.py
