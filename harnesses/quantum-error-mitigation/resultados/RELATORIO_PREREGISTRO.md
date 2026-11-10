# Pré-registro de comparação de layouts

Gerado em 2026-11-10T13:12:11-03:00.

## Decisão

- Comparar layouts agora: **False**.
- prep coerente abaixo de 0,99 em q0 e/ou q1.
- r1 acima de 0,05 em q0 e/ou q1.
- diferença de layout observada abaixo do efeito pré-registrado de 0,01.
- drift entre conjuntos não resolvido para r1.

## Gates

| Gate | Passa? | Evidência |
|---|---|---|
| prep coerente ≥ 0,99 | False | q0=0.9850, q1=0.9823 |
| r1 ≤ 0,05 | False | q0=0.0765, q1=0.0837 |
| efeito de layout ≥ 0,01 | False | diferença=0.0028 |
| drift resolvido | False | Δr1=+0.0072 |

## n pré-registrado

| Meia-largura | n por circuito/layout |
|---:|---:|
| 0.005 | 38,411 |
| 0.01 | 9,600 |
| 0.015 | 4,265 |

Escolhido: n = **38,411** por circuito/layout (meia-largura 0,005; p=0,5; 95%).

## Orçamento

- 12 jobs × 38,411 shots = 460,932 shots.
- 3 circuitos = E05 + calibração 00 + calibração 11; 2 conjuntos para estimar drift.

## Regras de parada

- Não comparar layouts se qualquer gate falhar.
- Não interpretar sobreposição de IC como equivalência.
- Repetir 2 conjuntos e reportar drift antes de concluir.
- Não declarar vantagem de layout sem efeito ≥ 0,01 e IC excluindo 0.

## Limites

- Pré-registro local baseado em p=0,5 e meia-largura conservadora. TVD não é proporção; o cálculo é uma aproximação de planejamento.

Hash SHA-256: `51d421c900f332f56e4e66b69a3a9bee06d023ebf32fce3cbbab3bf890dd63a4`.
