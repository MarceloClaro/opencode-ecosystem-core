# Hardware — ZNE e SPAM separation (R1115)

Backend **Baihua** · 4096 shots · 9 jobs · gates SDD/TDD/simulação aprovados.

## ZNE

| Escala | TVD vs Bell | Task ID |
|---:|---:|---|
| 1 | 0.0706 | `cfff51d4-072a-45e6-9fbd-4ba62d4c4527` |
| 3 | 0.1003 | `bdb63435-5517-427a-ab6b-3d4cf4758738` |
| 5 | 0.0671 | `08f5e45e-fba4-44ad-b030-79b29cdf9f24` |

- Monotônica: **False**.
- Extrapolação linear: 0.0819.
- Extrapolação quadrática: 0.0320.
- Conclusão: A curva ZNE não é monotônica; as extrapolações linear e quadrática divergem. Não há extrapolação válida nem ganho demonstrado.

## SPAM separation

| Qubit | P1(k=1) | P1(k=3) | P1(k=5) | Identificado? |
|---|---:|---:|---:|---|
| q0 | 0.9331 | 0.9233 | 0.9248 | **False** |
| q1 | 0.9255 | 0.9248 | 0.9302 | **False** |

O ajuste caiu em um limite (e≈0,5, r0≈0,5, r1≈0) e o resíduo foi alto.
Os valores de e/r0/r1 **não são físicos** e não devem ser usados. O protocolo
de pulsos π repetidos não separa preparação de leitura neste hardware.

## Limites

- ZNE não é fidelidade; a curva não monotônica invalida a extrapolação.
- SPAM separation é inconclusivo; requer tomografia/GST com bases múltiplas.
- PEC 2q, superfície e DD pulse-level não foram executados.
- Uma execução não prova vantagem quântica.
