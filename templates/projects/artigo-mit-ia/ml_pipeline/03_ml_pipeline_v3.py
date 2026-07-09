import pandas as pd, numpy as np, os, sys, json, warnings, hashlib
from datetime import datetime

# ========== CONFIG REPRODUTIVEL ==========
GLOBAL_SEED = 42
np.random.seed(GLOBAL_SEED)
SCRIPT_HASH = hashlib.sha256(open(__file__, "rb").read()).hexdigest()[:12]
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "ml_pipeline", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
warnings.filterwarnings("ignore")

print("=" * 70)
print("FASE 3 — PIPELINE ML v3 (COMPLEXIDADE ECONOMICA)")
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
target_class = "arm_trapped"
target_reg = "gdp_growth"

# ---- Imputacao por mediana ----
df_imp = df.copy()
for col in feature_cols:
    if col in df_imp.columns:
        df_imp[col] = df_imp[col].fillna(df_imp[col].median())

# ---- ARM RELATIVA ----
df_imp["is_middle_income"] = df_imp["gdp_per_capita"].between(1136, 13845)
mid_inc = df_imp[df_imp["is_middle_income"]]
threshold = mid_inc["gdp_growth"].quantile(0.20)
df_imp["arm_relative"] = (
    df_imp["is_middle_income"] & 
    (df_imp["gdp_growth"] <= threshold)
).astype(int)
print(f"ARM relativo: {df_imp['arm_relative'].sum()} / {len(df_imp)}")

# ========== 2. COMPUTAR 3 NOVAS FEATURES DE COMPLEXIDADE ==========
print("\n[2] Computando 3 medidas de complexidade economica...")

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

# --- Feature 12: knowledge_complexity (KCI proxy via PCA) ---
# Usa features de inovacao: P&D, patentes, alta tecnologia, internet, ensino superior, prontidao IA
innovation_features = ["rd_spending", "patent_apps", "high_tech_exp", 
                       "internet_users", "tertiary_enrollment", "ai_readiness"]
innovation_data = df_imp[innovation_features].copy()
# Padronizar
scaler_innov = StandardScaler()
innovation_scaled = scaler_innov.fit_transform(innovation_data.fillna(innovation_data.median()))
# PCA
pca = PCA(n_components=1, random_state=GLOBAL_SEED)
kci_raw = pca.fit_transform(innovation_scaled)[:, 0]
# Inverter sinal se necessario (maior complexidade = maior score)
if np.corrcoef(kci_raw, df_imp["gdp_per_capita"].fillna(df_imp["gdp_per_capita"].median()))[0, 1] < 0:
    kci_raw = -kci_raw
df_imp["knowledge_complexity"] = (kci_raw - kci_raw.mean()) / kci_raw.std()
print(f"  knowledge_complexity: media={df_imp['knowledge_complexity'].mean():.4f}, "
      f"std={df_imp['knowledge_complexity'].std():.4f}, "
      f"var_explicada_PC1={pca.explained_variance_ratio_[0]:.2%}")
print(f"  Carga PC1: {dict(zip(innovation_features, pca.components_[0].round(3)))}")

# --- Feature 13: export_sophistication (EXPY proxy) ---
# PRODY-like: GDP per capita ponderado por intensidade tecnologica
# Quanto maior a proporcao de exportacao de alta tecnologia e patentes, maior a sofisticacao
# EXPY = w1*log(high_tech_exp+1) + w2*log(patent_apps+1) + w3*rd_spending
# Normalizado pelo GDP per capita para capturar "renda implícita" das exportacoes
tech_features = ["high_tech_exp", "patent_apps", "rd_spending"]
tech_weights = np.array([0.4, 0.35, 0.25])  # Pesos baseados na literatura (Hausmann et al., 2007)

expy_raw = np.zeros(len(df_imp))
for i, feat in enumerate(tech_features):
    vals = df_imp[feat].fillna(df_imp[feat].median()).values
    # Log-transform para lidar com assimetria
    vals_log = np.log1p(np.maximum(vals, 0))
    expy_raw += tech_weights[i] * vals_log

# Interacao com GDP per capita (produtos sofisticados em paises ricos = maior EXPY)
gdp_log = np.log1p(df_imp["gdp_per_capita"].fillna(df_imp["gdp_per_capita"].median()).values)
expy_interact = expy_raw * gdp_log

df_imp["export_sophistication"] = (expy_interact - expy_interact.mean()) / expy_interact.std()
print(f"  export_sophistication: media={df_imp['export_sophistication'].mean():.4f}, "
      f"std={df_imp['export_sophistication'].std():.4f}")

