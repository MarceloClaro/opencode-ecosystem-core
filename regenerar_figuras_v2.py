#!/usr/bin/env python3
"""
Regenera as 6 figuras com espacamento generoso, sem sobreposicao.
v2: usa constrained_layout, dimensoes maiores, padding extra,
    anotacoes com fundo, labels mais curtas, fontes ajustadas.
"""
import os, warnings, textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D as L2

warnings.filterwarnings('ignore')

DPI = 200
# Dimensoes MAIORES para espacamento
FIG_W = 9.0
FIG_H = 5.5

# Paleta
BG = '#faf8f5'
GOLD = '#c9b99a'
TEAL = '#4ecdc4'
RED = '#ff6b6b'
DARK = '#1a1a2e'
MED = '#4a4a5e'
GRAY = '#d4c9b8'
GREEN = '#2ecc71'
ORANGE = '#f39c12'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11.5,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 9.5,
    'figure.facecolor': BG,
    'axes.facecolor': BG,
    'axes.edgecolor': MED,
    'axes.grid': False,
})

OUT = 'assets/figures'
os.makedirs(OUT, exist_ok=True)

def save_fig(fig, name):
    fig.savefig(os.path.join(OUT, f'{name}.svg'), format='svg', bbox_inches='tight', pad_inches=0.25)
    fig.savefig(os.path.join(OUT, f'{name}.png'), format='png', dpi=DPI, bbox_inches='tight', pad_inches=0.25)
    kb = os.path.getsize(os.path.join(OUT, f'{name}.png')) / 1024
    print(f'  ✅ {name}.png ({kb:.0f} KB)')
    plt.close(fig)

# ===== FIGURA 1: Custo IA vs Humano (log scale) =====
print('\n[Figura 1] Custo IA vs Humano...')
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H * 0.85), constrained_layout=True)
ax.set_facecolor(BG)

tarefas = ['FAQ\nSimples', 'Chatbot\nSuporte', 'Resumo\nde Texto',
           'Análise\nde Dados', 'Revisão\nde Código', 'Pesquisa\nMulti-etapas', 'Agente\nAutônomo\nComplexo']

custo_ia = np.array([0.006, 0.02, 0.08, 0.30, 2.0, 5.0, 8.0])
custo_humano = np.array([4.0, 8.0, 12.0, 20.0, 40.0, 60.0, 80.0])

x = np.arange(len(tarefas))
w = 0.30

b1 = ax.bar(x - w/2, custo_ia, w, label='IA', color=GOLD, edgecolor='white', linewidth=0.6, zorder=3)
b2 = ax.bar(x + w/2, custo_humano, w, label='Humano', color=TEAL, edgecolor='white', linewidth=0.6, zorder=3)

ax.set_yscale('log')
ax.set_ylabel('Custo por Tarefa (USD) — escala log', fontweight='bold', color=DARK, labelpad=8)
ax.set_xticks(x)
ax.set_xticklabels(tarefas, fontsize=9, color=DARK, linespacing=1.3)
ax.set_title('Custo por Tarefa: IA vs. Humano (USD, Q1 2026)', fontweight='bold', color=DARK, pad=14, loc='left', fontsize=13)
ax.grid(axis='y', alpha=0.15, color=MED)
ax.set_axisbelow(True)
ax.set_ylim(0.003, 200)

# Rotulos com offset vertical maior para evitar overlap
for bar, val in zip(b1, custo_ia):
    offset = 2.0 if val < 0.01 else 1.6
    label = f'$ {val:.3f}' if val < 0.01 else f'$ {val:.2f}' if val < 1 else f'$ {val:.0f}'
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * offset, label,
            ha='center', va='bottom', fontsize=7.5, fontweight='bold', color=GOLD, rotation=0)

for bar, val in zip(b2, custo_humano):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.12, f'$ {val:.0f}',
            ha='center', va='bottom', fontsize=7.5, fontweight='bold', color=TEAL, rotation=0)

# Legenda no canto superior direito (sem sobrepor)
ax.legend(loc='upper left', frameon=True, framealpha=0.92, facecolor='white', edgecolor=GRAY, fontsize=9.5)

# Anotacao destacada com fundo
ax.annotate('IA é 70–180×\nmais barata\nque humano', xy=(1, 150),
            fontsize=9, fontweight='bold', color=GOLD,
            bbox=dict(boxstyle='round,pad=0.35', facecolor=DARK, edgecolor=GOLD, alpha=0.9),
            ha='center')

