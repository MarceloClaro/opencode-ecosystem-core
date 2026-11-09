# Calibração Rabi de q1 — R1118

**Spec:** `specs/SPEC-935-R1118-rabi-preparation-calibration.md`
**Script:** `harnesses/quantum-error-mitigation/hardware_rabi_calibration.py`
**Resultado:** `harnesses/quantum-error-mitigation/resultados/hardware_rabi_q1/rabi_q1.json`

## O que foi medido

16 jobs no Baihua: 8 ângulos de rotação (π/4 a 2π) em 2 eixos (`rx`, `ry`),
4096 shots por ponto. O modelo

```
p1(θ) = r0 + A·sin²((θ+ε)/2)
```

separa erro de leitura (`r0`, `r1`) de desvio coerente (`ε`).

## Resultado

| Eixo | ε (rad) | SE ε | r0 | r1 | Contraste | χ²/dof |
|---|---:|---:|---:|---:|---:|---:|
| rx | −0,0006 | 0,0091 | 0,0156 | 0,0695 | 0,9149 | 1,54 |
| ry | +0,0012 | 0,0129 | 0,0126 | 0,0786 | 0,9088 | 3,13 |

- Eixo preferido: **none**.
- Nenhum desvio coerente acima de 2σ.
- Ganho estimado vs π: ~1e−7.
- `r1` do Rabi (0,0695–0,0786) próximo do `r1` da tomografia (0,0837).

## Conclusão operacional

O pulso π de q1 está calibrado dentro de ~0,02 rad. O erro dominante é de
leitura, não de preparação coerente. Não há justificativa para aplicar um
ângulo corrigido; a prioridade é mitigação de leitura e mais conjuntos para
estimar drift.

## Limites

- Um único run; não é série temporal.
- Modelo de 3 parâmetros sem decaimento/depuração.
- Não é GST.
- Ganho estimado não é ganho validado.
