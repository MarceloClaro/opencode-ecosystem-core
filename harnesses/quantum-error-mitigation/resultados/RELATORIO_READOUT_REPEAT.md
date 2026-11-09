# Repetição da leitura com mitigação

Gerado em 2026-11-09T19:02:09-03:00.

| Run | Baseline TVD | Otimizado TVD | Δ | Qubits baseline | Qubits otimizado |
|---|---:|---:|---:|---|---|
| original | 0.0249 | 0.0277 | +0.0028 | [0, 1] | [106, 107] |
| set1 | 0.0263 | 0.0153 | -0.0110 | [0, 1] | [106, 107] |
| set2 | 0.0228 | 0.0079 | -0.0149 | [0, 1] | [106, 107] |

## Resumo

- Runs disponíveis: 3.
- Baseline: média 0.0247; faixa [0.02280910916322354, 0.0262802274049585].
- Otimizado: média 0.0170; faixa [0.007865908808109223, 0.027730551333399994].
- Δ: média -0.0077; faixa [-0.014943200355114317, 0.0028443542670762156].
- Sinal estável entre runs: False.
- Qubits físicos diferentes: True.

## Decisão

- Comparar layouts agora: **False**.
- o layout otimizado usa qubits físicos diferentes do baseline.
- o sinal da diferença não é estável entre o run original e os dois novos.
- os gates de prep coerente e r1 da R1120 continuam falhando.
- a mitigação de leitura não reduz o r1 físico; mitigation ≠ correção do readout.

## Limites

- Três runs de 1 job por caso; não é série temporal. O layout otimizado usa 106/107 e o baseline usa 0/1, então a diferença mistura layout com qualidade de qubit.