save_fig(fig, 'figura_01_custo_ia_vs_humano')

# ===== FIGURA 2: Compensacao de Jevons =====
print('\n[Figura 2] Compensacao de Jevons...')
fig, ax1 = plt.subplots(figsize=(FIG_W, FIG_H * 0.85), constrained_layout=True)
ax1.set_facecolor(BG)

meses = np.arange(12)
preco = 100 * np.exp(-0.08 * meses) + 5
consumo = 10 * np.exp(0.12 * meses) + 2

ax1.plot(meses, preco, '-o', color=TEAL, linewidth=3, markersize=8,
         markerfacecolor='white', markeredgecolor=TEAL, markeredgewidth=1.8, zorder=5)
ax1.set_ylabel('Preço por Token (índice base 100)', fontweight='bold', color=TEAL, labelpad=8)
ax1.tick_params(axis='y', labelcolor=TEAL, labelsize=10)
ax1.set_xticks(meses[::2])
ax1.set_xticklabels(['Dez\n2024', 'Fev\n2025', 'Abr', 'Jun', 'Ago', 'Out\n2025'], fontsize=9, linespacing=1.3)
ax1.set_ylim(0, 115)
ax1.grid(axis='y', alpha=0.12, color=MED)

ax2 = ax1.twinx()
ax2.plot(meses, consumo, '-s', color=RED, linewidth=3, markersize=8,
         markerfacecolor='white', markeredgecolor=RED, markeredgewidth=1.8, zorder=5)
ax2.set_ylabel('Consumo de Tokens\npor Tarefa', fontweight='bold', color=RED, labelpad=8)
ax2.tick_params(axis='y', labelcolor=RED, labelsize=10)
ax2.set_ylim(0, 65)

ax1.set_xlabel('Período (Dez 2024 – Dez 2025)', fontweight='bold', color=DARK, labelpad=6)
ax1.set_title('A Grande Compensação (Jevons): Preço Cai, Consumo Sobe', fontweight='bold', color=DARK, pad=14, loc='left', fontsize=13)

# Linhas de referencia com labels mais afastadas
ax1.axhline(y=50, color=GRAY, linestyle='--', linewidth=0.8, alpha=0.4)
ax1.text(10.8, 53, 'Preço cai 50%', fontsize=8, color=MED, ha='right', va='bottom')

ax1.axhline(y=preco[0], color=TEAL, linestyle=':', linewidth=0.6, alpha=0.3)
ax1.text(10.8, preco[0]+2, f'Base: {preco[0]:.0f}', fontsize=7.5, color=TEAL, ha='right')

# Legenda
leg = [
    L2([0], [0], color=TEAL, linewidth=2.5, marker='o', markerfacecolor='white', markeredgecolor=TEAL, label='Preço por Token ↓'),
    L2([0], [0], color=RED, linewidth=2.5, marker='s', markerfacecolor='white', markeredgecolor=RED, label='Consumo por Tarefa ↑'),
]
ax1.legend(handles=leg, loc='upper right', frameon=True, framealpha=0.92, facecolor='white', edgecolor=GRAY, fontsize=9)

save_fig(fig, 'figura_02_token_consumption')

# ===== FIGURA 3: IVRA Regional (barras) =====
print('\n[Figura 3] IVRA Regional...')
fig, ax = plt.subplots(figsize=(FIG_W * 0.75, FIG_H * 0.65), constrained_layout=True)
ax.set_facecolor(BG)

regioes = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
ivra = [68.5, 72.3, 52.8, 44.2, 41.7]
cores = [RED, '#e74c3c', ORANGE, TEAL, GREEN]

bars = ax.bar(regioes, ivra, color=cores, edgecolor='white', linewidth=1.2, width=0.55, zorder=3)

for bar, val, cor in zip(bars, ivra, cores):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.8, f'{val:.1f}',
            ha='center', va='bottom', fontsize=14, fontweight='bold', color=cor)

ax.set_ylabel('Índice de Vulnerabilidade\nRegional à Automação (IVRA)', fontweight='bold', color=DARK, labelpad=8)
ax.set_title('IVRA por Região Brasileira (0–100)', fontweight='bold', color=DARK, pad=14, loc='left', fontsize=13)
ax.set_ylim(0, 90)
ax.grid(axis='y', alpha=0.15, color=MED)
ax.set_axisbelow(True)

