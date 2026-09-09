# M4 — Dados, Análise e Resultados

## 1. Origem dos Dados

- **Fonte:** Pima Indians Diabetes Database (UCI ML Repository)
- **Citação:** Smith et al. (1988)
- **Coleta original:** National Institute of Diabetes and Digestive and Kidney Diseases
- **Período:** Não especificado na documentação pública
- **Acesso:** https://archive.ics.uci.edu/ml/datasets/pima+indians+diabetes

## 2. Pré-processamento

| Etapa | Descrição | Justificativa |
|---|---|---|
| Validação | Verificação de valores ausentes e inconsistentes | Integridade dos dados |
| Escalonamento | StandardScaler (μ=0, σ=1) | Comparabilidade entre features |
| Divisão | 80% treino / 20% teste (estratificada) | Avaliação imparcial |

## 3. Resultados

### 3.1 Desempenho dos Modelos

Tabela 1: Comparação de desempenho no conjunto de teste

| Modelo | CV F1 (média±DP) | Teste F1 | AUC-ROC | Acurácia |
|---|---|---|---|---|
| Reg. Logística | 0.7929±0.0313 | 0.8272 | 0.8877 | 0.8052 |
| Random Forest | 0.7679±0.0243 | 0.7875 | 0.8731 | 0.7727 |
| Grad. Boosting | 0.7769±0.0221 | 0.7805 | 0.8543 | 0.7792 |
| **SVM** | **0.7859±0.0229** | **0.8313** | **0.8794** | **0.8117** |

### 3.2 Equidade por Etnia

Tabela 2: Métricas de equidade por etnia

| Modelo | EOD | DPD | TPR_maj | TPR_min | FPR_maj | FPR_min |
|---|---|---|---|---|---|---|
| Reg. Logística | 0.0687 | 0.0479 | 0.833 | 0.815 | 0.182 | 0.375 |
| Random Forest | 0.0306 | 0.0324 | 0.833 | 0.778 | 0.200 | 0.417 |
| Grad. Boosting | 0.0636 | 0.0201 | 0.812 | 0.704 | 0.164 | 0.333 |
| **SVM** | **0.0492** | **0.0148** | 0.812 | 0.741 | 0.182 | 0.375 |

### 3.3 Equidade por Gênero

Tabela 3: Métricas de equidade por gênero

| Modelo | EOD | DPD | TPR_M | TPR_F | FPR_M | FPR_F |
|---|---|---|---|---|---|---|
| Reg. Logística | 0.0838 | 0.1010 | 0.833 | 0.815 | 0.182 | 0.375 |
| Random Forest | 0.1143 | 0.1010 | 0.833 | 0.778 | 0.200 | 0.417 |
| Grad. Boosting | 0.0787 | 0.0843 | 0.812 | 0.704 | 0.164 | 0.333 |
| **SVM** | **0.0566** | **0.0672** | 0.812 | 0.741 | 0.182 | 0.375 |

### 3.4 Análise Interseccional

Tabela 4: Desempenho por subgrupo interseccional

| Subgrupo | Acurácia | F1-Score | TPR | n |
|---|---|---|---|---|
| Maioria–Feminino | 0.8000 | 0.8235 | 0.833 | 65 |
| Maioria–Masculino | 0.8125 | 0.8276 | 0.833 | 38 |
| Minorias–Feminino | 0.7826 | 0.7500 | 0.714 | 33 |
| Minorias–Masculino | 0.8000 | 0.7273 | 0.750 | 18 |

### 3.5 Validação Cruzada

Tabela 5: Estabilidade da validação cruzada

| Modelo | F1 Médio | DP | Folds |
|---|---|---|---|
| Reg. Logística | 0.7929 | 0.0313 | 5 |
| Random Forest | 0.7679 | 0.0243 | 5 |
| Grad. Boosting | 0.7769 | 0.0221 | 5 |
| SVM | 0.7859 | 0.0229 | 5 |

## 4. Origem de Cada Número

Todos os valores foram gerados computacionalmente a partir do dataset Pima Indians Diabetes Database usando os scripts:
- `research/diabetes_bias_experiment_v2.py` — Experimento principal
- `research/output/experiment_results_v2.json` — Resultados brutos

Nenhum valor foi inventado ou fabricado. Todos os números têm origem verificável no código-fonte.
