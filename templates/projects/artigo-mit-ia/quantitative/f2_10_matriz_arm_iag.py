"""
Fase 2.10 — Matriz ARM-IAG (4 Quadrantes)
===========================================
Classifica cada país em 2 eixos:
  Eixo X: Risco ARM (baixo escape_arm → alto risco)
  Eixo Y: Prontidão IAG (aipi_total)

4 quadrantes:
  Q1 - Alta resiliência (baixo ARM, alta IAG)
  Q2 - Potencial desperdiçado (alto ARM, alta IAG)
  Q3 - Vulnerável (alto ARM, baixa IAG)
  Q4 - Tradicional estável (baixo ARM, baixa IAG)

Saída: JSON + lista de países por quadrante.
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
OUT  = BASE / 'output' / 'matriz_arm_iag.json'

df = pd.read_csv(DATA)

# Selecionar países com dados completos
cols = ['pais', 'regiao', 'renda', 'escape_arm', 'aipi_total',
        'aipi_digital', 'aipi_humano', 'aipi_inovacao', 'aipi_regulacao',
        'pib_pc_ppc']
df_m = df[cols].dropna(subset=['escape_arm', 'aipi_total'])
print(f"Países com dados completos: {df_m.shape[0]}")

# ── Medianas como pontos de corte ────────────────────────────────────────────
med_escape = df_m['escape_arm'].median()
med_aipi   = df_m['aipi_total'].median()
print(f"Mediana escape_arm: {med_escape:.3f}")
print(f"Mediana aipi_total: {med_aipi:.1f}")

# ── Classificar quadrantes ───────────────────────────────────────────────────
def classificar(row):
    arm_alto = row['escape_arm'] < med_escape   # abaixo da mediana = ARM alto
    iag_alto = row['aipi_total'] >= med_aipi
    if not arm_alto and iag_alto:
        return 'Q1-Alta Resiliência'
    elif arm_alto and iag_alto:
        return 'Q2-Potencial Desperdiçado'
    elif arm_alto and not iag_alto:
        return 'Q3-Vulnerável'
    else:
        return 'Q4-Tradicional Estável'

df_m['quadrante'] = df_m.apply(classificar, axis=1)

# ── Estatísticas por quadrante ──────────────────────────────────────────────
print("\n═══ Distribuição por Quadrante ═══")
quadrantes = {}
for q in ['Q1-Alta Resiliência', 'Q2-Potencial Desperdiçado',
           'Q3-Vulnerável', 'Q4-Tradicional Estável']:
    subset = df_m[df_m['quadrante'] == q]
    info = {
        'n': len(subset),
        'escape_arm_medio': round(subset['escape_arm'].mean(), 3),
        'aipi_total_medio': round(subset['aipi_total'].mean(), 1),
        'pib_pc_ppc_medio': round(subset['pib_pc_ppc'].mean(), 0),
        'paises': subset['pais'].tolist()
    }
    quadrantes[q] = info
    print(f"\n  {q} (n={info['n']}):")
    print(f"    escape_arm médio = {info['escape_arm_medio']}")
    print(f"    aipi_total médio = {info['aipi_total_medio']}")
    print(f"    PIB pc médio     = {info['pib_pc_ppc_medio']}")

# ── Países notáveis em cada quadrante ────────────────────────────────────────
print("\n═══ Países por quadrante (amostra) ═══")
for q, info in quadrantes.items():
    # 10 primeiros
    amostra = info['paises'][:10]
    print(f"  {q}: {', '.join(amostra)}")

# ── Distribuição por região nos quadrantes ──────────────────────────────────
print("\n═══ Distribuição Regional nos Quadrantes ═══")
crosstab = pd.crosstab(df_m['quadrante'], df_m['regiao'])
print(crosstab.to_string())

# ── Salvar ──────────────────────────────────────────────────────────────────
resultados = {
    'mediana_escape_arm': round(med_escape, 3),
    'mediana_aipi_total': round(med_aipi, 1),
    'n_total': len(df_m),
    'quadrantes': quadrantes,
    'matriz_regiao': crosstab.to_dict()
}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)
print(f"\nResultados salvos em: {OUT}")