# --- Feature 14: product_density (Densidade Produtiva) ---
# Similaridade cosseno do perfil do pais com a "fronteira tecnologica" (top 10% GDP per capita)
# Adaptado de Hidalgo et al. (2007) - Product Space density
# Quanto mais similar o perfil de um pais ao da fronteira, maior a densidade

all_features_for_density = feature_cols.copy()
density_data = df_imp[all_features_for_density].fillna(df_imp[all_features_for_density].median())
scaler_density = StandardScaler()
density_scaled = scaler_density.fit_transform(density_data)

# Definir fronteira: top 10% GDP per capita
gdp_values = df_imp["gdp_per_capita"].fillna(df_imp["gdp_per_capita"].median()).values
frontier_threshold = np.percentile(gdp_values, 90)
frontier_mask = gdp_values >= frontier_threshold

if frontier_mask.sum() > 0:
    frontier_profile = density_scaled[frontier_mask].mean(axis=0).reshape(1, -1)
    similarities = cosine_similarity(density_scaled, frontier_profile).flatten()
    df_imp["product_density"] = (similarities - similarities.min()) / (similarities.max() - similarities.min() + 1e-10)
else:
    df_imp["product_density"] = 0.0

print(f"  product_density: media={df_imp['product_density'].mean():.4f}, "
      f"std={df_imp['product_density'].std():.4f}, "
      f"fronteira (P90): {frontier_threshold:.0f}, n_paises_fronteira={frontier_mask.sum()}")

# --- Correlacao das novas features com targets ---
new_features = ["knowledge_complexity", "export_sophistication", "product_density"]
print(f"\nCorrelacao das novas features com targets:")
for feat in new_features:
    for tgt in ["gdp_growth", "arm_relative"]:
        valid = df_imp[[feat, tgt]].dropna()
        if len(valid) > 5:
            r = valid[feat].corr(valid[tgt])
            print(f"  {feat:25s} vs {tgt:15s}: r={r:+.4f}")

# ========== 3. DATASET FINAL ==========
new_feature_cols = feature_cols + new_features
keep_cols = new_feature_cols + [target_class, target_reg, "arm_relative", "economy", "name", "income_level"]
keep_cols = [c for c in keep_cols if c in df_imp.columns]
df_ml = df_imp[keep_cols].copy()
df_ml = df_ml.dropna(subset=[target_reg], how="any")
print(f"\nDataset ML v3: {df_ml.shape}")

X = df_ml[new_feature_cols].values
y_class_strict = df_ml[target_class].fillna(0).astype(int).values
y_class_rel = df_ml["arm_relative"].values
y_reg = df_ml[target_reg].values
economy_names = df_ml["economy"].values

# ========== 4. IMPORTACOES E PIPELINE ML ==========
print("\n[3] Pipeline ML com 14 features...")
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.model_selection import (
    cross_val_score, cross_val_predict, StratifiedKFold, KFold
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, r2_score, mean_squared_error, mean_absolute_error
)
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA as PCA_vis
from scipy import stats

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ========== 5. CLASSIFICACAO ==========
print("\n[4] CLASSIFICACAO — ARM Relativo (14 features)")
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
            
            cm = confusion_matrix(y_class_rel, y_pred)
            print(f"  CM: TN={cm[0,0]} FP={cm[0,1]} FN={cm[1,0]} TP={cm[1,1]}")
        except Exception as e:
            print(f"  {name}: ERRO - {str(e)[:80]}")
else:
    results_class = {}

# Feature Importance
rf_class = RandomForestClassifier(n_estimators=500, max_depth=8, random_state=GLOBAL_SEED, class_weight="balanced")
rf_class.fit(X_scaled, y_class_rel)

importances = pd.DataFrame({
    "feature": new_feature_cols,
    "importance_rf": rf_class.feature_importances_
}).sort_values("importance_rf", ascending=False)

print(f"\nFeature Importance (RF Classification, 14 features):")
print(importances.to_string(index=False))

perm_imp = permutation_importance(rf_class, X_scaled, y_class_rel, n_repeats=20, random_state=GLOBAL_SEED)
importances["importance_perm"] = perm_imp.importances_mean
importances["importance_perm_std"] = perm_imp.importances_std

