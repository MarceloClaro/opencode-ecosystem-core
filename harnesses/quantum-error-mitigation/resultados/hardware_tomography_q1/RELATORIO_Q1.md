# Tomografia SPAM — q1

Conjuntos: **2**. Shots por conjunto: 4096.

| Conjunto | Prep \|0> | Prep \|1> | Prep \|+> | Prep \|+i> | r0 | r1 |
|---|---:|---:|---:|---:|---:|---:|
| set1 | 0.9856 | 0.9099 | 0.9824 | 0.9834 | 0.0144 | 0.0901 |
| set2 | 0.9827 | 0.9226 | 0.9822 | 0.9863 | 0.0173 | 0.0774 |

## Combinado + bootstrap

| Métrica | Valor | IC 95% |
|---|---:|---:|
| Prep \|0> | 0.9841 | [0.9813, 0.9868] |
| Prep \|1> | 0.9163 | [0.9100, 0.9221] |
| Prep \|+> | 0.9823 | [0.9794, 0.9851] |
| Prep \|+i> | 0.9849 | [0.9821, 0.9874] |
| r0 | 0.0159 | [0.0132, 0.0187] |
| r1 | 0.0837 | [0.0779, 0.0900] |

## Redundância do desenho

- Neste desenho, `prep \|0>` = 1 − r0 e `prep \|1>` = 1 − r1:
  são a mesma contagem Z, não duas evidências independentes.
- A preparação coerente independente de readout é medida por `\|+>` e `\|+i>`.

## Limites

- Bootstrap multinomial não captura drift entre conjuntos.
- A tomografia assume rotações de base ideais.
- Não é GST completa.
