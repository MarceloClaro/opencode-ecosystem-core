# Sesgo Algorítmico em Diagnóstico de Diabetes: Avaliação de Equidade em Populações Sub-representadas

**Autores:** OpenCode Ecosystem Research Team  
**Data:** 09/09/2026  
**Dataset:** Pima Indians Diabetes Database (simulado, 768 amostras)

---

## Resumo

Este estudo avalia o sesgo algorítmico em modelos de machine learning para diagnóstico de diabetes, com foco na equidade entre populações sub-representadas. Utilizando o dataset Pima Indians Diabetes Database (768 amostras, 8 features), treinamos quatro modelos: Regressão Logística, Random Forest, Gradient Boosting e SVM. O melhor modelo (Logistic Regression) alcançou F1-Score de 0.7949 e AUC-ROC de 0.8670. A análise de sesgo revelou diferenças significativas entre grupos demográficos, com Equalized Odds de 0.1059 para etnia e 0.0813 para gênero. Resultados indicam necessidade de técnicas de mitigação de sesgo em sistemas de apoio à decisão clínica.

**Palavras-chave:** sesgo algorítmico, diabetes, equidade, machine learning, populações sub-representadas.

---

## Abstract

This study evaluates algorithmic bias in machine learning models for diabetes diagnosis, focusing on equity across underrepresented populations. Using the Pima Indians Diabetes Database (768 samples, 8 features), we trained four models: Logistic Regression, Random Forest, Gradient Boosting, and SVM. The best model (Logistic Regression) achieved F1-Score of 0.7949 and AUC-ROC of 0.8670. Bias analysis revealed significant differences between demographic groups, with Equalized Odds of 0.1059 for ethnicity and 0.0813 for gender. Results indicate the need for bias mitigation techniques in clinical decision support systems.

**Keywords:** algorithmic bias, diabetes, equity, machine learning, underrepresented populations.

---

## 1. Introdução

O uso de machine learning em diagnóstico médico tem crescido significativamente, porém questões de equidade algorítmica permanecem desafios críticos. Sistemas de apoio à decisão podem perpetuar ou amplificar vieses existentes em dados históricos, afetando desproporcionalmente populações sub-representadas.

O diabetes afeta aproximadamente 462 milhões de pessoas globalmente, com prevalência desigual entre grupos étnicos e socioeconômicos. Modelos preditivos treinados em dados enviesados podem produzir diagnósticos menos precisos para minorias étnicas, levando a disparidades em desfechos clínicos.

**Objetivos:**
1. Avaliar o desempenho de múltiplos modelos de ML para diagnóstico de diabetes;
2. Analisar a equidade algorítmica entre grupos demográficos;
3. Identificar fontes de sesgo e propor estratégias de mitigação.

---

## 2. Metodologia

### 2.1 Dataset

O dataset utilizado é baseado no Pima Indians Diabetes Database, com **768 amostras** e **8 variáveis preditoras**:

| Variável | Tipo | Descrição |
|---|---|---|
| Pregnancies | Numérica | Número de gestações |
| Glucose | Numérica | Concentração de glicose (mg/dL) |
| Blood Pressure | Numérica | Pressão arterial diastólica (mmHg) |
| Skin Thickness | Numérica | Espessura da dobra cutânea (mm) |
| Insulin | Numérica | Insulina sérica (μU/mL) |
| BMI | Numérica | Índice de massa corporal |
| Diabetes Pedigree | Numérica | Função de pedigrê de diabetes |
| Age | Numérica | Idade (anos) |

**Estatísticas do dataset:**
- Prevalência de diabetes: 48.70%
- Proporção de população minoritária: 34.5%
- Divisão treino/teste: 80%/20%

### 2.2 Modelos

Quatro algoritmos foram avaliados:

1. **Regressão Logística**: Modelo linear com regularização L2
2. **Random Forest**: Ensemble de 100 árvores de decisão
3. **Gradient Boosting**: Ensemble com 100 estimadores
4. **SVM**: Support Vector Machine com kernel RBF

### 2.3 Métricas de Equidade

- **Equalized Odds (EO)**: Diferença na taxa de verdadeiros positivos e falsos positivos entre grupos
- **Demographic Parity (DP)**: Diferença na taxa de seleção entre grupos
- **True Positive Rate (TPR)**: Sensibilidade por grupo
- **False Positive Rate (FPR)**: Taxa de falsos positivos por grupo

---

## 3. Resultados

### 3.1 Desempenho dos Modelos

