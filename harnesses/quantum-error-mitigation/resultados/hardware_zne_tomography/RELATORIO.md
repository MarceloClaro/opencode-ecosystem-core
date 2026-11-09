# Hardware — ZNE 4 escalas e tomografia SPAM (R1115)

Backend **Baihua** · 4096 shots · 16 jobs · gates SDD/TDD/simulação aprovados.

## ZNE

| Escala | TVD vs Bell | Task ID |
|---:|---:|---|
| 1 | 0.0645 | `52b8c44d-f322-468e-b75a-eb9140b2d7cc` |
| 3 | 0.0747 | `52268fb6-bb0d-4680-8cb5-06a672ecb71c` |
| 5 | 0.0735 | `e947cb8c-7442-4f16-9dc2-e72d82ed53cd` |
| 7 | 0.0967 | `a605ab51-66dd-4c80-972c-acc70b0d9327` |

- Monotônica: **False**.
- Linear: 0.0582.
- Quadrática: 0.0671.
- Conclusão: Curva não monotônica; extrapolação inválida e sem ganho demonstrado.

## Tomografia SPAM

| Estado | Fidelidade de preparação | Comprimento de Bloch |
|---|---:|---:|
| 0 | 0.9875 | 0.9768 |
| 1 | 0.9292 | 0.8603 |
| + | 0.9824 | 0.9682 |
| +i | 0.9839 | 0.9697 |

- r0 = P(1|prep0): 0.012451171875.
- r1 = P(0|prep1): 0.07080078125.

## Pré-registro

- 4096 shots · confiança 95% · método Wilson.
- O n foi fixado antes da execução; não foi ajustado após ver os dados.

## Limites

- ZNE extrapola TVD; não é fidelidade.
- Tomografia assume rotações de base ideais e ausência de crosstalk.
- PEC 2q, superfície e DD pulse-level não foram executados.
- Uma execução não prova vantagem quântica.
