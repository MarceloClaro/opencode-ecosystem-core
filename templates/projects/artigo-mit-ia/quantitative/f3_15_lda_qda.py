"""
Fase 3.15 — LDA / QDA (Classificação Discriminante)
=====================================================
Classifica países em 2 grupos (alta/baixa escape_arm) usando
análise discriminante linear e quadrática.

Objetivos:
  1. LDA: fronteira linear entre grupos
  2. QDA: fronteira quadrática (captura não-linearidades)
  3. Comparação com RF (benchmark)
  4. Matriz de confusão + variáveis discriminantes
"""

import pandas as pd
import numpy as np
import json
import warnings
import sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')

BASE = Path(r'C:\Users\marce\.config\opencode\artigo-mit-ia\quantitative')
DATA = BASE / 'output' / 'dataset_corte_transversal.csv'
OUT  = BASE / 'output' / 'lda_qda_resultados.json'

df = pd.read_csv(DATA)
print(f"Dataset: {df.shape[0]} países")

# ── Features e target binário ────────────────────────────────────────────────
FEATURES = ['aipi_digital', 'aipi_humano', 'aipi_inovacao', 'aipi_regulacao',
            'pib_pc_ppc', 'ptf_relativa', 'educ_superior_pct',
            'internet_pop_pct', 'gini', 'agricultura_pib_pct']
TARGET = 'escape_arm'

# Remover NaN
df_m = df[FEATURES + [TARGET, 'pais']].dropna()
print(f"Amostra válida: {df_m.shape[0]} países")

# Mediana para binarizar
mediana = df_m[TARGET].median()
df_m['escape_alto'] = (df_m[TARGET] >= mediana).astype(int)
print(f"  Grupo alto (≥{mediana:.3f}): {(df_m['escape_alto']==1).sum()}")
print(f"  Grupo baixo (<{mediana:.3f}): {(df_m['escape_alto']==0).sum()}")

from sklearn.model_selection import cross_val_score, train_test_split, StratifiedKFold
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score

X = df_m[FEATURES].values
y = df_m['escape_alto'].values

# Split
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

resultados = {}

# ── 1. LDA ──────────────────────────────────────────────────────────────────
print("\n═══ LDA (Análise Discriminante Linear) ═══")
lda = LinearDiscriminantAnalysis()
lda.fit(X_tr, y_tr)
y_pred_lda = lda.predict(X_te)
y_prob_lda = lda.predict_proba(X_te)[:, 1]

acc_lda = accuracy_score(y_te, y_pred_lda)
auc_lda = roc_auc_score(y_te, y_prob_lda)
cv_lda = cross_val_score(lda, X, y, cv=5, scoring='accuracy')

resultados['LDA'] = {
    'acuracia_teste': round(acc_lda, 4),
    'auc_roc': round(auc_lda, 4),
    'cv_acuracia_media': round(cv_lda.mean(), 4),
    'cv_acuracia_std': round(cv_lda.std(), 4),
    'coeficientes': {feat: round(coef[0], 4) for feat, coef in zip(FEATURES, lda.coef_.T)},
    'intercepto': round(lda.intercept_[0], 4)
}
print(f"  Acurácia teste: {acc_lda:.4f}")
print(f"  AUC-ROC:        {auc_lda:.4f}")
print(f"  CV (5-fold):    {cv_lda.mean():.4f} ± {cv_lda.std():.4f}")
print(f"  Coeficientes:")
for feat, coef in zip(FEATURES, lda.coef_[0]):
    print(f"    {feat:25s}  {coef:+.4f}")

# ── 2. QDA ──────────────────────────────────────────────────────────────────
print("\n═══ QDA (Análise Discriminante Quadrática) ═══")
qda = QuadraticDiscriminantAnalysis(reg_param=0.01)
qda.fit(X_tr, y_tr)
y_pred_qda = qda.predict(X_te)
y_prob_qda = qda.predict_proba(X_te)[:, 1]

acc_qda = accuracy_score(y_te, y_pred_qda)
auc_qda = roc_auc_score(y_te, y_prob_qda)
cv_qda = cross_val_score(qda, X, y, cv=5, scoring='accuracy')

resultados['QDA'] = {
    'acuracia_teste': round(acc_qda, 4),
    'auc_roc': round(auc_qda, 4),
    'cv_acuracia_media': round(cv_qda.mean(), 4),
    'cv_acuracia_std': round(cv_qda.std(), 4)
}
print(f"  Acurácia teste: {acc_qda:.4f}")
print(f"  AUC-ROC:        {auc_qda:.4f}")
print(f"  CV (5-fold):    {cv_qda.mean():.4f} ± {cv_qda.std():.4f}")

# ── 3. RF Classifier (benchmark) ────────────────────────────────────────────
print("\n═══ RF Classifier (benchmark) ═══")
rf = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42, n_jobs=-1)
rf.fit(X_tr, y_tr)
y_pred_rf = rf.predict(X_te)
y_prob_rf = rf.predict_proba(X_te)[:, 1]

acc_rf = accuracy_score(y_te, y_pred_rf)
auc_rf = roc_auc_score(y_te, y_prob_rf)
cv_rf = cross_val_score(rf, X, y, cv=5, scoring='accuracy')

resultados['RF_benchmark'] = {
    'acuracia_teste': round(acc_rf, 4),
    'auc_roc': round(auc_rf, 4),
    'cv_acuracia_media': round(cv_rf.mean(), 4),
    'cv_acuracia_std': round(cv_rf.std(), 4),
    'top_features': {feat: round(imp, 4) for feat, imp in
                     sorted(zip(FEATURES, rf.feature_importances_), key=lambda x: -x[1])[:5]}
}
print(f"  Acurácia teste: {acc_rf:.4f}")
print(f"  AUC-ROC:        {auc_rf:.4f}")
print(f"  CV (5-fold):    {cv_rf.mean():.4f} ± {cv_rf.std():.4f}")

# ── 4. Matrizes de confusão ────────────────────────────────────────────────
print("\n═══ Matrizes de Confusão ═══")
print("  LDA:")
print(f"    {confusion_matrix(y_te, y_pred_lda)}")
print("  QDA:")
print(f"    {confusion_matrix(y_te, y_pred_qda)}")
print("  RF:")
print(f"    {confusion_matrix(y_te, y_pred_rf)}")

resultados['confusao_LDA'] = confusion_matrix(y_te, y_pred_lda).tolist()
resultados['confusao_QDA'] = confusion_matrix(y_te, y_pred_qda).tolist()
resultados['confusao_RF'] = confusion_matrix(y_te, y_pred_rf).tolist()

# ── 5. Resumo ───────────────────────────────────────────────────────────────
print("\n═══ RESUMO — Comparação LDA vs QDA vs RF ═══")
for modelo in ['LDA', 'QDA', 'RF_benchmark']:
    m = resultados[modelo]
    print(f"  {modelo:15s}  AUC={m['auc_roc']:.4f}  Acc={m['acuracia_teste']:.4f}  CV={m['cv_acuracia_media']:.4f}")

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)
print(f"\nResultados salvos em: {OUT}")