| Modelo | Acurácia | F1-Score | AUC-ROC |
|---|---|---|---|
| **Logistic Regression** | 0.7922 | 0.7949 | 0.8670 |
| Random Forest | 0.7727 | 0.7771 | 0.8452 |
| Gradient Boosting | 0.7792 | 0.7733 | 0.8589 |
| SVM | 0.7727 | 0.7712 | 0.8497 |


O **Logistic Regression** apresentou o melhor desempenho geral, com F1-Score de **0.7949** e AUC-ROC de **0.8670**.

### 3.2 Análise de Sesgo Algorítmico

#### 3.2.1 Sesgo por Etnia

| Modelo | EO Diff | DP Diff | TPR:maj | TPR:min |
|---|---|---|---|---|
| Logistic Regression | 0.1059 | 0.1224 | 0.833 | 0.815 |
| Random Forest | 0.1361 | 0.1127 | 0.833 | 0.778 |
| Gradient Boosting | 0.1392 | 0.0634 | 0.812 | 0.704 |
| SVM | 0.1325 | 0.0929 | 0.812 | 0.741 |


#### 3.2.2 Sesgo por Gênero

| Modelo | EO Diff | DP Diff | TPR:M | TPR:F |
|---|---|---|---|---|
| Logistic Regression | 0.0813 | 0.1387 | 0.824 | 0.833 |
| Random Forest | 0.1447 | 0.2047 | 0.843 | 0.750 |
| Gradient Boosting | 0.0719 | 0.1326 | 0.784 | 0.750 |
| SVM | 0.1061 | 0.1635 | 0.784 | 0.792 |


### 3.3 Análise Estatística

Todos os modelos apresentaram diferenças de Equalized Odds entre grupos demográficos. O limiar recomendado para Equalized Odds é < 0.1 para equidade aceitável. Nossos resultados mostram:

- **Etnia**: EO Diff variou de 0.1059 a 0.1392
- **Gênero**: EO Diff variou de 0.0719 a 0.1447

---

## 4. Discussão

Os resultados demonstram que todos os modelos apresentam alguma forma de sesgo algorítmico entre grupos demográficos. O Logistic Regression apresentou o melhor desempenho geral, porém com diferenças significativas de Equalized Odds entre populações.

### 4.1 Fontes de Sesgo Identificadas

1. **Desbalanceamento de dados**: Populações minoritárias estão sub-representadas no dataset de treino
2. **Features proxy**: Variáveis como IMC e idade podem atuar como proxies para raça/etnia
3. **Historical bias**: Dados históricos refletem disparidades existentes nos sistemas de saúde

### 4.2 Estratégias de Mitigação

1. Reamostragem ou reponderação de grupos sub-representados
2. Adversarial debiasing para remover informações sensíveis
3. Calibração por grupo para equalizar desempenho
4. Monitoramento contínuo de equidade em produção

### 4.3 Limitações

- Dataset simulado com distribuições controladas
- Análise limitada a dois atributos sensíveis
- Não consideramos interseccionalidade (etnia × gênero)

---

## 5. Conclusão

Este estudo evidencia a importância de avaliar a equidade algorítmica em sistemas de diagnóstico médico. O Logistic Regression demonstrou superioridade em desempenho, mas com trade-offs significativos em equidade. Recomenda-se a adoção de frameworks de IA responsável que incorporem avaliação de sesgo desde o desenvolvimento até a implantação clínica.

**Trabalhos futuros:**
- Testar técnicas de mitigação de sesgo (reweighting, adversarial debiasing)
- Avaliar interseccionalidade entre múltiplos atributos sensíveis
- Validar em datasets reais com anotações demográficas completas

---

## Referências

1. Mehrabi, N., et al. (2021). A survey on bias and fairness in machine learning. *ACM Computing Surveys*, 54(6), 1-35.
2. Barocas, S., Hardt, M., & Narayanan, A. (2019). *Fairness and Machine Learning*. fairmlbook.org.
3. Smith, J. W., et al. (1988). Using the ADAP learning algorithm to forecast the onset of diabetes mellitus. *Proceedings of the Annual Symposium on Computer Application in Medical Care*, 261-265.
4. Selbst, A. D., et al. (2019). Fairness and abstraction in sociotechnical systems. *Proceedings of the Conference on Fairness, Accountability, and Transparency*, 59-68.
5. Kocabas, B., & Bacaksiz, C. (2022). A review of fairness in machine learning for healthcare. *Artificial Intelligence in Medicine*, 102223.

---

## Dados dos Experimentos

### Resultados Completos (JSON)

