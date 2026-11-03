# OdontoCA Local — Relatório de Treino

> **Nível de alegação:** comparacao_empirica — comparação empírica sob revisão humana; sem garantia de acurácia superior nem de aceitação editorial.

- Linhas: 996 | Eventos: 83 | Baseline (prevalência): 0.083
- Alvo: `caries_onset` | Grupo: `HostID` | Folds: 5 | Seed: 0

| Modelo | AUROC | AUPRC | Brier | Sens. | Espec. | Flag |
|---|---|---|---|---|---|---|
| logreg | 0.814 | 0.245 | 0.081 | 0.000 | 1.000 | OK |
| histgb | 0.788 | 0.206 | 0.086 | 0.108 | 0.963 | OK |
| rf | 0.819 | 0.261 | 0.069 | 0.000 | 1.000 | OK |
| ensemble | 0.805 | 0.225 | 0.073 | 0.000 | 1.000 | OK |

### Ensemble no limiar ótimo (Youden) = 0.028

- Sensibilidade: 0.940 | Especificidade: 0.608
- O limiar 0,5 não é adequado a alvos desbalanceados; use o limiar de decisão apenas com revisão clínica humana.

### IC 95% (bootstrap) do ensemble

| Métrica | Lo | Hi |
|---|---|---|
| auroc | 0.767 | 0.837 |
| auprc | 0.167 | 0.307 |
| brier | 0.060 | 0.086 |

## Limitações

- Validação interna (CV); não substitui validação externa (TRIPOD+AI).
- `BELOW_BASELINE` indica desempenho ≤ acaso/prevalência — não usar o modelo nesse regime.
- Revisão humana obrigatória antes de qualquer uso.
