#!/usr/bin/env python3
"""
Generate publication-quality figures for the algorithmic bias manuscript.
Figures: fairness heatmap, performance bar chart, intersectional analysis.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import os

# Output directory
OUTPUT_DIR = '/home/marceloclaro/opencode-ecosystem-core/research/output/figures'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Data from experiments
models = ['Logistic\nRegression', 'Random\nForest', 'Gradient\nBoosting', 'SVM']
models_short = ['LR', 'RF', 'GB', 'SVM']

# Performance data
test_f1 = [0.8272, 0.7875, 0.7805, 0.8313]
auc_roc = [0.8877, 0.8731, 0.8543, 0.8794]
accuracy = [0.8052, 0.7727, 0.7792, 0.8117]
cv_f1_mean = [0.7929, 0.7679, 0.7769, 0.7859]
cv_f1_std = [0.0313, 0.0243, 0.0221, 0.0229]

# Fairness data - Ethnicity
eod_ethnicity = [0.0687, 0.0306, 0.0636, 0.0492]
dpd_ethnicity = [0.0479, 0.0324, 0.0201, 0.0148]
fpr_maj_eth = [0.182, 0.200, 0.164, 0.182]
fpr_min_eth = [0.375, 0.417, 0.333, 0.375]

# Fairness data - Gender
eod_gender = [0.0838, 0.1143, 0.0787, 0.0566]
dpd_gender = [0.1010, 0.1010, 0.0843, 0.0672]
fpr_male = [0.182, 0.200, 0.164, 0.182]
fpr_female = [0.375, 0.417, 0.333, 0.375]

# Intersectional data
groups = ['Majority-\nFemale', 'Majority-\nMale', 'Minority-\nFemale', 'Minority-\nMale']
groups_short = ['Maj-F', 'Maj-M', 'Min-F', 'Min-M']
inter_accuracy = [0.8000, 0.8125, 0.7826, 0.8000]
inter_f1 = [0.8235, 0.8276, 0.7500, 0.7273]
inter_tpr = [0.833, 0.833, 0.714, 0.750]

# Color scheme
COLORS = {
    'primary': '#2C3E50',
    'secondary': '#3498DB',
    'accent': '#E74C3C',
    'success': '#27AE60',
    'warning': '#F39C12',
    'bg': '#ECF0F1',
    'palette': ['#3498DB', '#2ECC71', '#F39C12', '#E74C3C']
}

plt.rcParams.update({
    'font.size': 10,
    'font.family': 'DejaVu Sans',
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.spines.top': False,
    'axes.spines.right': False,
})

# =============================================================================
# FIGURE 1: Performance Comparison (Bar Chart)
# =============================================================================
fig1, axes1 = plt.subplots(1, 3, figsize=(14, 4.5))

x = np.arange(len(models))
width = 0.6

# F1-Score
bars1 = axes1[0].bar(x, test_f1, width, color=COLORS['palette'], edgecolor='white', linewidth=0.5)
axes1[0].set_ylabel('F1-Score')
axes1[0].set_title('(A) Test F1-Score')
axes1[0].set_xticks(x)
axes1[0].set_xticklabels(models_short)
axes1[0].set_ylim(0.70, 0.88)
axes1[0].axhline(y=np.mean(test_f1), color=COLORS['accent'], linestyle='--', alpha=0.7, label=f'Mean: {np.mean(test_f1):.4f}')
axes1[0].legend(loc='lower right')
for bar, val in zip(bars1, test_f1):
    axes1[0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.003,
                  f'{val:.4f}', ha='center', va='bottom', fontsize=8)

# AUC-ROC
bars2 = axes1[1].bar(x, auc_roc, width, color=COLORS['palette'], edgecolor='white', linewidth=0.5)
axes1[1].set_ylabel('AUC-ROC')
axes1[1].set_title('(B) AUC-ROC')
axes1[1].set_xticks(x)
axes1[1].set_xticklabels(models_short)
axes1[1].set_ylim(0.80, 0.92)
axes1[1].axhline(y=np.mean(auc_roc), color=COLORS['accent'], linestyle='--', alpha=0.7, label=f'Mean: {np.mean(auc_roc):.4f}')
axes1[1].legend(loc='lower right')
for bar, val in zip(bars2, auc_roc):
    axes1[1].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.003,
                  f'{val:.4f}', ha='center', va='bottom', fontsize=8)

# Cross-validation F1
bars3 = axes1[2].bar(x, cv_f1_mean, width, yerr=cv_f1_std, color=COLORS['palette'], 
                      edgecolor='white', linewidth=0.5, capsize=4)
axes1[2].set_ylabel('CV F1-Score (mean±sd)')
axes1[2].set_title('(C) 5-Fold Cross-Validation')
axes1[2].set_xticks(x)
axes1[2].set_xticklabels(models_short)
axes1[2].set_ylim(0.70, 0.88)
axes1[2].axhline(y=np.mean(cv_f1_mean), color=COLORS['accent'], linestyle='--', alpha=0.7, label=f'Mean: {np.mean(cv_f1_mean):.4f}')
axes1[2].legend(loc='lower right')
for bar, val, err in zip(bars3, cv_f1_mean, cv_f1_std):
    axes1[2].text(bar.get_x() + bar.get_width()/2., bar.get_height() + err + 0.003,
                  f'{val:.4f}', ha='center', va='bottom', fontsize=8)

fig1.suptitle('Figure 1: Model Performance Comparison', fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
fig1.savefig(f'{OUTPUT_DIR}/fig1_performance.png', dpi=300, bbox_inches='tight')
plt.close(fig1)
print("✓ Figure 1 saved: fig1_performance.png")

# =============================================================================
# FIGURE 2: Fairness Heatmap
# =============================================================================
fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))

# Fairness matrix for ethnicity
fairness_eth = np.array([
    eod_ethnicity,
    dpd_ethnicity,
    fpr_maj_eth,
    fpr_min_eth,
    [fpr_min_eth[i] - fpr_maj_eth[i] for i in range(4)]
])
fairness_labels = ['EOD', 'DPD', 'FPR (Majority)', 'FPR (Minority)', 'FPR Gap']

im1 = axes2[0].imshow(fairness_eth, cmap='RdYlBu_r', aspect='auto', vmin=0, vmax=0.45)
axes2[0].set_xticks(range(4))
axes2[0].set_xticklabels(models_short)
axes2[0].set_yticks(range(5))
axes2[0].set_yticklabels(fairness_labels)
axes2[0].set_title('(A) Ethnicity Fairness Metrics')

# Add text annotations
for i in range(5):
    for j in range(4):
        text = axes2[0].text(j, i, f'{fairness_eth[i, j]:.4f}',
                            ha="center", va="center", color="black", fontsize=8)

# Fairness matrix for gender
fairness_gen = np.array([
    eod_gender,
    dpd_gender,
    fpr_male,
    fpr_female,
    [fpr_female[i] - fpr_male[i] for i in range(4)]
])

im2 = axes2[1].imshow(fairness_gen, cmap='RdYlBu_r', aspect='auto', vmin=0, vmax=0.45)
axes2[1].set_xticks(range(4))
axes2[1].set_xticklabels(models_short)
axes2[1].set_yticks(range(5))
axes2[1].set_yticklabels(fairness_labels)
axes2[1].set_title('(B) Gender Fairness Metrics')

# Add text annotations
for i in range(5):
    for j in range(4):
        text = axes2[1].text(j, i, f'{fairness_gen[i, j]:.4f}',
                            ha="center", va="center", color="black", fontsize=8)

# Add colorbars
fig2.colorbar(im1, ax=axes2[0], shrink=0.8, label='Metric Value')
fig2.colorbar(im2, ax=axes2[1], shrink=0.8, label='Metric Value')

fig2.suptitle('Figure 2: Fairness Metrics Heatmap', fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
fig2.savefig(f'{OUTPUT_DIR}/fig2_fairness_heatmap.png', dpi=300, bbox_inches='tight')
plt.close(fig2)
print("✓ Figure 2 saved: fig2_fairness_heatmap.png")

# =============================================================================
# FIGURE 3: Intersectional Analysis
# =============================================================================
fig3, axes3 = plt.subplots(1, 3, figsize=(14, 4.5))

x = np.arange(len(groups))
width = 0.6

# Accuracy by group
colors_inter = [COLORS['success'], COLORS['secondary'], COLORS['warning'], COLORS['accent']]
bars_acc = axes3[0].bar(x, inter_accuracy, width, color=colors_inter, edgecolor='white', linewidth=0.5)
axes3[0].set_ylabel('Accuracy')
axes3[0].set_title('(A) Accuracy by Subgroup')
axes3[0].set_xticks(x)
axes3[0].set_xticklabels(groups_short)
axes3[0].set_ylim(0.70, 0.88)
axes3[0].axhline(y=np.mean(inter_accuracy), color=COLORS['primary'], linestyle='--', alpha=0.7, label=f'Mean: {np.mean(inter_accuracy):.4f}')
axes3[0].legend(loc='lower right')
for bar, val in zip(bars_acc, inter_accuracy):
    axes3[0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.003,
                  f'{val:.4f}', ha='center', va='bottom', fontsize=8)

# F1-Score by group
bars_f1 = axes3[1].bar(x, inter_f1, width, color=colors_inter, edgecolor='white', linewidth=0.5)
axes3[1].set_ylabel('F1-Score')
axes3[1].set_title('(B) F1-Score by Subgroup')
axes3[1].set_xticks(x)
axes3[1].set_xticklabels(groups_short)
axes3[1].set_ylim(0.65, 0.90)
axes3[1].axhline(y=np.mean(inter_f1), color=COLORS['primary'], linestyle='--', alpha=0.7, label=f'Mean: {np.mean(inter_f1):.4f}')
axes3[1].legend(loc='lower right')
for bar, val in zip(bars_f1, inter_f1):
    axes3[1].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.003,
                  f'{val:.4f}', ha='center', va='bottom', fontsize=8)

# TPR by group
bars_tpr = axes3[2].bar(x, inter_tpr, width, color=colors_inter, edgecolor='white', linewidth=0.5)
axes3[2].set_ylabel('True Positive Rate')
axes3[2].set_title('(C) TPR by Subgroup')
axes3[2].set_xticks(x)
axes3[2].set_xticklabels(groups_short)
axes3[2].set_ylim(0.60, 0.90)
axes3[2].axhline(y=np.mean(inter_tpr), color=COLORS['primary'], linestyle='--', alpha=0.7, label=f'Mean: {np.mean(inter_tpr):.4f}')
axes3[2].legend(loc='lower right')
for bar, val in zip(bars_tpr, inter_tpr):
    axes3[2].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.003,
                  f'{val:.3f}', ha='center', va='bottom', fontsize=8)

# Add legend for groups
patches = [mpatches.Patch(color=c, label=l) for c, l in zip(colors_inter, ['Majority-Female', 'Majority-Male', 'Minority-Female', 'Minority-Male'])]
fig3.legend(handles=patches, loc='lower center', ncol=4, bbox_to_anchor=(0.5, -0.08))

fig3.suptitle('Figure 3: Intersectional Analysis (Gender × Ethnicity)', fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
fig3.savefig(f'{OUTPUT_DIR}/fig3_intersectional.png', dpi=300, bbox_inches='tight')
plt.close(fig3)
print("✓ Figure 3 saved: fig3_intersectional.png")

# =============================================================================
# FIGURE 4: FPR Disparity Summary
# =============================================================================
fig4, ax4 = plt.subplots(figsize=(10, 5))

x = np.arange(len(models))
width = 0.35

bars_maj = ax4.bar(x - width/2, fpr_maj_eth, width, label='Majority', color=COLORS['secondary'], edgecolor='white')
bars_min = ax4.bar(x + width/2, fpr_min_eth, width, label='Minority', color=COLORS['accent'], edgecolor='white')

ax4.set_ylabel('False Positive Rate')
ax4.set_title('Figure 4: False Positive Rate Disparity by Ethnicity', fontsize=12, fontweight='bold')
ax4.set_xticks(x)
ax4.set_xticklabels(models_short)
ax4.set_ylim(0, 0.50)
ax4.legend()

# Add value labels
for bar in bars_maj:
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
             f'{height:.3f}', ha='center', va='bottom', fontsize=8)
for bar in bars_min:
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
             f'{height:.3f}', ha='center', va='bottom', fontsize=8)

# Add annotation for disparity
for i in range(4):
    gap = fpr_min_eth[i] - fpr_maj_eth[i]
    ax4.annotate(f'Δ={gap:.3f}', xy=(i, fpr_min_eth[i] + 0.02), 
                fontsize=7, ha='center', color=COLORS['primary'], fontweight='bold')

plt.tight_layout()
fig4.savefig(f'{OUTPUT_DIR}/fig4_fpr_disparity.png', dpi=300, bbox_inches='tight')
plt.close(fig4)
print("✓ Figure 4 saved: fig4_fpr_disparity.png")

print(f"\n✅ All 4 figures generated in {OUTPUT_DIR}/")
print("Files:")
for f in sorted(os.listdir(OUTPUT_DIR)):
    if f.endswith('.png'):
        size = os.path.getsize(os.path.join(OUTPUT_DIR, f))
        print(f"  {f} ({size/1024:.1f} KB)")
