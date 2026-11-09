# Tomografia SPAM — q0 vs q1

| Qubit | Fidelidade \|0> | \|1> | \|+> | \|+i> | r0 | r1 |
|---|---:|---:|---:|---:|---:|---:|
| q0 | 0.9875 | 0.9292 | 0.9824 | 0.9839 | 0.0125 | 0.0708 |
| q1 | 0.9841 | 0.9163 | 0.9823 | 0.9849 | 0.0159 | 0.0837 |

## Bootstrap q1 (2 conjuntos)

| Estado | Média | IC 95% |
|---|---:|---:|
| 0 | 0.9841 | [0.9813, 0.9868] |
| 1 | 0.9163 | [0.9100, 0.9221] |
| + | 0.9823 | [0.9794, 0.9851] |
| +i | 0.9848 | [0.9821, 0.9874] |

r0: 0.0159 [0.0132, 0.0187].
r1: 0.0837 [0.0779, 0.0900].

## Limites

- q0 tem um conjunto; q1 tem dois; a comparação é descritiva.
- Bootstrap não captura drift entre execuções.
- A tomografia assume rotações de base ideais.
