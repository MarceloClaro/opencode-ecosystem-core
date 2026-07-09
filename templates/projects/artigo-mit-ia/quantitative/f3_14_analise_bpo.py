"""
Fase 3.14 — Análise do Caso BPO (Terceirização de Processos)
=============================================================
Analisa a relação entre terceirização de serviços (BPO) e
escape da armadilha da renda média.

Proxy empírico: servicos_pib_pct + export_tech_pct
Casos emblemáticos: Índia, Filipinas (BPO hubs globais)

Abordagem:
  1. Correlação serviços_pib_pct x escape_arm
  2. Cluster de economias BPO (alto serviços + baixa manufatura)
  3. Análise dos casos Índia e Filipinas
  4. Implicações para a tese IAG + BPO
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
OUT  = BASE / 'output' / 'analise_bpo.json'

df = pd.read_csv(DATA)
print(f"Dataset: {df.shape[0]} países")

# ── 1. Correlações com serviços ─────────────────────────────────────────────
print("\n═══ Correlações BPO Proxy ═══")
for var in ['servicos_pib_pct', 'manufatura_pib_pct', 'export_tech_pct']:
    if var in df.columns:
        r = df[var].corr(df['escape_arm'])
        print(f"  {var:25s} vs escape_arm: r = {r:+.4f}")

# Razão serviços/manufatura como proxy de terceirização
df['razao_serv_manuf'] = df['servicos_pib_pct'] / df['manufatura_pib_pct'].clip(lower=1)
r_razao = df['razao_serv_manuf'].corr(df['escape_arm'])
print(f"  razao_serv_manuf    vs escape_arm: r = {r_razao:+.4f}")

# ── 2. Economias BPO (alto serviços, serviços > manufatura + agricultura) ──
print("\n═══ Identificação de Economias BPO ═══")
df_bpo = df[['pais', 'regiao', 'renda', 'escape_arm', 'aipi_total',
             'servicos_pib_pct', 'manufatura_pib_pct', 'agricultura_pib_pct',
             'export_tech_pct', 'pib_pc_ppc']].dropna(subset=['servicos_pib_pct'])

# Critério BPO: serviços > 60% PIB + serviços > 2x manufatura
df_bpo['is_bpo'] = ((df_bpo['servicos_pib_pct'] > 60) & 
                     (df_bpo['servicos_pib_pct'] > 2 * df_bpo['manufatura_pib_pct'])).astype(int)

bpo_countries = df_bpo[df_bpo['is_bpo'] == 1]
print(f"  Economias com perfil BPO: {len(bpo_countries)}")
bpo_top = bpo_countries.sort_values('servicos_pib_pct', ascending=False)
print(bpo_top[['pais', 'regiao', 'servicos_pib_pct', 'manufatura_pib_pct', 
               'escape_arm', 'aipi_total']].head(20).to_string(index=False))

# ── 3. Casos emblemáticos ───────────────────────────────────────────────────
print("\n═══ Casos Emblemáticos ═══")
casos = ['India', 'Philippines', 'Brazil', 'Mexico', 'China', 'Vietnam']
for c in casos:
    row = df[df['pais'] == c]
    if len(row) > 0:
        r = row.iloc[0]
        print(f"\n  {c}:")
        print(f"    escape_arm={r['escape_arm']:.4f}   aipi_total={r['aipi_total']:.1f}")
        print(f"    servicos={r['servicos_pib_pct']:.1f}%  manufatura={r['manufatura_pib_pct']:.1f}%  "
              f"agricultura={r['agricultura_pib_pct']:.1f}%")
        print(f"    export_tech={r['export_tech_pct']:.1f}%") if 'export_tech_pct' in r.index else None

# ── 4. Regressão: interação BPO × AIPI ─────────────────────────────────────
print("\n═══ Interação BPO × AIPI ═══")
from statsmodels.api import OLS, add_constant

reg_df = df_bpo[['escape_arm', 'aipi_total', 'servicos_pib_pct', 
                  'manufatura_pib_pct', 'is_bpo', 'pib_pc_ppc']].dropna()
reg_df['aipi_x_bpo'] = reg_df['aipi_total'] * reg_df['is_bpo']

X = add_constant(reg_df[['aipi_total', 'is_bpo', 'aipi_x_bpo', 'pib_pc_ppc']])
y = reg_df['escape_arm']
model = OLS(y, X).fit(cov_type='HC3')
print(model.summary().tables[1])

resultados_bpo = {
    'correlacao_servicos_escape': round(df['servicos_pib_pct'].corr(df['escape_arm']), 4),
    'correlacao_razao_serv_manuf': round(r_razao, 4),
    'n_economias_bpo': int(len(bpo_countries)),
    'top_bpo': bpo_top['pais'].head(10).tolist(),
    'modelo_interacao': {
        'params': {k: round(v, 6) for k, v in model.params.items()},
        'pvalues': {k: round(v, 4) for k, v in model.pvalues.items()},
        'r2': round(model.rsquared, 4),
        'n': int(model.nobs)
    }
}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(resultados_bpo, f, indent=2, ensure_ascii=False, default=str)
print(f"\nResultados salvos em: {OUT}")
