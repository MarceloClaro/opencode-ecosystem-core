#!/usr/bin/env python3
"""
Gera 3 novas figuras para o pipeline v3 (complexidade economica).
Figura 8: Feature importance comparison v2 vs v3 (14 features)
Figura 9: Product density distribution by income group
Figura 10: Knowledge complexity vs GDP per capita (ARM highlight)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import os, warnings
warnings.filterwarnings("ignore")

# ========== CONFIG ==========
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "ml_pipeline", "outputs")
FIG_DIR = os.path.join(OUTPUT_DIR, "figuras")
os.makedirs(FIG_DIR, exist_ok=True)

# Paleta
COR_NOVAS = '#E74C3C'
COR_EXIST = '#2C3E50'
COR_ARM = '#E74C3C'
COR_NAO_ARM = '#3498DB'
COR_DESTAQUE = '#F39C12'

# Carregar dados
df = pd.read_csv(os.path.join(OUTPUT_DIR, "dataset_ml_v3.csv"))
fi = pd.read_csv(os.path.join(OUTPUT_DIR, "feature_importance_v3.csv"))
cluster_df = pd.read_csv(os.path.join(OUTPUT_DIR, "clusters_v3.csv"))

# Mapear income_level
income_map = {'high': 'Alta Renda', 'middle': 'Renda M\u00e9dia', 'low': 'Baixa Renda'}
df['income_label'] = df['income_level'].map(income_map)

novas_features = ['knowledge_complexity', 'export_sophistication', 'product_density']
label_map = {
    'gdp_per_capita': 'PIB per capita',
    'product_density': 'product_density \u2605',
    'knowledge_complexity': 'knowledge_complexity \u2605',
    'fdi_inflows': 'IDE',
    'internet_users': 'Internet',
    'rd_spending': 'P&D',
    'services_emp': 'Servi\u00e7os',
    'gini': 'Gini',
    'high_tech_exp': 'Alta Tecnologia',
    'export_sophistication': 'export_sophistication \u2605',
    'unemployment': 'Desemprego',
    'tertiary_enrollment': 'Ensino Superior',
    'patent_apps': 'Patentes',
    'ai_readiness': 'AI Readiness',
}

# ============================================================
# FIGURA 8: Feature Importance v3
# ============================================================
print("[Figura 8] Feature importance v3...")

fig, axes = plt.subplots(1, 2, figsize=(16, 8))

fi_sorted = fi.sort_values('importance_rf', ascending=True)
colors_rf = [COR_NOVAS if f in novas_features else COR_EXIST for f in fi_sorted['feature']]
labels_rf = [label_map.get(f, f) for f in fi_sorted['feature']]

axes[0].barh(range(len(fi_sorted)), fi_sorted['importance_rf'].values, color=colors_rf, height=0.7, edgecolor='white')
axes[0].set_yticks(range(len(fi_sorted)))
axes[0].set_yticklabels(labels_rf, fontsize=10)
axes[0].set_xlabel('Import\u00e2ncia (Random Forest)', fontsize=12, fontweight='bold')
axes[0].set_title('A. Import\u00e2ncia RF para Classifica\u00e7\u00e3o ARM', fontsize=13, fontweight='bold', loc='left')
axes[0].axvline(x=0, color='gray', linewidth=0.5)

for i, (_, row) in enumerate(fi_sorted.iterrows()):
    if row['feature'] in novas_features:
        axes[0].text(row['importance_rf'] + 0.002, i, f"  {row['importance_rf']:.1%}",
                      va='center', fontsize=9, color=COR_NOVAS, fontweight='bold')

fi_perm = fi.sort_values('importance_perm', ascending=True)
colors_perm = [COR_NOVAS if f in novas_features else COR_EXIST for f in fi_perm['feature']]
labels_perm = [label_map.get(f, f) for f in fi_perm['feature']]

axes[1].barh(range(len(fi_perm)), fi_perm['importance_perm'].values,
             xerr=fi_perm['importance_perm_std'].values, color=colors_perm, height=0.7,
             edgecolor='white', capsize=3, ecolor='gray', alpha=0.9)
axes[1].set_yticks(range(len(fi_perm)))
axes[1].set_yticklabels(labels_perm, fontsize=10)
axes[1].set_xlabel('Import\u00e2ncia (Permutation, 20 reps)', fontsize=12, fontweight='bold')
axes[1].set_title('B. Permutation Importance p/ Classifica\u00e7\u00e3o ARM', fontsize=13, fontweight='bold', loc='left')
axes[1].axvline(x=0, color='gray', linewidth=0.5)

for i, (_, row) in enumerate(fi_perm.iterrows()):
    if row['feature'] in novas_features:
        val = row['importance_perm']
        err = row['importance_perm_std']
        axes[1].text(val + 0.002 + err, i, f"  {val:.1%}",
                      va='center', fontsize=9, color=COR_NOVAS, fontweight='bold')

legend_elements = [
    Patch(facecolor=COR_NOVAS, label='Novas features (v3)'),
    Patch(facecolor=COR_EXIST, label='Features originais (v1/v2)'),
]
fig.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.02),
           ncol=2, fontsize=11, frameon=False)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'fig8_feature_importance_v3.png'), dpi=200, bbox_inches='tight')
plt.close()
print("  -> OK")

# ============================================================
# FIGURA 9: Product Density
# ============================================================
print("[Figura 9] Product density...")

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

order = ['Baixa Renda', 'Renda M\u00e9dia', 'Alta Renda']
box_data = []
for lbl in order:
    vals = df[df['income_label'] == lbl]['product_density'].dropna()
    box_data.append(vals)

bp = axes[0].boxplot(box_data, labels=order, patch_artist=True, widths=0.5,
                      showmeans=True, meanprops=dict(marker='D', markerfacecolor='white',
                                                     markeredgecolor='darkred', markersize=8))
colors_box = ['#E74C3C', '#F39C12', '#2ECC71']
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)

for i, vals in enumerate(box_data):
    jitter = np.random.normal(0, 0.04, len(vals))
    axes[0].scatter(np.ones(len(vals)) * (i + 1) + jitter, vals, alpha=0.3, s=15,
                    color=colors_box[i], edgecolor='white', linewidth=0.3)

axes[0].set_ylabel('Product Density', fontsize=12, fontweight='bold')
axes[0].set_title('A. Densidade Produtiva por Grupo de Renda', fontsize=13, fontweight='bold', loc='left')
axes[0].grid(axis='y', alpha=0.3)

for i, lbl in enumerate(order):
    vals = df[df['income_label'] == lbl]['product_density'].dropna()
    axes[0].text(i + 1, vals.max() + 0.03, f'm\u00e9dia={vals.mean():.2f}\nmediana={vals.median():.2f}',
                 ha='center', fontsize=8, color='gray')

gdp = df['gdp_per_capita'].values
density = df['product_density'].values
arm = df['arm_relative'].values == 1
income = df['income_label'].values

for lbl, color, marker in [('Baixa Renda', '#E74C3C', 'o'), ('Renda M\u00e9dia', '#F39C12', 's'), ('Alta Renda', '#2ECC71', '^')]:
    mask = (income == lbl) & (~arm)
    axes[1].scatter(gdp[mask], density[mask], c=color, marker=marker, label=lbl,
                    alpha=0.5, s=20, edgecolor='white', linewidth=0.3)

arm_mask = arm
axes[1].scatter(gdp[arm_mask], density[arm_mask], c='red', marker='X', s=80,
                label='ARM Relativo', edgecolor='black', linewidth=0.8, zorder=5)

notaveis = {'CHN': 'China', 'KOR': 'Coreia do Sul', 'SGP': 'Cingapura',
            'BRA': 'Brasil', 'USA': 'EUA', 'IND': '\u00cdndia', 'ZAF': '\u00c1frica do Sul'}
for eco, nome in notaveis.items():
    row = df[df['economy'] == eco]
    if len(row) > 0:
        r = row.iloc[0]
        axes[1].annotate(nome, (r['gdp_per_capita'], r['product_density']),
                         fontsize=8, ha='center', va='bottom',
                         bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='gray'))

axes[1].set_xlabel('PIB per capita (US$)', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Product Density', fontsize=12, fontweight='bold')
axes[1].set_title('B. Densidade Produtiva vs PIB per capita', fontsize=13, fontweight='bold', loc='left')
axes[1].legend(fontsize=9, loc='lower right')
axes[1].grid(alpha=0.3)
axes[1].set_xscale('symlog', linthresh=1000)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'fig9_product_density_income.png'), dpi=200, bbox_inches='tight')
plt.close()
print("  -> OK")

# ============================================================
# FIGURA 10: Knowledge Complexity
# ============================================================
print("[Figura 10] Knowledge complexity...")

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

kci = df['knowledge_complexity'].values

for lbl, color, marker in [('Baixa Renda', '#E74C3C', 'o'), ('Renda M\u00e9dia', '#F39C12', 's'), ('Alta Renda', '#2ECC71', '^')]:
    mask = (income == lbl) & (~arm)
    axes[0].scatter(gdp[mask], kci[mask], c=color, marker=marker, label=lbl,
                    alpha=0.5, s=20, edgecolor='white', linewidth=0.3)

axes[0].scatter(gdp[arm_mask], kci[arm_mask], c='red', marker='X', s=80,
                label='ARM Relativo', edgecolor='black', linewidth=0.8, zorder=5)

for eco, nome in notaveis.items():
    row = df[df['economy'] == eco]
    if len(row) > 0:
        r = row.iloc[0]
        axes[0].annotate(nome, (r['gdp_per_capita'], r['knowledge_complexity']),
                         fontsize=8, ha='center', va='bottom',
                         bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='gray'))

axes[0].set_xlabel('PIB per capita (US$)', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Knowledge Complexity (KCI proxy)', fontsize=12, fontweight='bold')
axes[0].set_title('A. Complexidade do Conhecimento vs PIB per capita', fontsize=13, fontweight='bold', loc='left')
axes[0].legend(fontsize=9, loc='lower right')
axes[0].grid(alpha=0.3)
axes[0].set_xscale('symlog', linthresh=1000)
axes[0].axhline(y=0, color='gray', linestyle='--', alpha=0.4)

df_cluster = df.merge(cluster_df[['economy', 'cluster']], on='economy', how='left')
cluster_order = sorted(cluster_df['cluster'].unique())
cluster_palette = {0: '#F39C12', 1: '#E74C3C', 2: '#2ECC71', 3: '#9B59B6'}
cluster_labels = {
    0: 'C0: Renda M\u00e9dia\n(125, 21 ARM)',
    1: 'C1: Baixa Renda\n(84, 8 ARM)',
    2: 'C2: Alta Renda\n(52, 0 ARM)',
    3: 'C3: Outlier (1)',
}

positions = []
data_for_boxes = []
cluster_names = []
for c in cluster_order:
    vals = df_cluster[df_cluster['cluster'] == c]['knowledge_complexity'].dropna()
    if len(vals) > 0:
        positions.append(c + 1)
        data_for_boxes.append(vals)
        cluster_names.append(cluster_labels.get(c, f'C{c}'))

bp2 = axes[1].boxplot(data_for_boxes, positions=positions, patch_artist=True, widths=0.5,
                       showmeans=True, meanprops=dict(marker='D', markerfacecolor='white',
                                                      markeredgecolor='darkred', markersize=8))
for j, patch in enumerate(bp2['boxes']):
    if j < len(cluster_order):
        patch.set_facecolor(cluster_palette[cluster_order[j]])
        patch.set_alpha(0.6)

for j, (pos, vals) in enumerate(zip(positions, data_for_boxes)):
    jitter = np.random.normal(0, 0.06, len(vals))
    c = cluster_palette[cluster_order[j]]
    axes[1].scatter(np.ones(len(vals)) * pos + jitter, vals, alpha=0.3, s=12,
                    color=c, edgecolor='white', linewidth=0.3)

axes[1].set_xticks(positions)
axes[1].set_xticklabels(cluster_names, fontsize=9)
axes[1].set_ylabel('Knowledge Complexity (KCI proxy)', fontsize=12, fontweight='bold')
axes[1].set_title('B. Complexidade do Conhecimento por Cluster', fontsize=13, fontweight='bold', loc='left')
axes[1].grid(axis='y', alpha=0.3)
axes[1].axhline(y=0, color='gray', linestyle='--', alpha=0.4)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'fig10_knowledge_complexity_scatter.png'), dpi=200, bbox_inches='tight')
plt.close()
print("  -> OK")

print("\n=== TODAS AS 3 FIGURAS V3 GERADAS ===")
print(f"Pasta: {FIG_DIR}")
for f in sorted(os.listdir(FIG_DIR)):
    if f.endswith('.png'):
        size = os.path.getsize(os.path.join(FIG_DIR, f)) / 1024
        print(f"  {f}: {size:.0f} KB")
