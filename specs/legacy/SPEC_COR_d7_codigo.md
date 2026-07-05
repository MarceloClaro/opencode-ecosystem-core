# SPEC-COR-D7: Verificacao de Codigo Cientifico (CORA-Eval)
Version: 1.0.0 | Status: verified | TDD: verified

## Objective
Suite TDD para D7 do CORA-Eval — aplica verificadores V7a-V7f ao proprio codigo dos testes CORA-Eval.

## Acceptance Criteria
- [x] CT-1 (N3-01): V7a Syntax — todos os arquivos test_*.py tem sintaxe Python valida via ast.parse()
- [x] CT-2 (N3-01): V7b Logic — mean(idempotent)=constant; variance sempre >= 0 (pre/post conditions)
- [x] CT-3 (N3-03): V7c Types — 5 funcoes (mean, variance, t_statistic, cohens_d, pearson_r) retornam float
- [x] CT-4 (N3-04): V7d Complexity — mean(10000) executa em < 0.1s (O(n) verificado)
- [x] CT-5 (N3-02): V7e Security — nenhum uso de eval() ou exec() (CWE-95) nos arquivos de teste
- [x] CT-6 (N3-05): V7f Coverage — 11 funcoes de D3 sao executaveis sem erro com dados validos

## Test File
tests/test_d7_codigo.py