# ========== 6. REGRESSAO ==========
print("\n\n[5] REGRESSAO — Previsao de GDP Growth (14 features)")
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
        print(f"\n{name}:  R2={scores_r2.mean():+.4f} RMSE={results_reg[name]['rmse']:.4f}")
    except Exception as e:
        print(f"{name}: ERRO - {str(e)[:80]}")

rf_reg = RandomForestRegressor(n_estimators=500, max_depth=8, random_state=GLOBAL_SEED)
rf_reg.fit(X_scaled, y_reg)
imp_reg = pd.DataFrame({
    "feature": new_feature_cols,
    "importance": rf_reg.feature_importances_
}).sort_values("importance", ascending=False)

# ========== 7. ANOMALIAS ==========
print("\n\n[6] DETECCAO DE ANOMALIAS")
iso_forest = IsolationForest(contamination=0.1, random_state=GLOBAL_SEED)
anomaly_labels = iso_forest.fit_predict(X_scaled)
anomaly_scores = iso_forest.decision_function(X_scaled)
anomalies = anomaly_labels == -1
print(f"Anomalias: {anomalies.sum()} / {len(anomalies)}")

anomaly_df = pd.DataFrame({
    "economy": economy_names,
    "anomaly_score": anomaly_scores,
    "is_anomaly": anomalies,
    "arm_relative": y_class_rel,
    "gdp_growth": y_reg,
    "knowledge_complexity": df_ml["knowledge_complexity"].values,
    "product_density": df_ml["product_density"].values,
}).sort_values("anomaly_score")

# ========== 8. CLUSTERING ==========
print("\n[7] CLUSTERING (14 features)")
kmeans = KMeans(n_clusters=4, random_state=GLOBAL_SEED, n_init=10)
clusters = kmeans.fit_predict(X_scaled)
cluster_df = pd.DataFrame({
    "economy": economy_names,
    "cluster": clusters,
    "gdp_per_capita": df_ml["gdp_per_capita"].values,
    "knowledge_complexity": df_ml["knowledge_complexity"].values,
    "export_sophistication": df_ml["export_sophistication"].values,
    "product_density": df_ml["product_density"].values,
    "gdp_growth": y_reg,
    "arm_relative": y_class_rel,
})
for c in range(kmeans.n_clusters):
    c_data = cluster_df[cluster_df["cluster"] == c]
    print(f"\nCluster {c}: {len(c_data)} paises | GDP={c_data['gdp_per_capita'].mean():.0f} "
          f"KCI={c_data['knowledge_complexity'].mean():.2f} "
          f"Growth={c_data['gdp_growth'].mean():.1f}% ARM={c_data['arm_relative'].sum()}")

# ========== 9. CORRELACOES AVANCADAS ==========
print("\n\n[8] CORRELACOES — NOVAS FEATURES")
corr_df = df_ml[new_feature_cols + [target_reg, "arm_relative"]].corr(method="pearson")
for feat in new_features:
    for tgt in ["gdp_growth", "arm_relative"]:
        r = corr_df.loc[feat, tgt]
        print(f"  {feat:25s} vs {tgt:15s}: r={r:+.4f}")

# Correlacao parcial
from sklearn.linear_model import LinearRegression as LR
def partial_corr(x_col, y_col, control_col, data):
    ctrl = data[control_col].values.reshape(-1, 1)
    mask = data[[x_col, y_col, control_col]].notna().all(axis=1)
    x, y, c = data.loc[mask, x_col].values, data.loc[mask, y_col].values, ctrl[mask]
    if len(x) < 10: return np.nan, np.nan
    lr_x = LR().fit(c, x.reshape(-1, 1))
    x_resid = x - lr_x.predict(c).flatten()
    lr_y = LR().fit(c, y)
    y_resid = y - lr_y.predict(c)
    return stats.pearsonr(x_resid, y_resid)

print(f"\nCorrelacao parcial (controlando GDP per capita):")
for feat in new_features:
    r, p = partial_corr(feat, "gdp_growth", "gdp_per_capita", df_ml)
    if not np.isnan(r):
        print(f"  r({feat}, Growth | GDP): {r:+.4f} (p={p:.4f})")
    r2, p2 = partial_corr(feat, "arm_relative", "gdp_per_capita", df_ml)
    if not np.isnan(r2):
        print(f"  r({feat}, ARM_rel | GDP): {r2:+.4f} (p={p2:.4f})")

# ========== 10. CARREGAR V2 E COMPARAR ==========
print("\n\n[9] ANALISE DE GANHO v2 -> v3")
print("-" * 60)