media = np.mean(ivra)
ax.axhline(y=media, color=DARK, linestyle='--', linewidth=0.8, alpha=0.35)
ax.text(4.5, media + 1.5, f'Média Brasil: {media:.0f}', fontsize=8.5, color=MED, ha='right', va='bottom')

# Legenda explicativa no canto
ax.text(0.02, 0.98, 'Maior = mais vulnerável', transform=ax.transAxes,
        fontsize=8, color=MED, va='top', ha='left',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=GRAY, alpha=0.85))

save_fig(fig, 'figura_03_ivra_regional')

# ===== FIGURA 4: Impacto Sertao (horizontal bars) =====
print('\n[Figura 4] Impacto Sertao...')
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H * 0.8), constrained_layout=True)
ax.set_facecolor(BG)

cats = ['Agricultura Familiar', 'Colheita Mecanizável', 'Pecuária Extensiva',
        'Comércio Local', 'Serviços Públicos', 'Indústria Têxtil']
risco = [1.2, 0.8, 0.7, 0.3, 0.15, 0.05]
cores_setor = [RED, '#e74c3c', '#c0392b', ORANGE, TEAL, GREEN]

bars = ax.barh(cats, risco, color=cores_setor, edgecolor='white', linewidth=0.8, height=0.55, zorder=3)

for bar, val in zip(bars, risco):
    ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
            f'{val:.2f} milhão', va='center', fontsize=10, fontweight='bold', color=DARK)

ax.set_xlabel('Postos em Risco (milhões)', fontweight='bold', color=DARK, labelpad=6)
ax.set_title('Impacto da Automação no Sertão e Agreste Nordestinos',
             fontweight='bold', color=DARK, pad=14, loc='left', fontsize=13)
ax.set_xlim(0, 1.7)
ax.grid(axis='x', alpha=0.12, color=MED)
ax.set_axisbelow(True)

# Anotacao total - deslocada para nao sobrepor
total = sum(risco)
ax.annotate(f'Total: {total:.1f}M postos\nem risco de automação\nmecanizável',
            xy=(1.50, 5.5), fontsize=10, fontweight='bold', color=RED,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor=RED, alpha=0.92),
            ha='center', va='center')

# Fonte no canto
ax.text(0.98, 0.02, 'Fonte: IBGIA WP-2026-013 [8], PNAD 2024 [50]',
        transform=ax.transAxes, fontsize=7, color=MED, ha='right', va='bottom',
        style='italic')

save_fig(fig, 'figura_04_sertao_impacto')

# ===== FIGURA 5: Neurodivergencia (dual-axis com fill) =====
print('\n[Figura 5] Neurodivergencia...')
fig, ax1 = plt.subplots(figsize=(FIG_W, FIG_H * 0.85), constrained_layout=True)
ax1.set_facecolor(BG)

anos = np.array([2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025])
conteudo = np.array([5, 8, 18, 35, 65, 120, 220, 380])
politicas = np.array([2, 3, 5, 8, 14, 22, 35, 55])

ax1.fill_between(anos, conteudo, alpha=0.1, color=GOLD)
ax1.plot(anos, conteudo, '-o', color=GOLD, linewidth=3, markersize=8,
         markerfacecolor='white', markeredgecolor=GOLD, markeredgewidth=1.8, zorder=5)
ax1.set_ylabel('Conteúdo Neurodivergente\n(Milhões de Views/Mês)', fontweight='bold', color=GOLD, labelpad=8)
ax1.tick_params(axis='y', labelcolor=GOLD, labelsize=10)
ax1.set_ylim(0, 480)

ax2 = ax1.twinx()
ax2.fill_between(anos, politicas, alpha=0.1, color=TEAL)
ax2.plot(anos, politicas, '-s', color=TEAL, linewidth=3, markersize=8,
         markerfacecolor='white', markeredgecolor=TEAL, markeredgewidth=1.8, zorder=5)
ax2.set_ylabel('Empresas com Políticas\nNeuroinclusivas (%)', fontweight='bold', color=TEAL, labelpad=8)
ax2.tick_params(axis='y', labelcolor=TEAL, labelsize=10)
ax2.set_ylim(0, 68)

ax1.set_xlabel('Ano', fontweight='bold', color=DARK, labelpad=6)
ax1.set_xticks(anos)
ax1.set_xticklabels(anos, fontsize=9)
ax1.set_title('Crescimento do Conteúdo Neurodivergente e das Políticas Neuroinclusivas',
              fontweight='bold', color=DARK, pad=14, loc='left', fontsize=13)

