import pandas as pd, numpy as np, os, sys, json, warnings, hashlib
from datetime import datetime

# ========== CONFIG REPRODUTIVEL ==========
GLOBAL_SEED = 42
np.random.seed(GLOBAL_SEED)
SCRIPT_HASH = hashlib.sha256(open(__file__, "rb").read()).hexdigest()[:12]
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
for _mod in ['sklearn', 'scipy']:
    __import__(_mod)

print("=" * 70)
print("FASE 2 — PIPELINE ML COMPLETO v2")
print(f"Seed: {GLOBAL_SEED} | Script Hash: {SCRIPT_HASH}")
print(f"Execucao: {datetime.now().isoformat()}")
print("=" * 70)

# ========== 1. CARREGAR E PRE-PROCESSAR ==========
print("\n[1] Carregando e preparando dados...")
df = pd.read_csv(os.path.join(OUTPUT_DIR, "dataset_latest.csv"))
print(f"Shape raw: {df.shape}")

feature_cols = [
    "gdp_per_capita", "tertiary_enrollment", "rd_spending",
    "patent_apps", "high_tech_exp", "internet_users",
    "fdi_inflows", "unemployment", "gini", "services_emp",
    "ai_readiness"
]
target_class = "arm_trapped"  # strict ARM (0/1)
target_reg = "gdp_growth"     # continuous

# Contar casos ARM antes de qualquer filtro
print(f"ARM strict: {int(df['arm_trapped'].sum())} trapped / {df['arm_trapped'].notna().sum()} classified")

# ---- Imputacao por mediana ----
df_imp = df.copy()
for col in feature_cols:
    if col in df_imp.columns:
        median_val = df_imp[col].median()
        df_imp[col] = df_imp[col].fillna(median_val)
        # Flag de imputacao para diagnostico
        flag_col = f"{col}_was_nan"
        df_imp[flag_col] = df[col].isna().astype(int)

# ---- Classificacao ARM RELATIVA ----
# Bottom 20% do crescimento entre paises de renda media
df_imp["is_middle_income"] = (
    df_imp["gdp_per_capita"].between(1136, 13845)
)
mid_inc = df_imp[df_imp["is_middle_income"]]
threshold = mid_inc["gdp_growth"].quantile(0.20)
df_imp["arm_relative"] = (
    df_imp["is_middle_income"] & 
    (df_imp["gdp_growth"] <= threshold)
).astype(int)
print(f"ARM relativo (bottom 20% growth, middle-income): "
      f"{df_imp['arm_relative'].sum()} / {len(df_imp)}")

# ---- Dataset final para ML ----
keep_cols = feature_cols + [target_class, target_reg, "arm_relative", "economy", "name", "income_level"]
keep_cols = [c for c in keep_cols if c in df_imp.columns]
df_ml = df_imp[keep_cols].copy()

# Drop NaN em target apenas
df_ml = df_ml.dropna(subset=[target_reg], how="any")
print(f"Shape apos dropna target: {df_ml.shape}")

X = df_ml[feature_cols].values
y_class_strict = df_ml[target_class].fillna(0).astype(int).values
y_class_rel = df_ml["arm_relative"].values
y_reg = df_ml[target_reg].values
economy_names = df_ml["economy"].values

print(f"\nX: {X.shape}")
print(f"y_class_strict: {y_class_strict.sum()} trapped / {len(y_class_strict)}")
print(f"y_class_relative: {y_class_rel.sum()} trapped / {len(y_class_rel)}")
print(f"y_reg: mean={y_reg.mean():.2f}%, std={y_reg.std():.2f}%")

# ========== 2. IMPORTACOES ML ==========
print("\n[2] Importando bibliotecas ML...")
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.model_selection import (
    cross_val_score, cross_val_predict, StratifiedKFold, KFold,
    train_test_split
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, r2_score, mean_squared_error, mean_absolute_error
)
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from scipy import stats
import warnings; warnings.filterwarnings("ignore")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ========== 3. CLASSIFICACAO (RELATIVA) ==========
print("\n[3] CLASSIFICACAO — ARM Relativo (bottom 20% growth)")
print("-" * 60)

