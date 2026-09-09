# M1 — Problema, Lacuna e Arquitetura Conceitual

## 1. Problema

Modelos de machine learning para diagnóstico de diabetes são treinados em dados que frequentemente sub-representam minorias étnicas e gênero feminino, resultando em predições enviesadas que podem ampliar disparidades existentes em saúde.

## 2. Lacuna na Literatura

| Tipo de Lacuna | Evidência |
|---|---|
| **Empírica** | Poucos estudos avaliam equidade em predição de diabetes com análise interseccional |
| **Metodológica** | Maioria dos estudos foca em um único atributo sensível (raça OU gênero) |
| **Aplicada** | Ausência de framework integrado para avaliação de equidade em ML clínico |

A lacuna é demonstrada por:
- Obermeyer et al. (2019): demonstrou sesgo em algoritmo de saúde amplamente usado, mas sem foco em diabetes
- Chen et al. (2019): avaliou disparidades raciais em predição de diabetes, mas sem análise interseccional
- Buolamwini & Gebru (2018): demonstrou efeitos interseccionais em reconhecimento facial, não em saúde

## 3. Pergunta Principal

**Como modelos de machine learning para diagnóstico de diabetes se comportam em termos de equidade entre populações sub-representadas, considerando etnia e gênero?**

## 4. Hipóteses

- **H₁:** Modelos de ML apresentam Equalized Odds significativamente diferentes entre grupos étnicos e de gênero
- **H₂:** A análise interseccional revela disparidades ampliadas para indivíduos na interseção de múltiplas identidades marginalizadas
- **H₃:** Não existe um único modelo que otimize simultaneamente desempenho discriminativo e equidade

## 5. Objetivos

### Geral
Avaliar o sesgo algorítmico em modelos de machine learning para diagnóstico de diabetes, com foco na equidade entre populações sub-representadas.

### Específicos
1. Avaliar o desempenho discriminativo de quatro modelos de classificação (Regressão Logística, Random Forest, Gradient Boosting, SVM) com validação cruzada 5-fold
2. Quantificar o sesgo algorítmico usando métricas de equidade (Equalized Odds, Demographic Parity)
3. Realizar análise interseccional para identificar disparidades ampliadas na interseção de etnia e gênero
4. Fornecer recomendações baseadas em evidências para mitigação de sesgo em sistemas clínicos de ML

## 6. Construtos e Variáveis

| Construto | Variável | Tipo | Escala |
|---|---|---|---|
| Desempenho | F1-Score, AUC-ROC, Acurácia | Contínua | 0–1 |
| Equidade | Equalized Odds Difference | Contínua | 0–1 |
| Equidade | Demographic Parity Difference | Contínua | 0–1 |
| Interseccionalidade | TPR/FPR por subgrupo | Contínua | 0–1 |

## 7. Matriz de Coerência

```
Problema → Pergunta → Objetivos → Método → Análise → Resultado → Conclusão
    ↓          ↓          ↓          ↓          ↓          ↓          ↓
Sesgo     Como se      Avaliar     4 modelos   EOD/DPD    Tabelas    Mitigação
algorít.  comportam?   4 métricas  CV 5-fold   Intersec.  Figuras    recomend.
```

## 8. Contribuições Esperadas

1. **Empírica:** Evidência de disparidades interseccionais em predição de diabetes
2. **Metodológica:** Framework integrado de avaliação de equidade (performance + fairness + intersecção)
3. **Aplicada:** Recomendações práticas para desenvolvimento de modelos mais justos
4. **Reprodutível:** Código e dados abertos para replicação
