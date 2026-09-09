# M3 — Projeto Metodológico e Ética

## 1. Desenho do Estudo

**Tipo:** Estudo quantitativo-computacional de avaliação de equidade em modelos de machine learning.

**Justificativa:** O desenho experimental permite controlar variáveis e avaliar causalmente o impacto de diferentes algoritmos na equidade de predições, seguindo diretrizes PROBAST \cite{wolff2019} para avaliação de vieses em modelos preditivos.

## 2. Dados

### 2.1 Fonte
- **Dataset:** Pima Indians Diabetes Database
- **Repositório:** UCI Machine Learning Repository
- **Citação original:** Smith et al. (1988)
- **Acesso:** Público, gratuito, sem restrições

### 2.2 Variáveis

| Variável | Tipo | Descrição | Unidade |
|---|---|---|---|
| Pregnancies | Contínua | Número de gestações | — |
| Glucose | Contínua | Glicose plasmática | mg/dL |
| BloodPressure | Contínua | Pressão arterial diastólica | mmHg |
| SkinThickness | Contínua | Prega cutânea do tríceps | mm |
| Insulin | Contínua | Insulina sérica 2h | mu U/ml |
| BMI | Contínua | Índice de massa corporal | kg/m² |
| DiabetesPedigreeFunction | Contínua | Score de predisposição genética | 0–2.5 |
| Age | Contínua | Idade | anos |
| Outcome | Binária | Diagnóstico de diabetes (0/1) | — |

### 2.3 Atributos Demográficos (Simulados)

| Atributo | Categorias | Proporção |
|---|---|---|
| Gênero | Masculino (35%) / Feminino (65%) | Estratificada |
| Etnia | Maioria (65%) / Minorias (35%) | Estratificada |

**⚠️ Limitação declarada:** Dados demográficos são simulados para fins de avaliação de equidade. Resultados devem ser interpretados com cautela.

## 3. Amostragem

- **Tamanho:** n = 768 amostras
- **Divisão:** 80% treino (614), 20% teste (154)
- **Estratificação:** Proporção de classes mantida em treino e teste
- **Validação cruzada:** 5-fold estratificada no conjunto de treino

## 4. Modelos

| Modelo | Tipo | Hiperparâmetros | Justificativa |
|---|---|---|---|
| Regressão Logística | Linear | L2, C=1.0 | Interpretabilidade, uso clínico comum |
| Random Forest | Ensemble (bagging) | 100 árvores | Não-linearidade, robustez |
| Gradient Boosting | Ensemble (boosting) | 100 árvores | Alto desempenho |
| SVM | Kernel | RBF, C=1.0 | Espaço de alta dimensão |

## 5. Métricas

### 5.1 Desempenho
- F1-Score (teste)
- AUC-ROC (teste)
- Acurácia (teste)
- F1-Score médio ± DP (CV 5-fold)

### 5.2 Equidade
- **Equalized Odds Difference (EOD):** $\frac{|TPR_{g_1} - TPR_{g_2}| + |FPR_{g_1} - FPR_{g_2}|}{2}$
- **Demographic Parity Difference (DPD):** $|SR_{g_1} - SR_{g_2}|$

### 5.3 Interseccional
- TPR, F1, Acurácia por subgrupo (etnia × gênero)

## 6. Procedimentos

1. Carregar dataset e verificar valores ausentes
2. Aplicar StandardScaler em todas as features
3. Dividir 80/20 estratificado
4. Treinar 4 modelos com CV 5-fold
5. Avaliar no conjunto de teste
6. Calcular fairness metrics por grupo
7. Realizar análise interseccional
8. Gerar tabelas e figuras

## 7. Análise Estatística

- **McNemar's test:** Diferenças de desempenho entre grupos ($p < 0.05$)
- **IC 95%:** Para TPR e FPR por grupo
- **Software:** Python 3.10, scikit-learn 1.3.0

## 8. Ética e Transparência

| Item | Status |
|---|---|
| Aprovação CEP | Não aplicável (dados secundários públicos) |
| Consentimento | Não aplicável |
| Anonimização | Dataset original já anônimo |
| Dados abertos | Sim (UCI Repository) |
| Código aberto | Sim (GitHub) |
| Conflitos de interesse | Nenhum declarado |
| Financiamento | Nenhum |

## 9. Diretriz de Relato

**PROBAST** (Prediction model Risk Of Bias ASsessment Tool) — Wolff et al. (2019).

Justificativa: O estudo avalia vieses em modelo preditivo clínico, e o PROBAST é a diretriz específica para esse tipo de avaliação.
