import pandas as pd
import numpy as np
import os, sys, json, warnings, hashlib
from datetime import datetime

# ========== CONFIG REPRODUTIVEL ==========
GLOBAL_SEED = 42
np.random.seed(GLOBAL_SEED)
SCRIPT_HASH = hashlib.sha256(open(__file__, "rb").read()).hexdigest()[:12]
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")

print("=" * 70)
print("FASE 2 — PIPELINE ML COMPLETO")
print(f"Seed: {GLOBAL_SEED} | Script Hash: {SCRIPT_HASH}")
print(f"Execucao: {datetime.now().isoformat()}")
print("=" * 70)

# ========== 1. CARREGAR DADOS ==========
print("\n[1] Carregando dados...")
df = pd.read_csv(os.path.join(OUTPUT_DIR, "dataset_latest.csv"))
print(f"Shape: {df.shape}")
print(f"Colunas: {list(df.columns)}")

# Filtrar features para ML
feature_cols = [
    "gdp_per_capita", "tertiary_enrollment", "rd_spending",
    "patent_apps", "high_tech_exp", "internet_users",
    "fdi_inflows", "unemployment", "gini", "services_emp",
    "ai_readiness"
]

# Remover linhas com NaN nas features principais
df_ml = df.dropna(subset=feature_cols + ["arm_trapped"], how="any").copy()
print(f"Dados para ML (features + target): {df_ml.shape}")

# Tratar valores infinitos
df_ml = df_ml.replace([np.inf, -np.inf], np.nan).dropna(subset=feature_cols)

X = df_ml[feature_cols].values
y_class = df_ml["arm_trapped"].values.astype(int)
y_reg = df_ml["gdp_growth"].values

economy_names = df_ml["economy"].values
country_names = df_ml.get("name", economy_names)

print(f"\nX shape: {X.shape}")
print(f"y_class: {y_class.sum()} trapped / {len(y_class)} total")
print(f"y_reg (GDP growth): media={y_reg[~np.isnan(y_reg)].mean():.2f}%, "
      f"std={y_reg[~np.isnan(y_reg)].std():.2f}%")

# ========== 2. IMPORTACOES ==========
print("\n[2] Importando bibliotecas ML...")
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.model_selection import (
    cross_val_score, cross_val_predict, StratifiedKFold, KFold,
    train_test_split, GridSearchCV
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report, r2_score, mean_squared_error,
    mean_absolute_error
)
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import warnings; warnings.filterwarnings("ignore")

# ========== 3. CLASSIFICACAO ARM ==========
print("\n[3] CLASSIFICACAO — Previsao de ARM")
print("-" * 60)

# 3a) Baseline: Logistic Regression
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# StratifiedKFold para classe desbalanceada
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=GLOBAL_SEED)

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=GLOBAL_SEED, class_weight="balanced"),
    "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=8, random_state=GLOBAL_SEED, class_weight="balanced"),
}

results_class = {}
for name, model in models.items():
    scores_acc = cross_val_score(model, X_scaled, y_class, cv=skf, scoring="accuracy")
    scores_f1 = cross_val_score(model, X_scaled, y_class, cv=skf, scoring="f1")
    scores_auc = cross_val_score(model, X_scaled, y_class, cv=skf, scoring="roc_auc")
    
    # Predict for confusion matrix
    y_pred = cross_val_predict(model, X_scaled, y_class, cv=skf)
    
    results_class[name] = {
        "accuracy": round(scores_acc.mean(), 4),
        "accuracy_std": round(scores_acc.std(), 4),
        "f1": round(scores_f1.mean(), 4),
        "f1_std": round(scores_f1.std(), 4),
        "roc_auc": round(scores_auc.mean(), 4),
        "roc_auc_std": round(scores_auc.std(), 4),
        "precision": round(precision_score(y_class, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_class, y_pred, zero_division=0), 4),
    }
    
    print(f"\n{name}:")
    print(f"  Accuracy:  {scores_acc.mean():.4f} +/- {scores_acc.std():.4f}")
    print(f"  F1-Score:  {scores_f1.mean():.4f} +/- {scores_f1.std():.4f}")
    print(f"  ROC-AUC:   {scores_auc.mean():.4f} +/- {scores_auc.std():.4f}")
    print(f"  Precision: {results_class[name]['precision']:.4f}")
    print(f"  Recall:    {results_class[name]['recall']:.4f}")
    
    # Confusion matrix
    cm = confusion_matrix(y_class, y_pred)
    print(f"  Confusion Matrix:")
    print(f"    TN={cm[0,0]}  FP={cm[0,1]}")
    print(f"    FN={cm[1,0]}  TP={cm[1,1]}")