# Anotacoes com fundo - posicionadas mais afastadas
ax1.annotate('Conteúdo cresceu\n76× em 7 anos', xy=(2024, 400), fontsize=9.5,
            fontweight='bold', color=GOLD, ha='center',
            bbox=dict(boxstyle='round,pad=0.35', facecolor=DARK, edgecolor=GOLD, alpha=0.88))

ax2.annotate('27,5× mais\nempresas', xy=(2024, 50), fontsize=9.5,
            fontweight='bold', color=TEAL, ha='center',
            bbox=dict(boxstyle='round,pad=0.35', facecolor=DARK, edgecolor=TEAL, alpha=0.88))

# Legenda
leg = [
    L2([0], [0], color=GOLD, linewidth=2.5, marker='o', markerfacecolor='white', markeredgecolor=GOLD, label='Conteúdo (views/mês)'),
    L2([0], [0], color=TEAL, linewidth=2.5, marker='s', markerfacecolor='white', markeredgecolor=TEAL, label='Empresas neuroinclusivas'),
]
ax1.legend(handles=leg, loc='upper left', frameon=True, framealpha=0.92, facecolor='white', edgecolor=GRAY, fontsize=9)

save_fig(fig, 'figura_05_neurodivergent_growth')

# ===== FIGURA 6: Matriz de Correlacao (heatmap) =====
print('\n[Figura 6] Matriz de Correlacao...')

# Variaveis com nomes MAIS CURTOS para caber no heatmap
var_short = ['Adoção\nIA', 'IVRA', 'Escolarid.', 'Conectiv.',
             'Renda', 'Informal.', 'Identif.\nND', 'Conteúdo\nND']

var_full = ['Adoção de IA', 'IVRA', 'Escolaridade', 'Conectividade',
            'Renda', 'Informalidade', 'Identif. Neurodiv.', 'Conteúdo Neurodiv.']

corr = np.array([
    [1.00, -0.72,  0.58,  0.63,  0.61, -0.55,  0.42,  0.38],
    [-0.72, 1.00, -0.65, -0.71, -0.68,  0.74, -0.35, -0.30],
    [0.58, -0.65,  1.00,  0.82,  0.79, -0.62,  0.48,  0.41],
    [0.63, -0.71,  0.82,  1.00,  0.85, -0.70,  0.38,  0.35],
    [0.61, -0.68,  0.79,  0.85,  1.00, -0.76,  0.32,  0.28],
    [-0.55, 0.74, -0.62, -0.70, -0.76,  1.00, -0.25, -0.22],
    [0.42, -0.35,  0.48,  0.38,  0.32, -0.25,  1.00,  0.88],
    [0.38, -0.30,  0.41,  0.35,  0.28, -0.22,  0.88,  1.00],
])

fig, ax = plt.subplots(figsize=(FIG_W, FIG_W * 0.85), constrained_layout=True)
ax.set_facecolor(BG)

cmap = plt.cm.RdYlBu_r.copy()
cmap.set_bad('white')
im = ax.imshow(corr, cmap=cmap, vmin=-1, vmax=1, aspect='equal')

# Valores nas celulas com cor adaptativa
for i in range(len(var_short)):
    for j in range(len(var_short)):
        val = corr[i, j]
        bg = abs(val)
        text_color = 'white' if bg > 0.6 else DARK
        ax.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=8.5,
                fontweight='bold' if bg > 0.4 else 'normal', color=text_color)

ax.set_xticks(range(len(var_short)))
ax.set_yticks(range(len(var_short)))
ax.set_xticklabels(var_short, fontsize=8.5, rotation=25, ha='right', color=DARK)
ax.set_yticklabels(var_short, fontsize=8.5, color=DARK)

ax.set_title('Matriz de Correlações: IA, Trabalho e Neurodivergência no Brasil',
             fontweight='bold', color=DARK, pad=16, loc='left', fontsize=12)

# Colorbar mais fina
cbar = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.035, shrink=0.75)
cbar.set_label('Coeficiente de Pearson (r)', fontsize=9, color=DARK)
cbar.ax.tick_params(labelsize=8)

save_fig(fig, 'figura_06_correlation_matrix')

print('\n=== TODAS AS 6 FIGURAS REGENERADAS (v2) ===')
