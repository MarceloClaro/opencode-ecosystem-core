# SPEC-COR-D9: Desenho Experimental e Metodologia (CORA-Eval)
Version: 1.0.0 | Status: verified | TDD: verified

## Objective
Suite TDD para D9 do CORA-Eval — validacao de metodos estatisticos para desenho experimental com scipy e numpy.

## Acceptance Criteria
- [x] CT-1: ANOVA one-way — p < 0.001 com grupos diferentes; p > 0.05 com grupos iguais
- [x] CT-2: Teste t — p < 0.001 com diferenca de 4 SD; p > 0.05 com diferenca de 0.1 SD
- [x] CT-3: Randomizacao — Grupos randomizados nao diferem antes do tratamento (p > 0.05)
- [x] CT-4: Cohen's d — d > 0.8 (large effect); d < 0.5 (small effect)
- [x] CT-5: Poder Estatistico — Poder > 0.4 para d=0.5, n=30; poder aumenta com n (p100 > p30)
- [x] CT-6: Shapiro-Wilk — p > 0.05 para dados normais; p < 0.05 para dados exponenciais
- [x] CT-7: Propagacao de Erros — dz = sqrt((df/dx*dx)^2 + (df/dy*dy)^2) consistente com derivadas numericas
- [x] CT-8: Delineamento Fatorial 2^2 — Efeito principal A (temperatura) > 0 e entre 6-10; efeito B (pH) < 3

## Test File
tests/test_d9_metodologia.py