# 3b) Feature Importance (Random Forest)
rf = RandomForestClassifier(n_estimators=500, max_depth=8, random_state=GLOBAL_SEED, class_weight="balanced")
rf.fit(X_scaled, y_class)

importances = pd.DataFrame({
    "feature": feature_cols,
    "importance_rf": rf.feature_importances_
}).sort_values("importance_rf", ascending=False)

print(f"\nFeature Importance (Random Forest):")
print(importances.to_string(index=False))

# Permutation importance
perm_imp = permutation_importance(rf, X_scaled, y_class, n_repeats=20, random_state=GLOBAL_SEED)
importances["importance_perm"] = perm_imp.importances_mean
importances["importance_perm_std"] = perm_imp.importances_std
print(f"\nPermutation Importance (confirmacao cruzada):")
print(importances.sort_values("importance_perm", ascending=False).to_string(index=False))

# ========== 4. REGRESSAO — GDP Growth ==========
print("\n\n[4] REGRESSAO — Previsao de Crescimento GDP")
print("-" * 60)

y_reg_clean = y_reg[~np.isnan(y_reg)]
X_reg = X_scaled[~np.isnan(y_reg)]
print(f"Samples regression: {len(X_reg)}")

kf = KFold(n_splits=5, shuffle=True, random_state=GLOBAL_SEED)

reg_models = {
    "Linear Regression": LinearRegression(),
    "Ridge (alpha=1)": Ridge(alpha=1.0, random_state=GLOBAL_SEED),
    "Random Forest Regressor": RandomForestRegressor(n_estimators=200, max_depth=8, random_state=GLOBAL_SEED),
}

results_reg = {}
for name, model in reg_models.items():
    scores_r2 = cross_val_score(model, X_reg, y_reg_clean, cv=kf, scoring="r2")
    y_pred_reg = cross_val_predict(model, X_reg, y_reg_clean, cv=kf)
    
    results_reg[name] = {
        "r2": round(scores_r2.mean(), 4),
        "r2_std": round(scores_r2.std(), 4),
        "rmse": round(np.sqrt(mean_squared_error(y_reg_clean, y_pred_reg)), 4),
        "mae": round(mean_absolute_error(y_reg_clean, y_pred_reg), 4),
    }
    
    print(f"\n{name}:")
    print(f"  R2:   {scores_r2.mean():.4f} +/- {scores_r2.std():.4f}")
    print(f"  RMSE: {results_reg[name]['rmse']:.4f}")
    print(f"  MAE:  {results_reg[name]['mae']:.4f}")
    
    # Correlacao predito vs real
    if len(y_pred_reg) > 3:
        corr, pval = stats.pearsonr(y_reg_clean, y_pred_reg)
        print(f"  Corr(pred, real): {corr:.4f} (p={pval:.6f})")

# Feature importance para regressao
rf_reg = RandomForestRegressor(n_estimators=500, max_depth=8, random_state=GLOBAL_SEED)
rf_reg.fit(X_reg, y_reg_clean)

imp_reg = pd.DataFrame({
    "feature": feature_cols,
    "importance": rf_reg.feature_importances_
}).sort_values("importance", ascending=False)
print(f"\nFeature Importance (Regression - GDP Growth predictors):")
print(imp_reg.to_string(index=False))

# ========== 5. DETECCAO DE ANOMALIAS ==========
print("\n\n[5] DETECCAO DE ANOMALIAS")
print("-" * 60)

# Isolation Forest
iso_forest = IsolationForest(contamination=0.1, random_state=GLOBAL_SEED)
anomaly_labels = iso_forest.fit_predict(X_scaled)
anomaly_scores = iso_forest.decision_function(X_scaled)

# Anomalies = -1
anomalies = anomaly_labels == -1
print(f"Anomalias detectadas: {anomalies.sum()} / {len(anomalies)}")

# Top anomalies
anomaly_df = pd.DataFrame({
    "economy": economy_names,
    "country": country_names,
    "anomaly_score": anomaly_scores,
    "is_anomaly": anomalies,
    "arm_trapped": y_class,
    "gdp_growth": y_reg,
    "ai_readiness": df_ml["ai_readiness"].values,
})
anomaly_df = anomaly_df.sort_values("anomaly_score")

print(f"\nTop 15 anomalias (mais negativas = mais anomalo):")
for _, row in anomaly_df.head(15).iterrows():
    print(f"  {row['country']:35s} score={row['anomaly_score']:.3f} "
          f"ARM={int(row['arm_trapped'])} growth={row['gdp_growth']:.1f}%")

