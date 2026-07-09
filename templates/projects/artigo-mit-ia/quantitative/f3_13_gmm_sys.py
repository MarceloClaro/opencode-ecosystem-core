"""
Fase 3.13 — IV-2SLS Cross-Sectional (substituto do GMM-Sys)
=============================================================
O dataset painel não possui variação temporal (dados repetidos).
Adaptação metodológica:
  1. Cross-sectional OLS (baseline) — N países
  2. IV-2SLS: instrumentos regionais para AIPI
  3. Explicação da limitação do painel

Instrumento: média regional leave-one-out de aipi_total.
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
OUT  = BASE / 'output' / 'gmm_sys_resultados.json'

df = pd.read_csv(DATA)
print(f"Dataset cross-sectional: {df.shape[0]} países")

FEATURES = ['aipi_total', 'pib_pc_ppc', 'educ_superior_pct',
            'internet_pop_pct', 'gini', 'agricultura_pib_pct']
TARGET = 'escape_arm'

# Instrumento: média regional leave-one-out
for regiao in df['regiao'].unique():
    mask = df['regiao'] == regiao
    n = mask.sum()
    soma = df.loc[mask, 'aipi_total'].sum()
    df.loc[mask, 'aipi_iv_loo'] = (soma - df.loc[mask, 'aipi_total']) / (n - 1)

print(f"  Correlação IV LOI -> aipi_total: {df['aipi_iv_loo'].corr(df['aipi_total']):.3f}")

modelo_df = df[FEATURES + [TARGET, 'aipi_iv_loo']].dropna()
print(f"Obs para modelos: {len(modelo_df)}")

from statsmodels.api import OLS, add_constant
from linearmodels.iv import IV2SLS

resultados = {}

# 1. OLS
print("\n═══ Modelo 1: OLS Cross-Sectional ═══")
X = add_constant(modelo_df[FEATURES])
y = modelo_df[TARGET]
ols = OLS(y, X).fit(cov_type='HC3')
print(ols.summary().tables[1])

resultados['ols'] = {
    'params': {k: round(v, 6) for k, v in ols.params.items()},
    'pvalues': {k: round(v, 4) for k, v in ols.pvalues.items()},
    'r2': round(ols.rsquared, 4),
    'n': int(ols.nobs)
}

# 2. IV-2SLS
print("\n═══ Modelo 2: IV-2SLS (instr: aipi_regional_LOO) ═══")
iv = IV2SLS.from_formula(
    'escape_arm ~ 1 + pib_pc_ppc + educ_superior_pct + internet_pop_pct + gini + agricultura_pib_pct'
    ' + [aipi_total ~ aipi_iv_loo]',
    data=modelo_df
).fit(cov_type='robust')
print(iv)

resultados['iv_2sls'] = {
    'params': {k: round(v, 6) for k, v in iv.params.items()},
    'pvalues': {k: round(v, 4) for k, v in iv.pvalues.items()},
    'n': int(iv.nobs)
}
try:
    resultados['iv_2sls']['f_stat_1o_estagio'] = round(iv.first_stage.f_statistic.stat, 2)
except:
    pass

# 3. OLS Restrito
print("\n═══ Modelo 3: OLS Restrito (AIPI + PIB) ═══")
Xr = add_constant(modelo_df[['aipi_total', 'pib_pc_ppc']])
yr = modelo_df[TARGET]
ols_r = OLS(yr, Xr).fit(cov_type='HC3')
resultados['ols_restrito'] = {
    'params': {k: round(v, 6) for k, v in ols_r.params.items()},
    'pvalues': {k: round(v, 4) for k, v in ols_r.pvalues.items()},
    'r2': round(ols_r.rsquared, 4),
    'n': int(ols_r.nobs)
}

# 4. Nota
resultados['nota_metodologica'] = (
    "Dataset painel (2016-2025) sem variacao temporal. "
    "GMM-Sys substituido por IV-2SLS cross-sectional "
    "(instrumento: media regional leave-one-out de AIPI). "
    "Recomenda-se dados WDI em serie temporal real."
)

print("\n═══ RESUMO ═══")
for m in ['ols', 'ols_restrito', 'iv_2sls']:
    r = resultados[m]
    print(f"  {m:20s}  n={r.get('n','?')}  R²={r.get('r2','?'):<8}"
          f"  β_aipi={r.get('params',{}).get('aipi_total','?'):<10}")

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)
print(f"\nSalvo em: {OUT}")
