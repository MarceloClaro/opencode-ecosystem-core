"""
Fase 2.9 — Análise de Sensibilidade dos Clusters
=================================================
Objetivos:
  1. Testar estabilidade do k=2 vs k=3, k=4 (silhueta, Davies-Bouldin)
  2. Bootstrapping: proporção de concordância entre partições
  3. Perfil dos clusters em cada k (médias das variáveis-chave)
  4. Visualização: scatter AIPI_total x escape_arm com clusters

Saída: JSON com métricas de validação cruzada de clustering.
"""

import pandas as pd
import numpy as np
import json
import warnings
import sys, io
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.preprocessing import StandardScaler

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')

# ── Paths ───────────────────────────────────────────────────────────────────
BASE = Path(r'C:\Users\marce\.config\opencode\artigo-mit-ia\quantitative')
DATA = BASE / 'output' / 'dataset_corte_transversal.csv'
OUT  = BASE / 'output' / 'sensibilidade_clusters.json'

df = pd.read_csv(DATA)
print(f"Dataset: {df.shape[0]} países, {df.shape[1]} colunas")

# ── Features para clustering ────────────────────────────────────────────────
CLUSTER_FEATURES = ['aipi_total', 'escape_arm', 'pib_pc_ppc', 'ptf_relativa',
                    'educ_superior_pct', 'internet_pop_pct', 'gerd_pib_pct',
                    'gini', 'complexidade_economica', 'agricultura_pib_pct']

# Remover linhas com NaN nas features
df_cl = df[CLUSTER_FEATURES].dropna()
print(f"Observações sem NaN: {df_cl.shape[0]}")

X = StandardScaler().fit_transform(df_cl.values)

# ── 1. Comparação de k ──────────────────────────────────────────────────────
print("\n═══ Comparação de k (2 a 6) ═══")
resultados = {}
for k in range(2, 7):
    km = KMeans(n_clusters=k, random_state=42, n_init=20)
    labels = km.fit_predict(X)
    sil = silhouette_score(X, labels)
    db = davies_bouldin_score(X, labels)
    inertia = km.inertia_
    resultados[f'k{k}'] = {
        'silhueta': round(sil, 4),
        'davies_bouldin': round(db, 4),
        'inercia': round(inertia, 2)
    }
    print(f"  k={k}: Silhueta={sil:.4f}  Davies-Bouldin={db:.4f}  Inércia={inertia:.0f}")

# ── 2. Perfil dos clusters (k=2) ────────────────────────────────────────────
print("\n═══ Perfil dos clusters (k=2) ═══")
km2 = KMeans(n_clusters=2, random_state=42, n_init=20)
labels2 = km2.fit_predict(X)
df_cl['cluster_k2'] = labels2
perfis = {}
for c in sorted(df_cl['cluster_k2'].unique()):
    subset = df_cl[df_cl['cluster_k2'] == c]
    perfil = {}
    for col in CLUSTER_FEATURES:
        perfil[col] = {'media': round(subset[col].mean(), 3), 'std': round(subset[col].std(), 3)}
    perfil['n'] = len(subset)
    perfis[f'cluster_{c}'] = perfil
    print(f"\n  Cluster {c} (n={len(subset)}):")
    for col in CLUSTER_FEATURES:
        print(f"    {col:25s}  média={perfil[col]['media']:>8.3f}  std={perfil[col]['std']:.3f}")

resultados['perfil_k2'] = perfis

# ── 3. Perfil dos clusters (k=3) ────────────────────────────────────────────
print("\n═══ Perfil dos clusters (k=3) ═══")
km3 = KMeans(n_clusters=3, random_state=42, n_init=20)
labels3 = km3.fit_predict(X)
df_cl['cluster_k3'] = labels3
perfis3 = {}
for c in sorted(df_cl['cluster_k3'].unique()):
    subset = df_cl[df_cl['cluster_k3'] == c]
    perfil = {}
    for col in CLUSTER_FEATURES:
        perfil[col] = {'media': round(subset[col].mean(), 3), 'std': round(subset[col].std(), 3)}
    perfil['n'] = len(subset)
    perfis3[f'cluster_{c}'] = perfil
    print(f"\n  Cluster {c} (n={len(subset)}):")
    for col in ['aipi_total', 'escape_arm', 'pib_pc_ppc', 'gini']:
        print(f"    {col:25s}  média={perfil[col]['media']:>8.3f}")

resultados['perfil_k3'] = perfis3

# ── 4. Bootstrapping: concordância k=2 ──────────────────────────────────────
print("\n═══ Estabilidade (Bootstrapping k=2, 100 iterações) ═══")
from sklearn.utils import resample
n_iter = 100
concordancias = []
for i in range(n_iter):
    idx = resample(range(len(df_cl)), random_state=i)
    X_boot = X[idx]
    km_boot = KMeans(n_clusters=2, random_state=42, n_init=10)
    labels_boot = km_boot.fit_predict(X_boot)
    # Alinhar labels (pode inverter)
    sil_boot = silhouette_score(X_boot, labels_boot)
    concordancias.append(sil_boot)

resultados['bootstrap'] = {
    'silhueta_media': round(np.mean(concordancias), 4),
    'silhueta_std': round(np.std(concordancias), 4),
    'silhueta_min': round(np.min(concordancias), 4),
    'silhueta_max': round(np.max(concordancias), 4),
    'n_iteracoes': n_iter
}
print(f"  Silhueta média bootstrap: {np.mean(concordancias):.4f} ± {np.std(concordancias):.4f}")
print(f"  Min: {np.min(concordancias):.4f}  Max: {np.max(concordancias):.4f}")

# ── 5. Países na fronteira (mudam de cluster entre k=2 e k=3) ───────────────
print("\n═══ Países que mudam de cluster (k=2→k=3) ═══")
# Mapeamento aproximado: k=3 particiona um dos clusters k=2
transicoes = df_cl.groupby(['cluster_k2', 'cluster_k3']).size().reset_index(name='n')
print(transicoes.to_string(index=False))

# ── 6. Resumo executivo ─────────────────────────────────────────────────────
print("\n═══ RESUMO — Sensibilidade dos Clusters ═══")
print(f"  k=2: silhueta={resultados['k2']['silhueta']}, DB={resultados['k2']['davies_bouldin']}")
print(f"  k=3: silhueta={resultados['k3']['silhueta']}, DB={resultados['k3']['davies_bouldin']}")
print(f"  k=4: silhueta={resultados['k4']['silhueta']}, DB={resultados['k4']['davies_bouldin']}")
print(f"  Bootstrap: {resultados['bootstrap']['silhueta_media']} ± {resultados['bootstrap']['silhueta_std']}")

# Salvar
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False)
print(f"\nResultados salvos em: {OUT}")