if y_class_rel.sum() >= 3:
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=GLOBAL_SEED)
    
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=GLOBAL_SEED, class_weight="balanced"),
        "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=8, random_state=GLOBAL_SEED, class_weight="balanced"),
    }
    
    results_class = {}
    for name, model in models.items():
        try:
            scores_acc = cross_val_score(model, X_scaled, y_class_rel, cv=skf, scoring="accuracy")
            scores_f1 = cross_val_score(model, X_scaled, y_class_rel, cv=skf, scoring="f1")
            scores_auc = cross_val_score(model, X_scaled, y_class_rel, cv=skf, scoring="roc_auc")
            y_pred = cross_val_predict(model, X_scaled, y_class_rel, cv=skf)
            
            results_class[name] = {
                "accuracy": round(scores_acc.mean(), 4),
                "accuracy_std": round(scores_acc.std(), 4),
                "f1": round(scores_f1.mean(), 4),
                "f1_std": round(scores_f1.std(), 4),
                "roc_auc": round(scores_auc.mean(), 4),
                "roc_auc_std": round(scores_auc.std(), 4),
                "precision": round(precision_score(y_class_rel, y_pred, zero_division=0), 4),
                "recall": round(recall_score(y_class_rel, y_pred, zero_division=0), 4),
            }
            
            print(f"\n{name}:")
            print(f"  Acc: {scores_acc.mean():.4f}+-{scores_acc.std():.4f}")
            print(f"  F1:  {scores_f1.mean():.4f}+-{scores_f1.std():.4f}")
            print(f"  AUC: {scores_auc.mean():.4f}+-{scores_auc.std():.4f}")
            print(f"  Prec: {results_class[name]['precision']:.4f} Rec: {results_class[name]['recall']:.4f}")
            
            cm = confusion_matrix(y_class_rel, y_pred)
            print(f"  CM: TN={cm[0,0]} FP={cm[0,1]} FN={cm[1,0]} TP={cm[1,1]}")
            
            # AUC warning handling
        except Exception as e:
            print(f"  {name}: ERRO - {str(e)[:80]}")
            results_class = {}
else:
    print("Amostras ARM relativo insuficientes para classificacao")
    results_class = {}

# Feature Importance
rf_class = RandomForestClassifier(n_estimators=500, max_depth=8, random_state=GLOBAL_SEED, class_weight="balanced")
rf_class.fit(X_scaled, y_class_rel)

importances = pd.DataFrame({
    "feature": feature_cols,
    "importance_rf": rf_class.feature_importances_
}).sort_values("importance_rf", ascending=False)

print(f"\nFeature Importance (RF Classification):")
print(importances.to_string(index=False))

# Permutation importance
perm_imp = permutation_importance(rf_class, X_scaled, y_class_rel, n_repeats=20, random_state=GLOBAL_SEED)
importances["importance_perm"] = perm_imp.importances_mean
importances["importance_perm_std"] = perm_imp.importances_std
print(f"\nPermutation Importance:")
print(importances.sort_values("importance_perm", ascending=False).to_string(index=False))

# ========== 4. REGRESSAO ==========
print("\n\n[4] REGRESSAO — Previsao de GDP Growth")
print("-" * 60)

kf = KFold(n_splits=5, shuffle=True, random_state=GLOBAL_SEED)

reg_models = {
    "Linear Regression": LinearRegression(),
    "Ridge (alpha=1)": Ridge(alpha=1.0, random_state=GLOBAL_SEED),
    "Random Forest": RandomForestRegressor(n_estimators=200, max_depth=8, random_state=GLOBAL_SEED),
}