# Anomalias "positivas" — paises que crescem muito apesar de baixa prontidao
print(f"\nTop 15 outliers positivos (crescem apesar de baixo AI Readiness):")
df_temp = df_ml.copy()
df_temp["anomaly_score"] = anomaly_scores
df_temp["economy"] = economy_names
pos_outliers = df_temp.nsmallest(30, "ai_readiness").nsmallest(15, "gdp_growth", "keep")  
# Actually let me redo this
pos_outliers = df_temp.sort_values("gdp_growth", ascending=False).head(15)
for _, row in pos_outliers.iterrows():
    print(f"  {row['economy']:35s} growth={row['gdp_growth']:.1f}% "
          f"ai_readiness={row['ai_readiness']:.1f} internet={row.get('internet_users', 0):.0f}%")

# ========== 6. CLUSTERING — PADROES DE DESENVOLVIMENTO ==========
print("\n\n[6] CLUSTERING — Padroes de Desenvolvimento")
print("-" * 60)

# KMeans para encontrar grupos naturais
kmeans = KMeans(n_clusters=4, random_state=GLOBAL_SEED, n_init=10)
clusters = kmeans.fit_predict(X_scaled)

cluster_df = pd.DataFrame({
    "economy": economy_names,
    "cluster": clusters,
    "gdp_per_capita": df_ml["gdp_per_capita"].values,
    "ai_readiness": df_ml["ai_readiness"].values,
    "arm_trapped": y_class,
})

print(f"\nPerfil dos clusters ({kmeans.n_clusters} grupos):")
for c in range(kmeans.n_clusters):
    c_data = cluster_df[cluster_df["cluster"] == c]
    print(f"\nCluster {c}: {len(c_data)} paises")
    print(f"  GDP medio: {c_data['gdp_per_capita'].mean():.0f}")
    print(f"  AI Readiness medio: {c_data['ai_readiness'].mean():.1f}")
    print(f"  ARM trapped: {c_data['arm_trapped'].sum()}")
    print(f"  Exemplos: {', '.join(c_data['economy'].head(5).tolist())}")

# ========== 7. CORRELACOES AVANCADAS ==========
print("\n\n[7] CORRELACOES AVANCADAS")
print("-" * 60)

# Matriz de correlacao com features selecionadas
corr_features = feature_cols + ["arm_trapped", "gdp_growth"]
corr_df = df_ml[corr_features].copy()

# Remover colunas totalmente NaN para correlacao
corr_df = corr_df.dropna(axis=1, how="all")
corr_matrix = corr_df.corr(method="pearson")

print("Correlacoes com ARM (target):")
arm_corr = corr_matrix["arm_trapped"].drop("arm_trapped").sort_values(ascending=False)
for feat, val in arm_corr.items():
    stars = "*" * (abs(val) > 0.1) + "*" * (abs(val) > 0.2) + "*" * (abs(val) > 0.3)
    print(f"  {feat:25s}  r={val:+.4f}  {stars}")

print(f"\nCorrelacoes com GDP Growth:")
growth_corr = corr_matrix["gdp_growth"].drop("gdp_growth").sort_values(ascending=False)
for feat, val in growth_corr.items():
    stars = "*" * (abs(val) > 0.1) + "*" * (abs(val) > 0.2) + "*" * (abs(val) > 0.3)
    print(f"  {feat:25s}  r={val:+.4f}  {stars}")

# Correlacao parcial — controlando por GDP per capita
print(f"\nCorrelacao parcial (controlando por GDP per capita):")
from sklearn.linear_model import LinearRegression

def partial_corr(x_col, y_col, control_col, data):
    """Correlacao parcial: correlacao entre x e y apos remover efeito de control"""
    x = data[x_col].values
    y = data[y_col].values
    c = data[control_col].values.reshape(-1, 1)
    
    # Remover efeito de control em x
    lr_x = LinearRegression().fit(c[~np.isnan(x) & ~np.isnan(y)], x[~np.isnan(x) & ~np.isnan(y)].reshape(-1, 1))
    x_resid = x[~np.isnan(x) & ~np.isnan(y)] - lr_x.predict(c[~np.isnan(x) & ~np.isnan(y)]).flatten()
    
    # Remover efeito de control em y  
    lr_y = LinearRegression().fit(c[~np.isnan(x) & ~np.isnan(y)], y[~np.isnan(x) & ~np.isnan(y)])
    y_resid = y[~np.isnan(x) & ~np.isnan(y)] - lr_y.predict(c[~np.isnan(x) & ~np.isnan(y)])
    
    if len(x_resid) > 3:
        r, p = stats.pearsonr(x_resid, y_resid)
        return r, p
    return np.nan, np.nan