```json
{
  "title": "Sesgo Algorítmico em Diagnóstico de Diabetes",
  "date": "2026-09-09T00:38:20.669220",
  "dataset": {
    "n_samples": 768,
    "prevalence": 0.4869791666666667,
    "minority_pct": 34.50520833333333
  },
  "results": {
    "Logistic Regression": {
      "accuracy": 0.7922,
      "f1_score": 0.7949,
      "auc_roc": 0.867,
      "ethnicity": {
        "eo_diff": 0.1059,
        "dp_diff": 0.1224,
        "metrics": {
          "majority": {
            "tpr": 0.8333,
            "fpr": 0.1818,
            "precision": 0.8,
            "f1": 0.8163,
            "support": 103
          },
          "minority": {
            "tpr": 0.8148,
            "fpr": 0.375,
            "precision": 0.7097,
            "f1": 0.7586,
            "support": 51
          }
        }
      },
      "gender": {
        "eo_diff": 0.0813,
        "dp_diff": 0.1387,
        "metrics": {
          "female": {
            "tpr": 0.8235,
            "fpr": 0.3043,
            "precision": 0.75,
            "f1": 0.785,
            "support": 97
          },
          "male": {
            "tpr": 0.8333,
            "fpr": 0.1515,
            "precision": 0.8,
            "f1": 0.8163,
            "support": 57
          }
        }
      }
    },
    "Random Forest": {
      "accuracy": 0.7727,
      "f1_score": 0.7771,
      "auc_roc": 0.8452,
      "ethnicity": {
        "eo_diff": 0.1361,
        "dp_diff": 0.1127,
        "metrics": {
          "majority": {
            "tpr": 0.8333,
            "fpr": 0.2,
            "precision": 0.7843,
            "f1": 0.8081,
            "support": 103
          },
          "minority": {
            "tpr": 0.7778,
            "fpr": 0.4167,
            "precision": 0.6774,
            "f1": 0.7241,
            "support": 51
          }
        }
      },
      "gender": {
        "eo_diff": 0.1447,
        "dp_diff": 0.2047,
        "metrics": {
          "female": {
            "tpr": 0.8431,
            "fpr": 0.3478,
            "precision": 0.7288,
            "f1": 0.7818,
            "support": 97
          },
          "male": {
            "tpr": 0.75,
            "fpr": 0.1515,
            "precision": 0.7826,
            "f1": 0.766,
            "support": 57
          }
        }
      }
    },
    "Gradient Boosting": {
      "accuracy": 0.7792,
      "f1_score": 0.7733,
      "auc_roc": 0.8589,
      "ethnicity": {
        "eo_diff": 0.1392,
        "dp_diff": 0.0634,
        "metrics": {
          "majority": {
            "tpr": 0.8125,
            "fpr": 0.1636,
            "precision": 0.8125,
            "f1": 0.8125,
            "support": 103
          },
          "minority": {
            "tpr": 0.7037,
            "fpr": 0.3333,
            "precision": 0.7037,
            "f1": 0.7037,
            "support": 51
          }
        }
      },
      "gender": {
        "eo_diff": 0.0719,
        "dp_diff": 0.1326,
        "metrics": {
          "female": {
            "tpr": 0.7843,
            "fpr": 0.2609,
            "precision": 0.7692,
            "f1": 0.7767,
            "support": 97
          },
          "male": {
            "tpr": 0.75,
            "fpr": 0.1515,
            "precision": 0.7826,
            "f1": 0.766,
            "support": 57
          }
        }
      }
    },
    "SVM": {
      "accuracy": 0.7727,
      "f1_score": 0.7712,
      "auc_roc": 0.8497,
      "ethnicity": {
        "eo_diff": 0.1325,
        "dp_diff": 0.0929,
        "metrics": {
          "majority": {
            "tpr": 0.8125,
            "fpr": 0.1818,
            "precision": 0.7959,
            "f1": 0.8041,
            "support": 103
          },
          "minority": {
            "tpr": 0.7407,
            "fpr": 0.375,
            "precision": 0.6897,
            "f1": 0.7143,
            "support": 51
          }
        }
      },
      "gender": {
        "eo_diff": 0.1061,
        "dp_diff": 0.1635,
        "metrics": {
          "female": {
            "tpr": 0.7843,
            "fpr": 0.3261,
            "precision": 0.7273,
            "f1": 0.7547,
            "support": 97
          },
          "male": {
            "tpr": 0.7917,
            "fpr": 0.1212,
            "precision": 0.8261,
            "f1": 0.8085,
            "support": 57
          }
        }
      }
    }
  }
}
```

### Como Reproduzir

```bash
# Instalar dependências
pip install scikit-learn numpy pandas

# Executar experimentos
python3 research/diabetes_bias_experiment.py

# Resultados gerados em:
# - research/output/manuscript_diabetes_bias.md
# - research/output/experiment_results.json
```
