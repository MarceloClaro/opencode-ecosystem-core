#!/usr/bin/env python3
"""análise QUANTITATIVA - ARM x IAG (DADOS REAIS WDI v2)"""
import numpy as np, pandas as pd, warnings, json, time
from pathlib import Path
warnings.filterwarnings("ignore")
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import ElasticNet, LinearRegression
from sklearn.model_selection import (cross_val_score, KFold, train_test_split, RepeatedKFold)
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from scipy.stats import pearsonr, spearmanr, f_oneway
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")
plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 300, "figure.figsize": (12, 8), "font.size": 10})
OUT = Path(__file__).parent / "output"
df_orig = pd.read_csv(OUT / "dataset_corte_transversal.csv")
df_painel = pd.read_csv(OUT / "dataset_painel_2016_2025.csv")
# Filter >=15 vars numeric
nc = [c for c in df_orig.select_dtypes(include=[np.number]).columns if c not in ("populacao_total",)]
mask = df_orig[nc].notna().sum(axis=1) >= 15
df = df_orig[mask].copy().reset_index(drop=True)
df = df.drop(columns=[c for c in ["pais_id", "income_code", "income_name", "populacao_total",
"aipi_digital", "aipi_humano", "aipi_regulacao", "aipi_inovacao",
"educ_secundaria_pct", "servicos_pib_pct", "patentes_residentes",
"densidade_pop_km2", "desemprego_pct", "cresc_pib_anual",
"pesquisadores_milhao", "forca_stem_pct", "habilidades_digitais_pct"]
if c in df.columns], errors="ignore")
resultados = {}
TARGET = "escape_arm"
TARGET_SYN = "escape_arm_score"
print("=" * 60)
print(f"análise ARM x IAG - WDI REAL ({len(df)} paises)")
print("=" * 60)
# 1. MATRIZ DE CORRELACAO
print("\n[1/10] Matriz de correlacao...")
vn = [c for c in df.select_dtypes(include=[np.number]).columns if c not in (TARGET, TARGET_SYN)]
cm = df[vn + [TARGET]].corr(method="pearson") if TARGET in df.columns else pd.DataFrame()
if TARGET in cm.columns:
    tc = cm[TARGET].drop(TARGET).sort_values(key=abs, ascending=False)
    resultados["top_corr"] = {k: round(v, 4) for k, v in tc.head(15).items()}
    print("Top correlacoes com escape_arm:")
    for k, v in list(resultados["top_corr"].items())[:10]:
        print(f" {k}: r={v:+.4f}")
