# Tomografia SPAM — q0

Conjuntos: **2**. Shots por conjunto: 4096.

| Conjunto | Prep \|0> | Prep \|1> | Prep \|+> | Prep \|+i> | r0 | r1 |
|---|---:|---:|---:|---:|---:|---:|
| set1 | 0.9875 | 0.9292 | 0.9824 | 0.9839 | 0.0125 | 0.0708 |
| set2 | 0.9802 | 0.9177 | 0.9875 | 0.9868 | 0.0198 | 0.0823 |

## Combinado + bootstrap

| Métrica | Valor | IC 95% |
|---|---:|---:|
| Prep \|0> | 0.9839 | [0.9811, 0.9865] |
| Prep \|1> | 0.9235 | [0.9178, 0.9290] |
| Prep \|+> | 0.9850 | [0.9823, 0.9875] |
| Prep \|+i> | 0.9854 | [0.9828, 0.9879] |
| r0 | 0.0161 | [0.0135, 0.0189] |
| r1 | 0.0765 | [0.0710, 0.0822] |

## Redundância do desenho

- Neste desenho, `prep \|0>` = 1 − r0 e `prep \|1>` = 1 − r1:
  são a mesma contagem Z, não duas evidências independentes.
- A preparação coerente independente de readout é medida por `\|+>` e `\|+i>`.

## Limites

- Bootstrap multinomial não captura drift entre conjuntos.
- A tomografia assume rotações de base ideais.
- Não é GST completa.