v2_path = os.path.join(OUTPUT_DIR, "resultados_ml_v2.json")
v2_gain = {"accuracy_gain": {}, "auc_gain": {}, "regression_r2_gain": {}}

if os.path.exists(v2_path):
    with open(v2_path) as f:
        v2 = json.load(f)
    
    print("Comparacao de metricas (v2=11 features vs v3=14 features):")
    for model_name in ["Logistic Regression", "Random Forest"]:
        v2_acc = v2.get("classification", {}).get(model_name, {}).get("accuracy", 0)
        v3_acc = results_class.get(model_name, {}).get("accuracy", 0)
        v2_auc = v2.get("classification", {}).get(model_name, {}).get("roc_auc", 0)
        v3_auc = results_class.get(model_name, {}).get("roc_auc", 0)
        acc_gain = v3_acc - v2_acc
        auc_gain = v3_auc - v2_auc
        v2_gain["accuracy_gain"][model_name] = round(acc_gain, 4)
        v2_gain["auc_gain"][model_name] = round(auc_gain, 4)
        print(f"\n  {model_name}:")
        print(f"    Accuracy: {v2_acc:.4f} (v2) -> {v3_acc:.4f} (v3) = {acc_gain:+.4f}")
        print(f"    ROC-AUC:  {v2_auc:.4f} (v2) -> {v3_auc:.4f} (v3) = {auc_gain:+.4f}")
    
    for model_name in ["Linear Regression", "Ridge (alpha=1)", "Random Forest"]:
        v2_r2 = v2.get("regression", {}).get(model_name, {}).get("r2", 0)
        v3_r2 = results_reg.get(model_name, {}).get("r2", 0)
        r2_gain = v3_r2 - v2_r2
        v2_gain["regression_r2_gain"][model_name] = round(r2_gain, 4)
        print(f"\n  {model_name} R2: {v2_r2:.4f} (v2) -> {v3_r2:.4f} (v3) = {r2_gain:+.4f}")
else:
    print("AVISO: resultados_ml_v2.json nao encontrado. Pulando comparacao.")

# ========== 11. SALVAR ==========
print(f"\n\n[10] Salvando resultados...")

results = {
    "metadata": {
        "script_hash": SCRIPT_HASH,
        "seed": GLOBAL_SEED,
        "timestamp": datetime.now().isoformat(),
        "n_samples": len(X),
        "n_features": len(new_feature_cols),
        "n_features_original": 11,
        "n_features_added": 3,
        "n_arm_strict": int(y_class_strict.sum()),
        "n_arm_relative": int(y_class_rel.sum()),
        "new_features": new_features,
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
            "kci_mean": float(cluster_df[cluster_df["cluster"] == c]["knowledge_complexity"].mean()),
            "expy_mean": float(cluster_df[cluster_df["cluster"] == c]["export_sophistication"].mean()),
            "density_mean": float(cluster_df[cluster_df["cluster"] == c]["product_density"].mean()),
            "growth_mean": float(cluster_df[cluster_df["cluster"] == c]["gdp_growth"].mean()),
            "arm_count": int(cluster_df[cluster_df["cluster"] == c]["arm_relative"].sum()),
        } for c in range(kmeans.n_clusters)
    },
    "new_features_v3": {
        feat: {
            "description": {
                "knowledge_complexity": "KCI proxy: PC1 de 6 features de inovacao",
                "export_sophistication": "EXPY proxy: PIBpc ponderado por sofisticacao exportadora",
                "product_density": "Densidade produtiva: similaridade cosseno a fronteira"
            }[feat],
            "mean": float(df_ml[feat].mean()),
            "std": float(df_ml[feat].std()),
        } for feat in new_features
    },
    "v3_gain_analysis": v2_gain,
}

# Salvar JSON
with open(os.path.join(OUTPUT_DIR, "resultados_ml_v3.json"), "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False, default=str)

# Salvar CSVs
anomaly_df.to_csv(os.path.join(OUTPUT_DIR, "anomalias_v3.csv"), index=False)
cluster_df.to_csv(os.path.join(OUTPUT_DIR, "clusters_v3.csv"), index=False)
importances.to_csv(os.path.join(OUTPUT_DIR, "feature_importance_v3.csv"), index=False)
df_ml.to_csv(os.path.join(OUTPUT_DIR, "dataset_ml_v3.csv"), index=False)

print(f"Resultados salvos em: {OUTPUT_DIR}")
print(f"\n{'='*70}")
print("FASE 3 CONCLUIDA!")
print(f"{'='*70}")
