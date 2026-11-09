# Comparação simétrica q0 vs q1 — tomografia SPAM

Cada qubit tem dois conjuntos de 12 jobs. A comparação é descritiva.

| Métrica | q0 | q1 | Δ (q1−q0) | IC q0 | IC q1 | Spread q0 | Spread q1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Prep \|0> | 0.9839 | 0.9841 | +0.0002 | [0.9811, 0.9865] | [0.9813, 0.9868] | 0.0073 | 0.0029 |
| Prep \|1> | 0.9235 | 0.9163 | -0.0072 | [0.9178, 0.9290] | [0.9100, 0.9221] | 0.0115 | 0.0127 |
| Prep \|+> | 0.9850 | 0.9823 | -0.0027 | [0.9823, 0.9875] | [0.9794, 0.9851] | 0.0051 | 0.0002 |
| Prep \|+i> | 0.9854 | 0.9849 | -0.0005 | [0.9828, 0.9879] | [0.9821, 0.9874] | 0.0029 | 0.0029 |
| r0 | 0.0161 | 0.0159 | -0.0002 | [0.0135, 0.0189] | [0.0132, 0.0187] | 0.0073 | 0.0029 |
| r1 | 0.0765 | 0.0837 | +0.0072 | [0.0710, 0.0822] | [0.0779, 0.0900] | 0.0115 | 0.0127 |

## Leitura

- Δ negativo em fidelidade de preparação significa q1 pior que q0.
- Δ positivo em r0/r1 significa mais erro de leitura em q1.
- Sobreposição de IC não equivale a equivalência estatística.
- Spread entre conjuntos maior que a largura do IC indica drift/variação
  não capturada pelo bootstrap multinomial.
- `prep \|0>` = 1 − r0 e `prep \|1>` = 1 − r1 neste desenho:
  as linhas de prep |0>/|1> e r0/r1 não são evidências independentes.
  A comparação de q1 vs q0 nesses pares é uma única medida, não duas.

## Limites

- Dois conjuntos por qubit; não é série temporal.
- Sem GST completa, sem crosstalk caracterizado.
- Nenhuma vantagem quântica é declarada.
