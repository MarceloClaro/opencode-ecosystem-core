#!/usr/bin/env python3
"""
Gera as 3 figuras do artigo R503 em português.
Saída: figures/fig1_accuracies.pdf, fig2_matrix.pdf, fig3_latency.pdf
"""
import json, math, os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
import numpy as np
from scipy.stats import beta as beta_dist

# ── Dados ──
DATAPATH = Path(__file__).resolve().parents[1] / "benchmark_9x3.json"
OUTDIR   = Path(__file__).resolve().parent / "figures"
OUTDIR.mkdir(exist_ok=True)

d = json.load(open(DATAPATH, encoding="utf-8"))
models = ["opencode/mimo-v2.5-free", "opencode/big-pickle", "opencode/nemotron-3-ultra-free"]
labels = ["mimo-v2.5", "big-pickle", "nemotron-3"]
colors = ["#2e74b5", "#e8a012", "#d62828"]
N = 9

# ── Helpers ──
def clopper_pearson(k, n, alpha=0.05):
    if k == 0: lo, hi = 0.0, 1 - alpha**(1/n)
    elif k == n: lo, hi = alpha**(1/n), 1.0
    else: lo = beta_dist.ppf(alpha/2, k, n-k+1); hi = beta_dist.ppf(1-alpha/2, k+1, n-k)
    return lo, hi

# ── Figura 1: Acurácia com IC ──
fig1, ax1 = plt.subplots(figsize=(7, 4.5))
accs, los, his = [], [], []
for m in models:
    rs = d[m]; k = sum(r["correct"] for r in rs); n = len(rs)
    acc = k/n; lo, hi = clopper_pearson(k, n)
    accs.append(acc); los.append(lo); his.append(hi)

bars = ax1.bar(labels, accs, color=colors, width=0.55, edgecolor='white', linewidth=1.2, zorder=3)
for i, (acc, lo, hi) in enumerate(zip(accs, los, his)):
    err_lo = acc - lo; err_hi = hi - acc
    ax1.errorbar(i, acc, yerr=[[err_lo],[err_hi]], fmt='none', ecolor='black', capsize=6, capthick=1.8, elinewidth=1.8, zorder=4)
    ax1.text(i, hi + 0.03, f'{acc:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

ax1.set_ylabel('Acurácia (proporção de acertos)', fontsize=12)
ax1.set_title('Acurácia com IC Clopper-Pearson 95% (n = 9)', fontsize=13, fontweight='bold')
ax1.set_ylim(-0.02, 0.72)
ax1.yaxis.set_major_locator(mticker.MultipleLocator(0.1))
ax1.axhline(1/9, color='gray', ls='--', lw=0.8, alpha=0.5, label='acaso (1/9)')
ax1.legend(fontsize=9, loc='upper right')
ax1.grid(axis='y', alpha=0.3, zorder=0)
ax1.spines['top'].set_visible(False); ax1.spines['right'].set_visible(False)
fig1.tight_layout()
fig1.savefig(OUTDIR / 'fig1_accuracies.pdf', dpi=300)
plt.close(fig1)
print("Figura 1 salva.")

# ── Figura 2: Matriz 9×3 ──
probs = [r["problem"] for r in d[models[0]]]
prob_labels = [
    "Alg-001\n(piso)", "Alg-004\n(desig.)", "NT-001\n(p^3-q^5)",
    "Comb-001\n(máxloc)", "Alg-002\n(2^n>n^2)", "NT-002\n(p^2|2^p+1)",
    "NT-003\n(v₃(2023!))", "Comb-002\n(S₅)", "Geo-001\n(2023-gono)"
]

matrix = np.zeros((N, 3), dtype=int)
for j, m in enumerate(models):
    for i in range(N):
        matrix[i, j] = 1 if d[m][i]["correct"] else 0

fig2, ax2 = plt.subplots(figsize=(8, 5.5))
cmap = matplotlib.colors.ListedColormap(['#f0f0f0', '#2e74b5'])
ax2.imshow(matrix, cmap=cmap, aspect='auto', interpolation='nearest')

for i in range(N):
    for j in range(3):
        txt = '✓' if matrix[i,j]==1 else '·'
        col = 'white' if matrix[i,j]==1 else '#888888'
        ax2.text(j, i, txt, ha='center', va='center', fontsize=18, color=col, fontweight='bold')

ax2.set_xticks(range(3)); ax2.set_xticklabels(labels, fontsize=11, fontweight='bold')
ax2.set_yticks(range(N)); ax2.set_yticklabels(prob_labels, fontsize=9)
ax2.set_title('Matriz de acertos: 9 problemas × 3 modelos', fontsize=13, fontweight='bold')
ax2.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
ax2.spines[:].set_visible(False)

# Grid lines
for i in range(N+1): ax2.axhline(i-0.5, color='white', lw=1.5)
for j in range(4): ax2.axvline(j-0.5, color='white', lw=1.5)

fig2.tight_layout()
fig2.savefig(OUTDIR / 'fig2_matrix.pdf', dpi=300)
plt.close(fig2)
print("Figura 2 salva.")

# ── Figura 3: Latência ──
fig3, ax3 = plt.subplots(figsize=(7, 4.5))
positions = []; data_for_box = []; colors_for_box = []

for j, (m, lab, col) in enumerate(zip(models, labels, colors)):
    ts = [r["elapsed_s"] for r in d[m] if r["status"]=="ok"]
    to_times = [r["elapsed_s"] for r in d[m] if r["status"]=="timeout"]
    if ts:
        data_for_box.append(ts); positions.append(j); colors_for_box.append(col)
    if to_times:
        ax3.scatter([j]*len(to_times), to_times, marker='D', color='red', s=60, zorder=5, edgecolors='black', linewidths=0.8, label='timeout' if j==0 else None)

bp = ax3.boxplot(data_for_box, positions=positions, widths=0.4, patch_artist=True,
                 medianprops=dict(color='black', lw=2), whiskerprops=dict(color='black'),
                 capprops=dict(color='black'), flierprops=dict(marker='o', markerfacecolor='gray', markersize=5))
for patch, col in zip(bp['boxes'], colors_for_box):
    patch.set_facecolor(col); patch.set_alpha(0.6); patch.set_edgecolor('black')

ax3.set_xticks(range(3)); ax3.set_xticklabels(labels, fontsize=11, fontweight='bold')
ax3.set_ylabel('Latência (segundos)', fontsize=12)
ax3.set_title('Distribuição de latência por modelo (chamadas ok)', fontsize=13, fontweight='bold')
ax3.grid(axis='y', alpha=0.3)
ax3.spines['top'].set_visible(False); ax3.spines['right'].set_visible(False)
if to_times: ax3.legend(fontsize=9, loc='upper left')
fig3.tight_layout()
fig3.savefig(OUTDIR / 'fig3_latency.pdf', dpi=300)
plt.close(fig3)
print("Figura 3 salva.")
print("Todas as figuras geradas em", OUTDIR)