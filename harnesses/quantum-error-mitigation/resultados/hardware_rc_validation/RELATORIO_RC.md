# Validação RC — baseline vs twirlado

Shots por job: 9600. Jobs: 16 (2 conjuntos × 8).

## TVD por conjunto

| Conjunto | Braço | Média TVD |
|---|---|---:|
| set1 | baseline | 0.0915 |
| set1 | twirled | 0.0944 |
| set2 | baseline | 0.1009 |
| set2 | twirled | 0.1012 |

## Combinado

- Baseline: 0.0962
- Twirlado: 0.0978
- Δ (twirlado − baseline): +0.0018 [-0.0071, +0.0108]
- Decisão: **sem efeito detectável** — IC 95% inclui zero.

## Limites

- 16 jobs; não é série temporal.
- TVD mede distribuição, não fidelidade de estado.
- O resultado negativo também é reportado.