results_reg = {}
for name, model in reg_models.items():
    try:
        scores_r2 = cross_val_score(model, X_scaled, y_reg, cv=kf, scoring="r2")
        y_pred_reg = cross_val_predict(model, X_scaled, y_reg, cv=kf)
        
        results_reg[name] = {
            "r2": round(scores_r2.mean(), 4),
            "r2_std": round(scores_r2.std(), 4),
            "rmse": round(np.sqrt(mean_squared_error(y_reg, y_pred_reg)), 4),
            "mae": round(mean_absolute_error(y_reg, y_pred_reg), 4),
        }
        
        print(f"\n{name}:")
        print(f"  R2:   {scores_r2.mean():+.4f} +- {scores_r2.std():.4f}")
        print(f"  RMSE: {results_reg[name]['rmse']:.4f}")
        print(f"  MAE:  {results_reg[name]['mae']:.4f}")
        
        if len(y_pred_reg) > 3:
            corr, pval = stats.pearsonr(y_reg, y_pred_reg)
            print(f"  Corr(pred,real): r={corr:.4f} (p={pval:.6f})")
    except Exception as e:
        print(f"{name}: ERRO - {str(e)[:80]}")

# Feature importance for regression
rf_reg = RandomForestRegressor(n_estimators=500, max_depth=8, random_state=GLOBAL_SEED)
rf_reg.fit(X_scaled, y_reg)

imp_reg = pd.DataFrame({
    "feature": feature_cols,
    "importance": rf_reg.feature_importances_
}).sort_values("importance", ascending=False)
print(f"\nFeature Importance (Regression):")
print(imp_reg.to_string(index=False))

# ========== 5. DETECCAO DE ANOMALIAS ==========
print("\n\n[5] DETECCAO DE ANOMALIAS")
print("-" * 60)

iso_forest = IsolationForest(contamination=0.1, random_state=GLOBAL_SEED)
anomaly_labels = iso_forest.fit_predict(X_scaled)
anomaly_scores = iso_forest.decision_function(X_scaled)

anomalies = anomaly_labels == -1
print(f"Anomalias: {anomalies.sum()} / {len(anomalies)}")

anomaly_df = pd.DataFrame({
    "economy": economy_names,
    "anomaly_score": anomaly_scores,
    "is_anomaly": anomalies,
    "arm_strict": y_class_strict,
    "arm_relative": y_class_rel,
    "gdp_growth": y_reg,
    "ai_readiness": df_ml["ai_readiness"].values,
})
anomaly_df = anomaly_df.sort_values("anomaly_score")

print(f"\nTop 15 anomalias (mais negativas = mais anomalo):")
for _, row in anomaly_df.head(15).iterrows():
    print(f"  {row['economy']:35s} score={row['anomaly_score']:.3f} "
          f"ARM_rel={row['arm_relative']} growth={row['gdp_growth']:.1f}%")

print(f"\nTop 15 anomalias POSITIVAS (crescem apesar de baixa prontidao):")
anomaly_pos = anomaly_df.sort_values("anomaly_score", ascending=False).head(15)
for _, row in anomaly_pos.iterrows():
    print(f"  {row['economy']:35s} score={row['anomaly_score']:.3f} "
          f"growth={row['gdp_growth']:.1f}% AI={row['ai_readiness']:.1f}")

# ========== 6. CLUSTERING ==========
print("\n\n[6] CLUSTERING")
print("-" * 60)

kmeans = KMeans(n_clusters=4, random_state=GLOBAL_SEED, n_init=10)
clusters = kmeans.fit_predict(X_scaled)

cluster_df = pd.DataFrame({
    "economy": economy_names,
    "cluster": clusters,
    "gdp_per_capita": df_ml["gdp_per_capita"].values,
    "ai_readiness": df_ml["ai_readiness"].values,
    "gdp_growth": y_reg,
    "arm_relative": y_class_rel,
})

