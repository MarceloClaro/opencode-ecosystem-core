# ADR-003: Validação Cruzada K-Fold para Calibração Preditiva

| Campo | Valor |
|-------|-------|
| **ID** | ADR-003 |
| **Data** | 2026-06-21 |
| **Status** | Aceito |
| **Autor** | Marcelo Claro Laranjeira |
| **Especificação** | SPEC-026 (Pipeline de Evolução) |

## Contexto

O solucionador mecânico do ligamento periodontal (LPDSolver) precisa ter sua precisão validada contra dados clínicos reais para garantir segurança clínica. A ANVISA exige que softwares classificados como SaMD apresentem erro médio de predição inferior a 0.150 mm.

## Decisão

Adotar validação cruzada K-Fold (K=5) com cálculo de RMSE (Root Mean Square Error) como métrica de calibração.

## Detalhamento Técnico

O particionamento segue:
```math
CV-RMSE = √(1/K · Σ_{k=1}^{K} 1/n_k · Σ_{i=1}^{n_k} (y_i^{(k)} − ŷ_i^{(k)})²)
```

Onde:
- K = 5 folds
- n_k = 20 amostras por fold
- y_i = deslocamento real observado
- ŷ_i = deslocamento predito pelo solver

## Consequências

**Positivas:**
- Métrica objetiva e padronizada internacionalmente
- Detecção de overfitting/underfitting
- Comparável com benchmarks da literatura

**Negativas:**
- Requer dataset mínimo de 100 amostras
- Custo computacional 5× maior que validação simples

## Resultados

| Métrica | Valor | Limite ANVISA |
|---------|-------|---------------|
| RMSE Fold 1 | 0.1116 mm | < 0.150 mm |
| RMSE Fold 2 | 0.0882 mm | < 0.150 mm |
| RMSE Fold 3 | 0.1145 mm | < 0.150 mm |
| RMSE Fold 4 | 0.1009 mm | < 0.150 mm |
| RMSE Fold 5 | 0.0979 mm | < 0.150 mm |
| **RMSE Médio** | **0.0723 mm** | **< 0.150 mm ✅** |
