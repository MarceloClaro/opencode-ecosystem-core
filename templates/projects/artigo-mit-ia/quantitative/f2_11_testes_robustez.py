"""
Fase 2.11 — Testes de Robustez
================================
1. Permutation test: significância do R² (shuffle target)
2. Subamostragem: R² em 80% dos dados (100 iterações)
3. Modelo linear OLS (transparência vs RF)
4. Correlação parcial AIPI vs escape_arm (controlando PIB)

Saída: JSON com todas as métricas de robustez.
"""

import pandas as pd
import numpy as np
import json
import warnings
import sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score
from sklearn.impute import SimpleImputer
from sklearn.utils import resample
from scipy import stats

BASE = Path(r'C:\Users\marce\.config\opencode\artigo-mit-ia\quantitative')
DATA = BASE / 'output' / 'dataset_corte_transversal.csv'
OUT  = BASE / 'output' / 'testes_robustez.json'

df = pd.read_csv(DATA)
print(f"Dataset: {df.shape[0]} países, {df.shape[1]} colunas")

# Features SEM leakage
FEATURES = ['pib_pc_ppc', 'manufatura_pib_pct', 'agricultura_pib_pct',
            'export_tech_pct', 'aipi_digital', 'aipi_humano',
            'aipi_inovacao', 'aipi_regulacao']
TARGET = 'escape_arm'

# Preparar dados
X = df[FEATURES].copy()
y = df[TARGET].values
mask = ~np.isnan(y)
X, y = X[mask], y[mask]
imp = SimpleImputer(strategy='median')
X_imp = pd.DataFrame(imp.fit_transform(X), columns=X.columns)
print(f"Dados válidos: {X_imp.shape[0]} obs, {X_imp.shape[1]} features")

resultados = {}

# ── 1. Permutation Test (100 iterações) ─────────────────────────────────────
print("\n═══ Permutation Test (100 iterações) ═══")
X_tr, X_te, y_tr, y_te = train_test_split(X_imp, y, test_size=0.2, random_state=42)

r2_original = None
r2_permutados = []
for i in range(50):
    rf = RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42, n_jobs=-1)
    y_perm = np.random.permutation(y_tr)
    rf.fit(X_tr, y_perm)
    r2 = r2_score(y_te, rf.predict(X_te))
    r2_permutados.append(r2)
    if i == 0:
        # Treinar com dados reais
        rf_real = RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42, n_jobs=-1)
        rf_real.fit(X_tr, y_tr)
        r2_original = r2_score(y_te, rf_real.predict(X_te))

p_value = (1 + sum(np.array(r2_permutados) >= r2_original)) / 51
resultados['permutation_test'] = {
    'r2_original': round(r2_original, 4),
    'r2_perm_medio': round(np.mean(r2_permutados), 4),
    'r2_perm_std': round(np.std(r2_permutados), 4),
    'r2_perm_max': round(np.max(r2_permutados), 4),
    'p_value': round(p_value, 4)
}
print(f"  R² original:     {r2_original:.4f}")
print(f"  R² permutado:    {np.mean(r2_permutados):.4f} ± {np.std(r2_permutados):.4f}")
print(f"  Max permutado:   {np.max(r2_permutados):.4f}")
print(f"  p-value:         {p_value:.4f}")

# ── 2. Subamostragem (80%, 50 iterações) ───────────────────────────────────
print("\n═══ Subamostragem (80%, 50 iterações) ═══")
r2_sub = []
for i in range(50):
    X_sub, y_sub = resample(X_imp, y, n_samples=int(0.8*len(y)), random_state=i, replace=False)
    X_s_tr, X_s_te, y_s_tr, y_s_te = train_test_split(X_sub, y_sub, test_size=0.2, random_state=42)
    rf = RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42, n_jobs=-1)
    rf.fit(X_s_tr, y_s_tr)
    r2_sub.append(r2_score(y_s_te, rf.predict(X_s_te)))

resultados['subsampling'] = {
    'r2_medio': round(np.mean(r2_sub), 4),
    'r2_std': round(np.std(r2_sub), 4),
    'r2_p5': round(np.percentile(r2_sub, 5), 4),
    'r2_p95': round(np.percentile(r2_sub, 95), 4)
}
print(f"  R² médio:  {np.mean(r2_sub):.4f} ± {np.std(r2_sub):.4f}")
print(f"  P5-P95:    {np.percentile(r2_sub, 5):.4f} — {np.percentile(r2_sub, 95):.4f}")

# ── 3. OLS Linear (transparência) ──────────────────────────────────────────
print("\n═══ Regressão Linear (OLS) ═══")
ols = LinearRegression()
cv_ols = cross_val_score(ols, X_imp, y, cv=5, scoring='r2')
ols.fit(X_tr, y_tr)
r2_ols_te = r2_score(y_te, ols.predict(X_te))

resultados['ols'] = {
    'r2_teste': round(r2_ols_te, 4),
    'cv_r2_medio': round(cv_ols.mean(), 4),
    'cv_r2_std': round(cv_ols.std(), 4),
    'coeficientes': {col: round(coef, 4) for col, coef in zip(FEATURES, ols.coef_)}
}
print(f"  R² teste OLS: {r2_ols_te:.4f}")
print(f"  CV OLS:       {cv_ols.mean():.4f} ± {cv_ols.std():.4f}")
for col, coef in zip(FEATURES, ols.coef_):
    print(f"    {col:25s}  β = {coef:+.4f}")

# ── 4. Correlação parcial (AIPI vs escape_arm, controlando PIB) ─────────────
print("\n═══ Correlação Parcial ═══")
# Correlação simples
r_simple = df['aipi_total'].corr(df['escape_arm'])
# Correlação parcial: resíduo AIPI ~ PIB vs resíduo escape ~ PIB
from sklearn.linear_model import LinearRegression

def correlacao_parcial(df, x_col, y_col, controle_col):
    """Correlação parcial entre x e y controlando por controle."""
    m1 = LinearRegression().fit(df[[controle_col]], df[x_col])
    m2 = LinearRegression().fit(df[[controle_col]], df[y_col])
    resid_x = df[x_col] - m1.predict(df[[controle_col]])
    resid_y = df[y_col] - m2.predict(df[[controle_col]])
    return np.corrcoef(resid_x, resid_y)[0, 1]

df_parcial = df[['aipi_total', 'escape_arm', 'pib_pc_ppc']].dropna()
r_parcial = correlacao_parcial(df_parcial, 'aipi_total', 'escape_arm', 'pib_pc_ppc')
r_simple_val = df_parcial['aipi_total'].corr(df_parcial['escape_arm'])

resultados['correlacao_parcial'] = {
    'r_simples_aipi_escape': round(r_simple_val, 4),
    'r_parcial_controlando_pib': round(r_parcial, 4),
    'n': len(df_parcial)
}
print(f"  r simples (AIPI vs escape):    {r_simple_val:.4f}")
print(f"  r parcial (controle PIB pc):   {r_parcial:.4f}")

# ── 5. Resumo ───────────────────────────────────────────────────────────────
print("\n═══ RESUMO — Robustez ═══")
print(f"  Permutation p-value: {resultados['permutation_test']['p_value']}")
print(f"  Subsampling R²:      {resultados['subsampling']['r2_medio']} ± {resultados['subsampling']['r2_std']}")
print(f"  OLS R²:              {resultados['ols']['r2_teste']}")
print(f"  Correlação parcial:  {r_parcial:.4f} (vs simples {r_simple_val:.4f})")

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)
print(f"\nResultados salvos em: {OUT}")