print(f"Perfil dos clusters:")
for c in range(kmeans.n_clusters):
    c_data = cluster_df[cluster_df["cluster"] == c]
    print(f"\nCluster {c}: {len(c_data)} paises")
    print(f"  GDP medio: {c_data['gdp_per_capita'].mean():.0f}")
    print(f"  AI Readiness medio: {c_data['ai_readiness'].mean():.1f}")
    print(f"  Growth medio: {c_data['gdp_growth'].mean():.1f}%")
    print(f"  ARM relativo: {c_data['arm_relative'].sum()}")
    print(f"  Exemplos: {', '.join(c_data['economy'].head(5).tolist())}")

# ========== 7. CORRELACOES AVANCADAS ==========
print("\n\n[7] CORRELACOES")
print("-" * 60)

corr_df = df_ml[feature_cols + [target_reg, "arm_relative"]].copy()
corr_matrix = corr_df.corr(method="pearson")

print("Correlacoes com GDP Growth:")
growth_corr = corr_matrix["gdp_growth"].drop("gdp_growth").sort_values(ascending=False)
for feat, val in growth_corr.items():
    sig = "***" if abs(val) > 0.3 else "**" if abs(val) > 0.2 else "*" if abs(val) > 0.1 else ""
    print(f"  {feat:25s}  r={val:+.4f}  {sig}")

print(f"\nCorrelacoes com ARM Relativo:")
arm_corr = corr_matrix["arm_relative"].drop("arm_relative").sort_values(ascending=False)
for feat, val in arm_corr.items():
    sig = "***" if abs(val) > 0.3 else "**" if abs(val) > 0.2 else "*" if abs(val) > 0.1 else ""
    print(f"  {feat:25s}  r={val:+.4f}  {sig}")

# Correlacao parcial (controlando por GDP per capita)
print(f"\nCorrelacao parcial (controlando por GDP per capita):")
from sklearn.linear_model import LinearRegression

def partial_corr(x_col, y_col, control_col, data):
    ctrl = data[control_col].values.reshape(-1, 1)
    mask = data[[x_col, y_col, control_col]].notna().all(axis=1)
    x, y, c = data.loc[mask, x_col].values, data.loc[mask, y_col].values, ctrl[mask]
    if len(x) < 10: return np.nan, np.nan
    lr_x = LinearRegression().fit(c, x.reshape(-1, 1))
    x_resid = x - lr_x.predict(c).flatten()
    lr_y = LinearRegression().fit(c, y)
    y_resid = y - lr_y.predict(c)
    return stats.pearsonr(x_resid, y_resid)

for feat in ["ai_readiness", "internet_users", "tertiary_enrollment", "rd_spending"]:
    r, p = partial_corr(feat, "gdp_growth", "gdp_per_capita", df_ml)
    if not np.isnan(r):
        print(f"  r({feat}, Growth | GDP): {r:+.4f} (p={p:.4f})")
    r2, p2 = partial_corr(feat, "arm_relative", "gdp_per_capita", df_ml)
    if not np.isnan(r2):
        print(f"  r({feat}, ARM_rel | GDP): {r2:+.4f} (p={p2:.4f})")

# ========== 8. TESTES ESTATISTICOS ==========
print("\n\n[8] TESTES ESTATISTICOS")
print("-" * 60)

# Teste t: ARM_rel vs Nao-ARM_rel
print("Teste t (ARM_rel vs Nao-ARM_rel) para cada feature:")
for feat in feature_cols:
    arm_g = df_ml[df_ml["arm_relative"] == 1][feat].dropna()
    no_g = df_ml[df_ml["arm_relative"] == 0][feat].dropna()
    if len(arm_g) > 1 and len(no_g) > 1:
        t_stat, p_val = stats.ttest_ind(arm_g, no_g, equal_var=False)
        cohens_d = (arm_g.mean() - no_g.mean()) / np.sqrt(
            (arm_g.std()**2 + no_g.std()**2) / 2
        )
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        print(f"  {feat:25s} t={t_stat:+6.2f} p={p_val:.4f} d={cohens_d:.3f} {sig}")
        print(f"    ARM media={arm_g.mean():.2f} vs Nao-ARM media={no_g.mean():.2f}")

