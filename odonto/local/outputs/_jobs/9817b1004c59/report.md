# OdontoCA Local — Relatório de Treino

> **Nível de alegação:** comparacao_empirica — comparação empírica sob revisão humana; sem garantia de acurácia superior nem de aceitação editorial.

- Linhas: 2504 | Eventos: 1050 | Baseline (prevalência): 0.419
- Alvo: `Y` | Grupo: `None` | Folds: 5 | Seed: 0

| Modelo | AUROC | AUPRC | Brier | Sens. | Espec. | Flag |
|---|---|---|---|---|---|---|
| logreg | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | OK |
| histgb | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | OK |
| rf | 1.000 | 1.000 | 0.179 | 0.555 | 1.000 | OK |
| ensemble | 1.000 | 1.000 | 0.021 | 1.000 | 1.000 | OK |

### Ensemble no limiar ótimo (Youden) = 0.788

- Sensibilidade: 1.000 | Especificidade: 1.000
- O limiar 0,5 não é adequado a alvos desbalanceados; use o limiar de decisão apenas com revisão clínica humana.

### IC 95% (bootstrap) do ensemble

| Métrica | Lo | Hi |
|---|---|---|
| auroc | 1.000 | 1.000 |
| auprc | 1.000 | 1.000 |
| brier | 0.021 | 0.021 |

## Limitações

- Validação interna (CV); não substitui validação externa (TRIPOD+AI).
- `BELOW_BASELINE` indica desempenho ≤ acaso/prevalência — não usar o modelo nesse regime.
- Revisão humana obrigatória antes de qualquer uso.
