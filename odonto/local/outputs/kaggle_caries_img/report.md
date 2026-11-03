# OdontoCA Local — Relatório de Treino

> **Nível de alegação:** comparacao_empirica — comparação empírica sob revisão humana; sem garantia de acurácia superior nem de aceitação editorial.

- Linhas: 957 | Eventos: 783 | Baseline (prevalência): 0.818
- Alvo: `label` | Grupo: `None` | Folds: 5 | Seed: 0

| Modelo | AUROC | AUPRC | Brier | Sens. | Espec. | Flag |
|---|---|---|---|---|---|---|
| logreg | 0.840 | 0.961 | 0.116 | 0.958 | 0.241 | OK |
| histgb | 0.888 | 0.963 | 0.095 | 0.946 | 0.500 | OK |
| rf | 0.886 | 0.966 | 0.096 | 0.966 | 0.425 | OK |
| ensemble | 0.896 | 0.972 | 0.093 | 0.960 | 0.448 | OK |

### Ensemble no limiar ótimo (Youden) = 0.781

- Sensibilidade: 0.822 | Especificidade: 0.868
- O limiar 0,5 não é adequado a alvos desbalanceados; use o limiar de decisão apenas com revisão clínica humana.

### IC 95% (bootstrap) do ensemble

| Métrica | Lo | Hi |
|---|---|---|
| auroc | 0.868 | 0.922 |
| auprc | 0.962 | 0.982 |
| brier | 0.081 | 0.105 |

## Limitações

- Validação interna (CV); não substitui validação externa (TRIPOD+AI).
- `BELOW_BASELINE` indica desempenho ≤ acaso/prevalência — não usar o modelo nesse regime.
- Revisão humana obrigatória antes de qualquer uso.
