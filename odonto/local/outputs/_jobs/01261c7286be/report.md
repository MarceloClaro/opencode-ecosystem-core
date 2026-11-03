# OdontoCA Local — Relatório de Treino

> **Nível de alegação:** comparacao_empirica — comparação empírica sob revisão humana; sem garantia de acurácia superior nem de aceitação editorial.

- Linhas: 200 | Eventos: 162 | Baseline (prevalência): 0.810
- Alvo: `label` | Grupo: `None` | Folds: 2 | Seed: 0

| Modelo | AUROC | AUPRC | Brier | Sens. | Espec. | Flag |
|---|---|---|---|---|---|---|
| logreg | 0.805 | 0.927 | 0.127 | 0.920 | 0.421 | BELOW_BASELINE |
| histgb | 0.834 | 0.942 | 0.140 | 0.901 | 0.395 | OK |
| rf | 0.808 | 0.945 | 0.123 | 0.975 | 0.263 | BELOW_BASELINE |
| ensemble | 0.821 | 0.943 | 0.117 | 0.957 | 0.342 | OK |

### Ensemble no limiar ótimo (Youden) = 0.862

- Sensibilidade: 0.735 | Especificidade: 0.842
- O limiar 0,5 não é adequado a alvos desbalanceados; use o limiar de decisão apenas com revisão clínica humana.

### IC 95% (bootstrap) do ensemble

| Métrica | Lo | Hi |
|---|---|---|
| auroc | 0.753 | 0.898 |
| auprc | 0.910 | 0.977 |
| brier | 0.086 | 0.146 |

## Limitações

- Validação interna (CV); não substitui validação externa (TRIPOD+AI).
- `BELOW_BASELINE` indica desempenho ≤ acaso/prevalência — não usar o modelo nesse regime.
- Revisão humana obrigatória antes de qualquer uso.