# Bootstrap 95% CI
print(f"\nBootstrap 95% CI (n=1000):")
n_bootstrap = 1000
np.random.seed(GLOBAL_SEED)

for feat in ["ai_readiness", "internet_users", "gdp_per_capita", "tertiary_enrollment"]:
    for target in ["gdp_growth", "arm_relative"]:
        colname = f"{feat}_{target}"
        data = df_ml[[feat, target]].dropna()
        if len(data) < 10:
            continue
        boot_corrs = []
        for _ in range(n_bootstrap):
            idx = np.random.randint(0, len(data), len(data))
            sample = data.iloc[idx]
            boot_corrs.append(sample.corr().iloc[0, 1])
        boot_corrs = sorted(boot_corrs)
        ci_low, ci_high = boot_corrs[25], boot_corrs[974]
        print(f"  r({feat},{target}): {np.mean(boot_corrs):.3f} [95%CI: {ci_low:.3f}, {ci_high:.3f}]")

# ========== 9. RESULTADOS STRICT ARM (para comparacao) ==========
if y_class_strict.sum() >= 2:
    print(f"\n\n[8b] TESTE T — ARM Strict (n={y_class_strict.sum()}) vs Nao-ARM")
    print("-" * 60)
    for feat in feature_cols:
        arm_g = df_ml[df_ml[target_class] == 1][feat].dropna()
        no_g = df_ml[df_ml[target_class] == 0][feat].dropna()
        if len(arm_g) > 0 and len(no_g) > 1:
            t_stat, p_val = stats.ttest_ind(arm_g, no_g, equal_var=False)
            print(f"  {feat:25s} t={t_stat:+6.2f} p={p_val:.4f}")
            print(f"    ARM media={arm_g.mean():.2f} (n={len(arm_g)}) vs Nao-ARM media={no_g.mean():.2f}")

# ========== 10. SALVAR ==========
print(f"\n\n[9] Salvando...")

results = {
    "metadata": {
        "script_hash": SCRIPT_HASH,
        "seed": GLOBAL_SEED,
        "timestamp": datetime.now().isoformat(),
        "n_samples": len(X),
        "n_features": len(feature_cols),
        "n_arm_strict": int(y_class_strict.sum()),
        "n_arm_relative": int(y_class_rel.sum()),
    },
    "classification": results_class if results_class else {},
    "regression": results_reg,
    "feature_importance": importances.to_dict("records"),
    "feature_importance_regression": imp_reg.to_dict("records"),
    "anomalies": {
        "n_anomalies": int(anomalies.sum()),
        "top_anomalies": anomaly_df.head(20).to_dict("records"),
    },
    "cluster_profiles": {
        str(c): {
            "n": int(len(cluster_df[cluster_df["cluster"] == c])),
            "gdp_mean": float(cluster_df[cluster_df["cluster"] == c]["gdp_per_capita"].mean()),
            "ai_mean": float(cluster_df[cluster_df["cluster"] == c]["ai_readiness"].mean()),
            "growth_mean": float(cluster_df[cluster_df["cluster"] == c]["gdp_growth"].mean()),
            "arm_count": int(cluster_df[cluster_df["cluster"] == c]["arm_relative"].sum()),
        } for c in range(kmeans.n_clusters)
    },
}

with open(os.path.join(OUTPUT_DIR, "resultados_ml_v2.json"), "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False, default=str)

anomaly_df.to_csv(os.path.join(OUTPUT_DIR, "anomalias_v2.csv"), index=False)
cluster_df.to_csv(os.path.join(OUTPUT_DIR, "clusters_v2.csv"), index=False)
importances.to_csv(os.path.join(OUTPUT_DIR, "feature_importance_v2.csv"), index=False)
df_ml.to_csv(os.path.join(OUTPUT_DIR, "dataset_ml_v2.csv"), index=False)

print(f"Salvo em: {OUTPUT_DIR}")
print(f"\n{'='*70}")
print("FASE 2 CONCLUIDA!")
print(f"{'='*70}")
