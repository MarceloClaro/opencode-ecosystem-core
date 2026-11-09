# Calibração Rabi — q1

Backend: Baihua. Jobs: 16. Shots por ponto: 4096.

| Eixo | ε (rad) | SE ε | r0 | r1 | Contraste | χ²/dof | Identificado |
|---|---:|---:|---:|---:|---:|---:|---|
| x | -0.0006 | 0.0091 | 0.0156 | 0.0695 | 0.9149 | 1.54 | True |
| y | +0.0012 | 0.0129 | 0.0126 | 0.0786 | 0.9088 | 3.13 | True |

## Leitura

- Eixo preferido: **none**.
- Ganho estimado vs π: 0.00e+00 ± 0.00e+00.
- `x`: |ε| = 0.0006 rad; 2σ = 0.0182 rad; θ* = 3.1422 rad; ganho vs π = 9.19e-08.
- `y`: |ε| = 0.0012 rad; 2σ = 0.0259 rad; θ* = 3.1404 rad; ganho vs π = 3.48e-07.

## Interpretação

- Não foi detectado desvio coerente do ângulo de π acima de 2σ.
- `rx` e `ry` são equivalentes dentro da incerteza; não há eixo preferido.
- O erro dominante é de leitura (r0/r1), não de preparação coerente.
- Nenhum ângulo corrigido é justificado por este run.

## Limites

- Um único run; não é série temporal.
- Modelo de 3 parâmetros sem decaimento/depuração.
- Não é GST; r1 é sensível ao modelo e ao drift.
- Ganho estimado não é ganho validado.
