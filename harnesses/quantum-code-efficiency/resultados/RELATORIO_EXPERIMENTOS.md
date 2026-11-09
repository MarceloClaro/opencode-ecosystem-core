# Eficiência nos experimentos E01–E18

Seed 42 · níveis [0, 1, 2, 3] · ruído [0.0, 0.001, 0.005, 0.01] · 2048 tiros por ponto de ruído.

## Protocolo

- Baseline: `optimization_level=0`.
- Varredura: níveis de otimização declarados.
- Gate de correção: TVD ≤ `1e-9` entre as distribuições ideais.
- Ruído: modelo depolarizante de porta (`u` 1q, `cx` 2q), sem hardware.

## Resumo

- Circuitos: **25** em **18** experimentos.
- Pass: **25** · Fail: **0**.
- Redução média de 2q: **1.3%**.
- Redução média de profundidade: **12.9%**.
- TVD médio do melhor nível: **1.693e-17**.

## Por circuito

| Circuito | Exp. | Melhor nível | 2q base | 2q melhor | Δ2q | depth base | depth melhor | Δdepth | TVD | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| E01_1 | E01 | 0 | 0 | 0 | 0.0% | 1 | 1 | 0.0% | 0.00e+00 | pass |
| E02_1 | E02 | 0 | 0 | 0 | 0.0% | 2 | 2 | 0.0% | 0.00e+00 | pass |
| E03_1 | E03 | 0 | 0 | 0 | 0.0% | 2 | 2 | 0.0% | 0.00e+00 | pass |
| E04_1 | E04 | 1 | 0 | 0 | 0.0% | 4 | 2 | 50.0% | 7.97e-33 | pass |
| E05_1 | E05 | 0 | 1 | 1 | 0.0% | 3 | 3 | 0.0% | 0.00e+00 | pass |
| E06_1 | E06 | 0 | 3 | 3 | 0.0% | 5 | 5 | 0.0% | 0.00e+00 | pass |
| E07_1 | E07 | 0 | 1 | 1 | 0.0% | 4 | 4 | 0.0% | 0.00e+00 | pass |
| E07_2 | E07 | 0 | 1 | 1 | 0.0% | 4 | 4 | 0.0% | 0.00e+00 | pass |
| E07_3 | E07 | 0 | 1 | 1 | 0.0% | 4 | 4 | 0.0% | 0.00e+00 | pass |
| E07_4 | E07 | 0 | 1 | 1 | 0.0% | 4 | 4 | 0.0% | 0.00e+00 | pass |
| E08_1 | E08 | 0 | 0 | 0 | 0.0% | 2 | 2 | 0.0% | 0.00e+00 | pass |
| E09_1 | E09 | 0 | 0 | 0 | 0.0% | 2 | 2 | 0.0% | 0.00e+00 | pass |
| E10_1 | E10 | 1 | 1 | 1 | 0.0% | 5 | 4 | 20.0% | 0.00e+00 | pass |
| E10_2 | E10 | 1 | 1 | 1 | 0.0% | 5 | 4 | 20.0% | 1.11e-16 | pass |
| E10_3 | E10 | 1 | 1 | 1 | 0.0% | 5 | 4 | 20.0% | 5.55e-17 | pass |
| E10_4 | E10 | 1 | 1 | 1 | 0.0% | 5 | 4 | 20.0% | 1.11e-16 | pass |
| E11_1 | E11 | 1 | 1 | 1 | 0.0% | 5 | 4 | 20.0% | 0.00e+00 | pass |
| E12_1 | E12 | 2 | 9 | 6 | 33.3% | 20 | 14 | 30.0% | 1.18e-16 | pass |
| E13_1 | E13 | 0 | 0 | 0 | 0.0% | 2 | 2 | 0.0% | 0.00e+00 | pass |
| E14_1 | E14 | 1 | 0 | 0 | 0.0% | 4 | 2 | 50.0% | 0.00e+00 | pass |
| E15_1 | E15 | 0 | 3 | 3 | 0.0% | 5 | 5 | 0.0% | 0.00e+00 | pass |
| E16_1 | E16 | 0 | 0 | 0 | 0.0% | 2 | 2 | 0.0% | 0.00e+00 | pass |
| E16_2 | E16 | 1 | 0 | 0 | 0.0% | 3 | 1 | 66.7% | 1.87e-33 | pass |
| E17_1 | E17 | 1 | 2 | 2 | 0.0% | 8 | 6 | 25.0% | 2.78e-17 | pass |
| E18_1 | E18 | 0 | 0 | 0 | 0.0% | 2 | 2 | 0.0% | 0.00e+00 | pass |

## Ruído depolarizante

| p | TVD baseline | TVD melhor nível | Δ |
|---:|---:|---:|---:|
| 0 | 0.0068 | 0.0077 | +0.0009 |
| 0.001 | 0.0061 | 0.0063 | +0.0002 |
| 0.005 | 0.0094 | 0.0073 | -0.0021 |
| 0.01 | 0.0142 | 0.0094 | -0.0048 |

> Em p = 0, a TVD reflete apenas o ruído de amostragem (2048 tiros), não erro de porta.

## Limites

- Simulação e distribuição ideal; não é hardware.
- A TVD com ruído é um proxy do modelo depolarizante, não uma previsão de fidelidade.
- O resultado depende da versão do Qiskit, do seed e do conjunto de portas.
- Redução de portas não é vantagem quântica.