plt.figure(figsize=(16, 12))
sns.heatmap(cm, cmap="RdBu_r", center=0, vmin=-1, vmax=1, annot=False, linewidths=0.3)
plt.title("Matriz de Correlacao - Dados WDI", fontsize=14, fontweight="bold")
plt.tight_layout(); plt.savefig(OUT / "fig01_matriz_correlacao.png", bbox_inches="tight", dpi=200); plt.close()
# 2. CORRELACOES INUSITADAS
print("\n[2/10] Correlacoes inusitadas...")
pares = [("agricultura_pib_pct", "internet_pop_pct", "Agricultura vs Internet"),
("gini", "internet_pop_pct", "Desigualdade vs Internet"),
("educ_superior_pct", "gini", "educação vs Desigualdade"),
("gerd_pib_pct", "gini", "P&D vs Desigualdade"),
("export_tech_pct", "manufatura_pib_pct", "Export tech vs Manufatura"),
("agricultura_pib_pct", "aipi_total", "Agricultura vs Prontidao IA"),
]
ci_list = []
for v1, v2, lb in pares:
if v1 in df.columns and v2 in df.columns:
d = df[[v1, v2]].dropna()
if len(d) > 5:
r, p = pearsonr(d[v1], d[v2])
rh, _ = spearmanr(d[v1], d[v2])
sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
ci_list.append({"par": lb, "r": round(r, 4), "p": round(p, 6), "rho": round(rh, 4), "sig": sig})
resultados["corr_insolitas"] = ci_list
for c in ci_list:
print(f" {c['par']}: r={c['r']:+.4f} (p={c['p']:.4f}) {c['sig']}")
if ci_list:
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
for ax, (v1, v2, lb), ci in zip(axes.flat, pares, ci_list):
if v1 in df.columns and v2 in df.columns:
d = df[[v1, v2]].dropna()
ax.scatter(d[v1], d[v2], alpha=0.6, s=25, c="steelblue", edgecolors="white")
z = np.polyfit(d[v1], d[v2], 1)
ax.plot(d[v1], np.polyval(z, d[v1]), "r--", alpha=0.6)
ax.set_xlabel(v1[:20], fontsize=8); ax.set_ylabel(v2[:20], fontsize=8)
ax.set_title(f"{lb}\nr={ci['r']:.3f}, p={ci['p']:.4f}", fontsize=9, fontweight="bold")
plt.suptitle("Correlacoes não-Obvias - Dados WDI", fontsize=13, fontweight="bold")
plt.tight_layout(); plt.savefig(OUT / "fig02_correlacoes_inusitadas.png", bbox_inches="tight"); plt.close()
# 3. CLUSTERIZACAO
print("\n[3/10] Clusterizacao...")
vc = [c for c in ["aipi_total", "ptf_relativa", "educ_superior_pct", "internet_pop_pct",
"gerd_pib_pct", "export_tech_pct", "gini", "complexidade_economica", "escape_arm"]
if c in df.columns]
Xc = df[vc].dropna()
Xcs = StandardScaler().fit_transform(Xc)
from sklearn.metrics import silhouette_score
sl = [silhouette_score(Xcs, KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(Xcs)) for k in range(2, 9)]
k_opt = range(2, 9)[np.argmax(sl)]
resultados["k_otimo"] = int(k_opt)
km = KMeans(n_clusters=k_opt, random_state=42, n_init=10)
clusters = km.fit_predict(Xcs)
# Map cluster back to original df
df["cluster"] = np.nan
df.loc[Xc.index, "cluster"] = clusters
pca = PCA(n_components=2)
Xp = pca.fit_transform(Xcs)
df["pca1"] = np.nan; df["pca2"] = np.nan
df.loc[Xc.index, "pca1"] = Xp[:, 0]
df.loc[Xc.index, "pca2"] = Xp[:, 1]
plt.figure(figsize=(10, 7))
for k in range(k_opt):
m = df["cluster"] == k
plt.scatter(df.loc[m, "pca1"], df.loc[m, "pca2"],
c=[plt.cm.Set1(k / k_opt)], label=f"Cluster {k}", s=50, alpha=0.7, edgecolors="w")
plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%})")
plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%})")
plt.title(f"Clusters - Dados WDI (k={k_opt})", fontweight="bold")
plt.legend(); plt.grid(True, alpha=0.3)
plt.savefig(OUT / "fig03_clusters_pca.png", bbox_inches="tight"); plt.close()
df.groupby("cluster")[vc].mean().round(2).to_csv(OUT / "tabela_cluster_profiles.csv")
# 4. MODELOS ML
print("\n[4/10] Modelos ML...")
drop_ml = ["cluster", "pca1", "pca2", "pais", "regiao", "renda", TARGET, TARGET_SYN, "aipi_total"]
fc = [c for c in df.columns if df[c].dtype in (np.float64, np.int64) and df[c].nunique() > 5 and c not in drop_ml]
X = df[fc].dropna()
y = df.loc[X.index, TARGET] if TARGET in df.columns else df.loc[X.index, TARGET_SYN]
if len(X) > 20:
Xs = StandardScaler().fit_transform(X)
Xs = pd.DataFrame(Xs, columns=X.columns, index=X.index)
Xt, Xv, yt, yv = train_test_split(Xs, y, test_size=0.25, random_state=42)
mods = {
"RandomForest": RandomForestRegressor(n_estimators=200, max_depth=6, min_samples_leaf=3, random_state=42, n_jobs=-1),
"GradientBoosting": GradientBoostingRegressor(n_estimators=150, learning_rate=0.05, max_depth=3, random_state=42),
"ElasticNet": ElasticNet(alpha=0.01, l1_ratio=0.5, random_state=42, max_iter=5000),
}
try:
import xgboost as xgb
mods["XGBoost"] = xgb.XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=3, subsample=0.8, random_state=42)
except: pass
try:
import lightgbm as lgb
mods["LightGBM"] = lgb.LGBMRegressor(n_estimators=200, learning_rate=0.05, max_depth=3, subsample=0.8, random_state=42, verbose=-1)
except: pass
metrics = []
for nm, mod in mods.items():
mod.fit(Xt, yt)
yp = mod.predict(Xv)
cv = cross_val_score(mod, Xs, y, cv=KFold(5, shuffle=True, random_state=42), scoring="r2")
m = {"modelo": nm, "r2_teste": round(r2_score(yv, yp), 4),
"rmse": round(np.sqrt(mean_squared_error(yv, yp)), 4),
"cv_r2": f"{cv.mean():.4f}+-{cv.std():.4f}"}
metrics.append(m)
print(f" {nm}: R2={m['r2_teste']:.4f}, CV={cv.mean():.4f}+-{cv.std():.4f}")
resultados["metricas"] = metrics
pd.DataFrame(metrics).to_csv(OUT / "tabela_comparacao_modelos.csv", index=False)
# 5. FEATURE IMPORTANCE
print("\n[5/10] Feature importance...")
rf = mods.get("RandomForest")
if rf:
imp = pd.DataFrame({"variavel": X.columns, "importância": rf.feature_importances_}).sort_values("importância", ascending=False)
imp.to_csv(OUT / "tabela_feature_importance_rf.csv", index=False)
resultados["top_features"] = imp.head(15).to_dict("records")
plt.figure(figsize=(9, 7))
imp.head(15).plot(x="variavel", y="importância", kind="barh", color="steelblue", legend=False)
plt.gca().invert_yaxis()
plt.xlabel("importância Random Forest")
plt.title("Top 15 Features para Escape ARM (WDI)", fontweight="bold")
plt.tight_layout(); plt.savefig(OUT / "fig04_feature_importance.png", bbox_inches="tight"); plt.close()
# SHAP
xm = mods.get("XGBoost") or mods.get("GradientBoosting")
if xm:
try:
import shap
sv = shap.TreeExplainer(xm).shap_values(Xv)
plt.figure(figsize=(11, 7))
shap.summary_plot(sv, Xv, feature_names=X.columns, show=False, max_display=15)
plt.title("SHAP - Escape ARM (WDI)", fontweight="bold")
plt.tight_layout(); plt.savefig(OUT / "fig05_shap_summary.png", bbox_inches="tight"); plt.close()
plt.figure(figsize=(9, 6))
shap.summary_plot(sv, Xv, feature_names=X.columns, plot_type="bar", show=False, max_display=15)
plt.tight_layout(); plt.savefig(OUT / "fig05b_shap_bar.png", bbox_inches="tight"); plt.close()
print(" SHAP OK")
except Exception as e:
print(f" SHAP: {e}")
# 6. validação CRUZADA
print("\n[6/10] validação cruzada...")
rkf = RepeatedKFold(n_splits=5, n_repeats=10, random_state=42)
rkf_s = cross_val_score(rf, Xs, y, cv=rkf, scoring="r2")
resultados["rkf_mean"] = round(rkf_s.mean(), 4)
resultados["rkf_std"] = round(rkf_s.std(), 4)
print(f" Repeated K-Fold: R2={rkf_s.mean():.4f}+-{rkf_s.std():.4f}")
try:
ft = [c for c in ["internet_pop_pct", "educ_superior_pct", "gerd_pib_pct"] if c in df_painel.columns]
anos = sorted(df_painel["ano"].unique())
r2t = []
for i in range(len(anos) - 1):
tr = df_painel[df_painel["ano"].isin(anos[:i+1])]
te = df_painel[df_painel["ano"] == anos[i+1]]
if len(te) > 5:
lr = LinearRegression()
lr.fit(tr[ft].fillna(0), tr.get("cresc_pib_anual", tr.get("pib_pc_ppc", 0)))
yt_ = te.get("cresc_pib_anual", te.get("pib_pc_ppc", 0))
r2t.append(r2_score(yt_, lr.predict(te[ft].fillna(0))))
if r2t:
resultados["temporal_cv"] = round(np.mean(r2t), 4)
print(f" Temporal CV: R2={np.mean(r2t):.4f}")
except: print(" Temporal CV: N/A")
# 7. ECONOMETRIA
print("\n[7/10] Econometria...")
try:
fe = [c for c in ["internet_pop_pct", "educ_superior_pct", "gerd_pib_pct", "gini"] if c in df_painel.columns]
Y = df_painel.get("cresc_pib_anual", df_painel.get("pib_pc_ppc", 0)).fillna(0).values
Xe = sm.add_constant(df_painel[fe].fillna(0).values)
ols = sm.OLS(Y, Xe).fit()
resultados["pooled_r2"] = round(ols.rsquared, 4)
vif = pd.DataFrame({"var": fe, "VIF": [round(variance_inflation_factor(Xe[:, 1:], i), 2) for i in range(Xe.shape[1] - 1)]})
vif.to_csv(OUT / "tabela_vif.csv", index=False)
resultados["vif"] = vif.to_dict("records")
print(f" Pooled OLS: R2={ols.rsquared:.4f}")
from statsmodels.stats.diagnostic import het_breuschpagan
bp = het_breuschpagan(ols.resid, Xe)
resultados["bp_p"] = round(bp[1], 4)
print(f" Breusch-Pagan: p={bp[1]:.4f}")
except Exception as e:
print(f" Econometria: {e}")
# 8. SIMILARIDADE
print("\n[8/10] Similaridade...")
from sklearn.metrics.pairwise import cosine_similarity
sim = cosine_similarity(StandardScaler().fit_transform(Xc.values))
np.fill_diagonal(sim, 0)
# 9. ANOVA
print("\n[9/10] ANOVA...")
va = [c for c in ["aipi_total", "escape_arm", "ptf_relativa", "educ_superior_pct", "internet_pop_pct", "gini"] if c in df.columns]
an = []
for v in va:
grps = [df[df["regiao"] == r][v].dropna().values for r in df["regiao"].unique()]
grps = [g for g in grps if len(g) > 1]
if len(grps) > 1:
f, p = f_oneway(*grps)
an.append({"var": v, "f": round(f, 2), "p": round(p, 6)})
resultados["anova"] = an
for r in an:
s = "***" if r["p"] < 0.001 else "**" if r["p"] < 0.01 else "*" if r["p"] < 0.05 else "ns"
print(f" {r['var']}: F={r['f']:.2f}, p={r['p']:.4f} {s}")
# 10. EXPORT
print("\n[10/10] Exportando...")
resultados["n_paises"] = len(df)
resultados["n_features"] = len(fc)
with open(OUT / "resultados_análise.json", "w") as f:
json.dump(resultados, f, indent=2, default=str)
bm = max(resultados.get("metricas", []), key=lambda x: x.get("r2_teste", 0)) if resultados.get("metricas") else {}
rpt = f"""
RELATORIO FINAL - ARM x IAG (WDI REAL)
1. DADOS: {resultados['n_paises']} paises, {resultados['n_features']} features
2. TOP CORRELACOES:
{chr(10).join(f' {k}: r={v}' for k,v in list(resultados.get('top_corr',{}).items())[:5])}
3. CLUSTER: k={resultados.get("k_otimo","N/A")}, silhouette={max(sl):.3f}
4. MELHOR MODELO: {bm.get("modelo","N/A")} R2={bm.get("r2_teste","N/A")}
5. validação: R2={resultados.get("rkf_mean","N/A")}+-{resultados.get("rkf_std","N/A")}
6. ECONOMETRIA: R2={resultados.get("pooled_r2","N/A")}
"""
with open(OUT / "relatorio_resumo.txt", "w") as f:
f.write(rpt)
print(rpt)
print("OK")
