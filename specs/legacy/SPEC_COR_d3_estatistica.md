# SPEC-COR-D3: Analise Estatistica e Inferencia (CORA-Eval)
Version: 1.0.0 | Status: verified | TDD: verified

## Objective
Suite TDD para D3 do CORA-Eval — funcoes estatisticas implementadas do zero com validacao N2+N3.

## Acceptance Criteria
- [x] CT-1 (N2-01): Teste t — amostras iguais produzem |t| < 2.5; amostras diferentes produzem |t| > 5 e Cohen d > 2.0
- [x] CT-2 (N2-02): ANOVA one-way — F > 10 para 3 grupos com medias distintas (10, 12, 15)
- [x] CT-3 (N2-03): Regressao linear — recupera y = 2 + 3x com R^2 > 0.95
- [x] CT-4 (N2-04): Correlacao de Pearson — r > 0.95 para y = 2x + ruido; |r| < 0.3 para independentes
- [x] CT-5 (N2-04 ext): Bootstrap IC 95% — contem media populacional (10.0) com 1000 reamostragens
- [x] CT-6 (N3-01): MCMC Metropolis-Hastings — amostra N(0,1): |media| < 0.1, |std-1| < 0.15
- [x] CT-7 (N3-02): PCA — PC1 explica > 70% da variancia em dados 2D com correlacao 0.9
- [x] CT-8 (N3-04): Correcao multiplas comparacoes — Bonferroni e Benjamini-Hochberg com FDR controlado
- [x] CT-9: Cobertura — 11 funcoes (mean, variance, std, t_statistic, welch_df, cohens_d, pearson_r, r_squared, linear_regression, bonferroni_correction, benjamini_hochberg) todas testadas

## Test File
tests/test_d3_estatistica.py
