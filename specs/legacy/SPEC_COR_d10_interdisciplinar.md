# SPEC-COR-D10: Sintese Interdisciplinar (CORA-Eval)
Version: 1.0.0 | Status: verified | TDD: verified

## Objective
Suite TDD para D10 do CORA-Eval — implementacao dos conceitos centrais da Geometric Arbitrage Theory (Farinelli, arXiv:0910.1671).

## Acceptance Criteria
- [x] CT-1 (N4-01): Derivadas de Nelson — D=D*=D=a para processo linear; D=2t+1, D*=2t-1, D=2t para quadratico
- [x] CT-2 (N4-02): Curvatura e Arbitragem — Curvatura R=0 quando taxas iguais (Theorem 34); R!=0 quando taxas diferentes; conexao chi e 1-forma com N componentes; holonomia trivial em curva fechada (Ambrose-Singer)
- [x] CT-3 (N4-03): Equacao de Continuidade — div_x J = r^x (eq 81); NFLVR => Dρ+divJ=0 verificado para r=0 => divJ=0

## Test File
tests/test_d10_gat.py