for feat in ["ai_readiness", "internet_users", "tertiary_enrollment"]:
    if feat in df_ml.columns:
        r, p = partial_corr(feat, "arm_trapped", "gdp_per_capita", df_ml)
        if not np.isnan(r):
            print(f"  {feat:25s} x ARM | GDP: r={r:+.4f} (p={p:.4f})")
        r2, p2 = partial_corr(feat, "gdp_growth", "gdp_per_capita", df_ml)
        if not np.isnan(r2):
            print(f"  {feat:25s} x Growth | GDP: r={r2:+.4f} (p={p2:.4f})")

# ========== 8. TESTES ESTATISTICOS ==========
print("\n\n[8] TESTES ESTATISTICOS")
print("-" * 60)

# Teste t: diferenca entre ARM e nao-ARM para cada feature
print("Teste t (ARM vs Nao-ARM) para cada feature:")
for feat in feature_cols:
    if feat not in df_ml.columns:
        continue
    arm_group = df_ml[df_ml["arm_trapped"] == 1][feat].dropna()
    no_arm_group = df_ml[df_ml["arm_trapped"] == 0][feat].dropna()
    
    if len(arm_group) > 1 and len(no_arm_group) > 1:
        t_stat, p_val = stats.ttest_ind(arm_group, no_arm_group, equal_var=False)
        cohens_d = (arm_group.mean() - no_arm_group.mean()) / np.sqrt(
            (arm_group.std()**2 + no_arm_group.std()**2) / 2
        )
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        print(f"  {feat:25s}  t={t_stat:+6.2f}  p={p_val:.4f}  d={cohens_d:.3f}  {sig}")
        print(f"           ARM media={arm_group.mean():.2f} vs Nao-ARM media={no_arm_group.mean():.2f}")

# Bootstrap para intervalo de confianca das correlacoes
print(f"\nBootstrap 95% CI para correlacoes principais:")
n_bootstrap = 1000
np.random.seed(GLOBAL_SEED)

for feat in ["ai_readiness", "internet_users", "gdp_per_capita"]:
    if feat not in df_ml.columns:
        continue
    data = df_ml[[feat, "arm_trapped"]].dropna()
    boot_corrs = []
    for _ in range(n_bootstrap):
        idx = np.random.randint(0, len(data), len(data))
        sample = data.iloc[idx]
        boot_corrs.append(sample.corr().iloc[0, 1])
    
    boot_corrs = sorted(boot_corrs)
    ci_low, ci_high = boot_corrs[25], boot_corrs[974]
    print(f"  r({feat}, ARM): {np.mean(boot_corrs):.3f}  "
          f"95%CI=[{ci_low:.3f}, {ci_high:.3f}]")

# ========== 9. SALVAR RESULTADOS ==========
print(f"\n\n[9] Salvando resultados...")

results = {
    "metadata": {
        "script_hash": SCRIPT_HASH,
        "seed": GLOBAL_SEED,
        "timestamp": datetime.now().isoformat(),
        "n_samples": len(X),
        "n_features": len(feature_cols),
        "n_arm": int(y_class.sum()),
        "n_non_arm": int(len(y_class) - y_class.sum()),
    },
    "classification": results_class,
    "regression": results_reg,
    "feature_importance": importances.to_dict("records"),
    "feature_importance_regression": imp_reg.to_dict("records"),
    "anomalies": {
        "n_anomalies": int(anomalies.sum()),
        "top_anomalies": anomaly_df.head(20).to_dict("records"),
    },
    "cluster_profiles": {
        str(c): {"n": int(len(cluster_df[cluster_df["cluster"] == c])),
                 "gdp_mean": float(cluster_df[cluster_df["cluster"] == c]["gdp_per_capita"].mean()),
                 "ai_mean": float(cluster_df[cluster_df["cluster"] == c]["ai_readiness"].mean()),
                 "arm_count": int(cluster_df[cluster_df["cluster"] == c]["arm_trapped"].sum())}
        for c in range(kmeans.n_clusters)
    },
    "correlations": {
        "arm": arm_corr.to_dict(),
        "growth": growth_corr.to_dict(),
    },
}

with open(os.path.join(OUTPUT_DIR, "resultados_ml.json"), "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False, default=str)

# Salvar datasets processados
anomaly_df.to_csv(os.path.join(OUTPUT_DIR, "anomalias.csv"), index=False)
cluster_df.to_csv(os.path.join(OUTPUT_DIR, "clusters.csv"), index=False)
importances.to_csv(os.path.join(OUTPUT_DIR, "feature_importance.csv"), index=False)

print(f"Resultados salvos em: {OUTPUT_DIR}")
print(f"\n{'='*70}")
print("FASE 2 CONCLUIDA!")
print(f"{'='*70}")
