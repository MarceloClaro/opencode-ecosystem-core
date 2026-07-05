# SPEC-COR-D4: Quimica Computacional e Estrutural (CORA-Eval)
Version: 1.0.0 | Status: verified | TDD: verified

## Objective
Suite TDD para D4 do CORA-Eval — balanceamento, massa molar e concentracao com massas atomicas IUPAC 2021.

## Acceptance Criteria
- [x] CT-1 (N1-01): Balanceamento — 2 H2 + O2 -> 2 H2O (manual) e CH4 + 2 O2 -> CO2 + 2 H2O (algoritmico)
- [x] CT-2 (N1-02): Massa Molar — C6H12O6 (180.156), H2O (18.015), NaCl (58.440), CaCO3 (100.087) com tolerancia 0.01 g/mol
- [x] CT-3 (N1-03): Concentracao — Conversao %(m/v) <-> mol/L para glicose 5% e NaCl 0.9%, com roundtrip consistente

## Test File
tests/test_d4_quimica.py
