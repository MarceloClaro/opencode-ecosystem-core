"""
Fase 3.12 — Análise Empírica Brasil (PNAD proxy)
=================================================
Objetivos:
  1. Perfil completo do Brasil no cross-section
  2. Comparação com América Latina e pares de renda média
  3. Posição do Brasil na Matriz ARM-IAG
  4. Identificação de gaps nos pilares AIPI
  5. Evolução no painel (mesmo que estático, mostra baseline)
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
DATA_CT = BASE / 'output' / 'dataset_corte_transversal.csv'
DATA_PN = BASE / 'output' / 'dataset_painel_2016_2025.csv'
OUT  = BASE / 'output' / 'analise_brasil.json'

df = pd.read_csv(DATA_CT)
print(f"Dataset: {df.shape[0]} países")

# ── 1. Perfil Brazil ────────────────────────────────────────────────────────
VARS_PERFIL = ['pais', 'regiao', 'renda', 'escape_arm', 'pib_pc_ppc',
               'aipi_total', 'aipi_digital', 'aipi_humano', 'aipi_inovacao',
               'aipi_regulacao', 'ptf_relativa', 'educ_superior_pct',
               'internet_pop_pct', 'gerd_pib_pct', 'gini',
               'complexidade_economica', 'manufatura_pib_pct',
               'servicos_pib_pct', 'agricultura_pib_pct', 'export_tech_pct',
               'desemprego_pct', 'populacao_total']

br = df[df['pais'] == 'Brazil']
if len(br) == 0:
    # Try 'Brasil'
    br = df[df['pais'].str.contains('razil|rasil', case=False, na=False)]

if len(br) > 0:
    br_profile = br[VARS_PERFIL].iloc[0].to_dict()
    for k, v in br_profile.items():
        if isinstance(v, float):
            br_profile[k] = round(v, 4)
    
    print(f"\n── Perfil Brasil ──")
    for k, v in br_profile.items():
        print(f"  {k:30s} = {v}")
else:
    print("Brasil não encontrado!")
    br_profile = {}

# ── 2. Comparação regional (América Latina) ─────────────────────────────────
print("\n── Comparação com América Latina ──")
latam = df[df['regiao'] == 'Latin America & Caribbean']
print(f"  Países LATAM: {len(latam)}")

comparacao = {}
for var in ['escape_arm', 'aipi_total', 'aipi_digital', 'aipi_humano',
            'aipi_inovacao', 'aipi_regulacao', 'pib_pc_ppc', 'gini',
            'educ_superior_pct', 'internet_pop_pct', 'gerd_pib_pct']:
    br_val = br[var].values[0] if len(br) > 0 else None
    latam_mean = latam[var].mean()
    latam_std = latam[var].std()
    latam_max = latam[var].max()
    latam_min = latam[var].min()
    if br_val and latam_std > 0:
        z = (br_val - latam_mean) / latam_std
    else:
        z = 0
    comparacao[var] = {
        'brasil': round(br_val, 4) if br_val else None,
        'latam_media': round(latam_mean, 4),
        'latam_std': round(latam_std, 4),
        'latam_max': round(latam_max, 4),
        'latam_min': round(latam_min, 4),
        'z_score': round(z, 4)
    }
    print(f"  {var:30s} BR={br_val:<10.4f} LATAM_μ={latam_mean:<10.4f} "
          f"z={z:+.2f}  [min={latam_min:.2f}, max={latam_max:.2f}]")

# ── 3. Posição na Matriz ARM-IAG ────────────────────────────────────────────
print("\n── Posição do Brasil na Matriz ARM-IAG ──")
med_escape = df['escape_arm'].median()
med_aipi = df['aipi_total'].median()
br_escape = br['escape_arm'].values[0] if len(br) > 0 else 0
br_aipi = br['aipi_total'].values[0] if len(br) > 0 else 0

# Percentis
pct_escape = (df['escape_arm'] < br_escape).mean() * 100
pct_aipi = (df['aipi_total'] < br_aipi).mean() * 100
print(f"  escape_arm: {br_escape:.3f} (mediana global: {med_escape:.3f}, percentil: {pct_escape:.0f})")
print(f"  aipi_total: {br_aipi:.1f} (mediana global: {med_aipi:.1f}, percentil: {pct_aipi:.0f})")

if br_escape >= med_escape and br_aipi >= med_aipi:
    quadrante = "Q1 - Alta Resiliência (baixo ARM, alta IAG)"
elif br_escape < med_escape and br_aipi >= med_aipi:
    quadrante = "Q2 - Potencial Desperdiçado (alto ARM, alta IAG)"
elif br_escape < med_escape and br_aipi < med_aipi:
    quadrante = "Q3 - Vulnerável (alto ARM, baixa IAG)"
else:
    quadrante = "Q4 - Tradicional Estável (baixo ARM, baixa IAG)"
print(f"  Quadrante: {quadrante}")

# ── 4. Gaps AIPI ────────────────────────────────────────────────────────────
print("\n── Gaps nos Pilares AIPI ──")
aipi_pilares = ['aipi_digital', 'aipi_humano', 'aipi_inovacao', 'aipi_regulacao']
aipi_gaps = {}
for pilar in aipi_pilares:
    br_val = br[pilar].values[0] if len(br) > 0 else 0
    top10 = df[pilar].quantile(0.9)
    media_ocde = df[df['renda'] == 'alta_renda'][pilar].mean()
    gap_top10 = top10 - br_val
    gap_ocde = media_ocde - br_val
    aipi_gaps[pilar] = {
        'brasil': round(br_val, 1),
        'top10_global': round(top10, 1),
        'media_ocde': round(media_ocde, 1),
        'gap_top10': round(gap_top10, 1),
        'gap_ocde': round(gap_ocde, 1)
    }
    print(f"  {pilar:20s} BR={br_val:<6.1f} OCDE_μ={media_ocde:<6.1f} "
          f"TOP10={top10:<6.1f}  gap_OCDE={gap_ocde:+.1f}")

# ── 5. Países comparáveis (renda média) ─────────────────────────────────────
print("\n── Países de Renda Média Comparáveis ──")
rm = df[df['renda'].isin(['renda_media_alta', 'renda_media_baixa'])]
rm_sorted = rm.sort_values('escape_arm', ascending=False)
top_rm = rm_sorted[['pais', 'renda', 'escape_arm', 'aipi_total', 'pib_pc_ppc']].head(15)
print(top_rm.to_string(index=False))

# Posição do Brasil entre renda média
br_pos = rm_sorted['pais'].tolist().index('Brazil') if 'Brazil' in rm_sorted['pais'].tolist() else 'N/A'
print(f"  Posição do Brasil entre países de renda média: {br_pos+1}° de {len(rm_sorted)}")

# ── Salvar ──────────────────────────────────────────────────────────────────
resultados = {
    'perfil_brasil': br_profile,
    'comparacao_latam': {k: {kk: vv for kk, vv in v.items() if kk != 'latam_std'} 
                         for k, v in comparacao.items()},
    'matriz_arm_iag': {
        'quadrante': quadrante,
        'escape_arm': round(br_escape, 4),
        'aipi_total': round(br_aipi, 1),
        'percentil_escape': round(pct_escape, 1),
        'percentil_aipi': round(pct_aipi, 1),
        'mediana_escape': round(med_escape, 4),
        'mediana_aipi': round(med_aipi, 1)
    },
    'gaps_aipi': aipi_gaps,
    'posicao_renda_media': {
        'posicao': br_pos if br_pos != 'N/A' else 'N/A',
        'total': len(rm_sorted)
    }
}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)
print(f"\nResultados salvos em: {OUT}")
