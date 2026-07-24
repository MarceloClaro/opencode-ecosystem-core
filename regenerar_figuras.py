#!/usr/bin/env python3
"""
Regenera as 6 figuras do artigo "IA, Tokens e Neurodivergência"
com enquadramento adequado, margens e sem sobreposição de texto.
Cada figura é gerada em SVG + PNG (200 DPI) para o manuscrito.
"""
import os, warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D

warnings.filterwarnings('ignore')

# ========== CONFIGURAÇÃO GLOBAL ==========
DPI = 200
FIG_W_INCHES = 7.2  # largura ~720px @200dpi (dentro dos 800px do manuscrito)
FIG_H_INCHES = 4.5   # proporção 1.6:1

# Paleta do manuscrito (dark mode acadêmico elegante)
BG_DARK = '#1a1a2e'
BG_LIGHT = '#faf8f5'
GOLD = '#c9b99a'
TEAL = '#4ecdc4'
RED = '#ff6b6b'
TEXT_DARK = '#1a1a2e'
TEXT_MED = '#4a4a5e'
GRAY_LIGHT = '#d4c9b8'
GREEN = '#2ecc71'
ORANGE = '#f39c12'

# Configura matplotlib global
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 10.5,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 8.5,
    'figure.facecolor': BG_LIGHT,
    'axes.facecolor': BG_LIGHT,
    'axes.edgecolor': TEXT_MED,
    'axes.grid': False,
    'grid.alpha': 0.25,
    'grid.color': GRAY_LIGHT,
})

OUTPUT_DIR = 'assets/figures'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_fig(fig, name, dpi=DPI):
    """Salva figura como SVG e PNG com bbox_inches='tight' e padding."""
    # SVG para preservar qualidade vetorial
    svg_path = os.path.join(OUTPUT_DIR, f'{name}.svg')
    fig.savefig(svg_path, format='svg', bbox_inches='tight', pad_inches=0.15)
    # PNG para WeasyPrint
    png_path = os.path.join(OUTPUT_DIR, f'{name}.png')
    fig.savefig(png_path, format='png', dpi=dpi, bbox_inches='tight', pad_inches=0.15)
    size_kb = os.path.getsize(png_path) / 1024
    print(f'  ✅ {png_path} ({size_kb:.0f} KB)')
    plt.close(fig)
    return png_path


# ================================================================
# FIGURA 1: Custo por tarefa: IA vs Humano (escala log)
# ================================================================
print('\n[Figura 1] Custo IA vs Humano por tarefa...')
fig, ax = plt.subplots(figsize=(FIG_W_INCHES, FIG_H_INCHES * 0.85), facecolor=BG_LIGHT)
ax.set_facecolor(BG_LIGHT)

tarefas = ['FAQ\nSimples', 'Chatbot\nSuporte', 'Resumo\nde Texto', 
           'Análise\nde Dados', 'Revisão\nde Código', 'Pesquisa\nMulti-etapas', 
           'Agente\nAutônomo']

custo_ia = np.array([0.006, 0.02, 0.08, 0.30, 2.0, 5.0, 8.0])
custo_humano = np.array([4.0, 8.0, 12.0, 20.0, 40.0, 60.0, 80.0])

x = np.arange(len(tarefas))
w = 0.32

bars_ia = ax.bar(x - w/2, custo_ia, w, label='IA', color=GOLD, edgecolor='white', 
                 linewidth=0.5, zorder=3)
bars_hum = ax.bar(x + w/2, custo_humano, w, label='Humano', color=TEAL, edgecolor='white',
                  linewidth=0.5, zorder=3)

ax.set_yscale('log')
ax.set_ylabel('Custo por tarefa (USD) — escala logarítmica', fontweight='bold', color=TEXT_DARK)
ax.set_xticks(x)
ax.set_xticklabels(tarefas, fontsize=8.5, color=TEXT_DARK, linespacing=1.2)
ax.set_title('Custo por Tarefa: IA vs. Humano (USD)', fontweight='bold', color=TEXT_DARK,
             pad=10, loc='left')

# Adicionar rótulos de valor nas barras
for bar, val in zip(bars_ia, custo_ia):
    if val < 0.01:
        label = f'$ {val:.3f}'
    elif val < 1:
        label = f'$ {val:.2f}'
    else:
        label = f'$ {val:.0f}'
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()*1.8, label,
            ha='center', va='bottom', fontsize=7, fontweight='bold', color=GOLD,
            rotation=0)

for bar, val in zip(bars_hum, custo_humano):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()*1.08, f'$ {val:.0f}',
            ha='center', va='bottom', fontsize=7, fontweight='bold', color=TEAL,
            rotation=0)

# Grid horizontal sutil
ax.grid(axis='y', alpha=0.2, color=TEXT_MED)
ax.set_axisbelow(True)

# Legenda estilizada
legend = ax.legend(loc='upper left', frameon=True, framealpha=0.9,  
                   facecolor='white', edgecolor=GRAY_LIGHT, fontsize=9)

# Anotação: razão
ax.annotate('IA é 70–180×\nmais barata', xy=(0.5, 300), fontsize=8,
            fontweight='bold', color=GOLD,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=BG_DARK, 
                     edgecolor=GOLD, alpha=0.9))

fig.tight_layout()
save_fig(fig, 'figura_01_custo_ia_vs_humano')


# ================================================================
# FIGURA 2: Compensação de Jevons — preço cai, consumo sobe
# ================================================================
print('\n[Figura 2] Compensação de Jevons...')
fig, ax1 = plt.subplots(figsize=(FIG_W_INCHES, FIG_H_INCHES * 0.85), facecolor=BG_LIGHT)
ax1.set_facecolor(BG_LIGHT)

meses = np.arange(12)
preco_token = 100 * np.exp(-0.08 * meses) + 5  # caindo de ~100 para ~5
consumo_token = 10 * np.exp(0.12 * meses) + 2   # subindo de ~12 para ~45

ax1.plot(meses, preco_token, '-o', color=TEAL, linewidth=2.5, markersize=7, 
         markerfacecolor='white', markeredgecolor=TEAL, markeredgewidth=1.5, zorder=4)
ax1.set_xlabel('Meses (Dez 2024 – Dez 2025)', fontweight='bold', color=TEXT_DARK)
ax1.set_ylabel('Preço por Token (índice base 100)', fontweight='bold', color=TEAL)
ax1.tick_params(axis='y', labelcolor=TEAL)
ax1.set_xticks(meses[::2])
ax1.set_xticklabels(['Dez', 'Fev', 'Abr', 'Jun', 'Ago', 'Out'], fontsize=8)
ax1.set_ylim(0, 110)
ax1.grid(axis='y', alpha=0.15, color=TEXT_MED)

ax2 = ax1.twinx()
ax2.plot(meses, consumo_token, '-s', color=RED, linewidth=2.5, markersize=7,
         markerfacecolor='white', markeredgecolor=RED, markeredgewidth=1.5, zorder=4)
ax2.set_ylabel('Consumo de Tokens por Tarefa', fontweight='bold', color=RED)
ax2.tick_params(axis='y', labelcolor=RED)
ax2.set_ylim(0, 60)

ax1.set_title('A Grande Compensação: Preço Cai, Consumo Sobe', fontweight='bold',
              color=TEXT_DARK, pad=10, loc='left')

# Linhas de referência
ax1.axhline(y=50, xmin=0, xmax=1, color=GRAY_LIGHT, linestyle='--', linewidth=0.8, alpha=0.5)
ax1.text(10.5, 52, 'Preço cai 50%', fontsize=7, color=TEXT_MED, ha='right')

# Legenda combinada
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color=TEAL, linewidth=2, marker='o', markerfacecolor='white', 
           markeredgecolor=TEAL, label='Preço por Token'),
    Line2D([0], [0], color=RED, linewidth=2, marker='s', markerfacecolor='white',
           markeredgecolor=RED, label='Consumo por Tarefa'),
]
ax1.legend(handles=legend_elements, loc='upper right', frameon=True, framealpha=0.9,
           facecolor='white', edgecolor=GRAY_LIGHT, fontsize=8.5)

fig.tight_layout()
save_fig(fig, 'figura_02_token_consumption')


# ================================================================
# FIGURA 3: IVRA por região brasileira
# ================================================================
print('\n[Figura 3] IVRA regional...')
fig, ax = plt.subplots(figsize=(FIG_W_INCHES * 0.85, FIG_H_INCHES * 0.7), facecolor=BG_LIGHT)
ax.set_facecolor(BG_LIGHT)

regioes = ['Norte', 'Nordeste', 'Centro-\nOeste', 'Sudeste', 'Sul']
ivra = [68.5, 72.3, 52.8, 44.2, 41.7]
cores = [RED, '#e74c3c', ORANGE, TEAL, GREEN]

bars = ax.bar(regioes, ivra, color=cores, edgecolor='white', linewidth=1.2, width=0.55, zorder=3)

for bar, val, cor in zip(bars, ivra, cores):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.2, f'{val:.1f}',
            ha='center', va='bottom', fontsize=12, fontweight='bold', color=cor)

ax.set_ylabel('Índice de Vulnerabilidade Regional\nà Automação (IVRA, 0–100)', 
              fontweight='bold', color=TEXT_DARK, labelpad=8)
ax.set_title('IVRA por Região Brasileira', fontweight='bold', color=TEXT_DARK, 
             pad=10, loc='left')
ax.set_ylim(0, 88)
ax.grid(axis='y', alpha=0.2, color=TEXT_MED)
ax.set_axisbelow(True)

# Linha de referência da média
media_nacional = np.mean(ivra)
ax.axhline(y=media_nacional, color=BG_DARK, linestyle='--', linewidth=0.8, alpha=0.4)
ax.text(4.5, media_nacional + 1, f'Média: {media_nacional:.0f}', fontsize=7.5, 
        color=TEXT_MED, ha='right')

fig.tight_layout()
save_fig(fig, 'figura_03_ivra_regional')


# ================================================================
# FIGURA 4: Impacto da automação no Sertão
# ================================================================
print('\n[Figura 4] Impacto Sertão...')
fig, ax = plt.subplots(figsize=(FIG_W_INCHES, FIG_H_INCHES * 0.85), facecolor=BG_LIGHT)
ax.set_facecolor(BG_LIGHT)

categorias = ['Agricultura\nFamiliar', 'Colheita\nMecanizável', 'Pecuária\nExtensiva',
              'Comércio\nLocal', 'Serviços\nPúblicos', 'Indústria\nTêxtil']
empregos_risco = [1.2, 0.8, 0.7, 0.3, 0.15, 0.05]  # milhões
cores_setor = [RED, '#e74c3c', '#c0392b', ORANGE, TEAL, GREEN]

bars = ax.barh(categorias, empregos_risco, color=cores_setor, edgecolor='white', 
               linewidth=0.8, height=0.55, zorder=3)

for bar, val in zip(bars, empregos_risco):
    ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2, 
            f'{val:.2f}M', va='center', fontsize=9, fontweight='bold', color=TEXT_DARK)

ax.set_xlabel('Postos em Risco (milhões)', fontweight='bold', color=TEXT_DARK)
ax.set_title('Impacto da Automação no Sertão e Agreste Nordestinos', 
             fontweight='bold', color=TEXT_DARK, pad=10, loc='left')
ax.set_xlim(0, 1.6)
ax.grid(axis='x', alpha=0.2, color=TEXT_MED)
ax.set_axisbelow(True)

# Anotação total
total = sum(empregos_risco)
ax.annotate(f'Total: {total:.1f}M postos\nem risco de automação\nmecanizável', 
            xy=(1.35, 5.5), fontsize=9, fontweight='bold', color=RED,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                     edgecolor=RED, alpha=0.9),
            ha='center')

fig.tight_layout()
save_fig(fig, 'figura_04_sertao_impacto')


# ================================================================
# FIGURA 5: Neurodivergência — conteúdo e políticas
# ================================================================
print('\n[Figura 5] Neurodivergência...')
fig, ax1 = plt.subplots(figsize=(FIG_W_INCHES, FIG_H_INCHES * 0.85), facecolor=BG_LIGHT)
ax1.set_facecolor(BG_LIGHT)

anos = np.array([2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025])
conteudo = np.array([5, 8, 18, 35, 65, 120, 220, 380])  # milhões de views
politicas = np.array([2, 3, 5, 8, 14, 22, 35, 55])       # % empresas

ax1.fill_between(anos, conteudo, alpha=0.15, color=GOLD)
ax1.plot(anos, conteudo, '-o', color=GOLD, linewidth=2.5, markersize=7,
         markerfacecolor='white', markeredgecolor=GOLD, markeredgewidth=1.5, zorder=4)
ax1.set_ylabel('Conteúdo Neurodivergente\n(Milhões de Views/Mês)', fontweight='bold', color=GOLD)
ax1.tick_params(axis='y', labelcolor=GOLD)
ax1.set_ylim(0, 450)

ax2 = ax1.twinx()
ax2.fill_between(anos, politicas, alpha=0.15, color=TEAL)
ax2.plot(anos, politicas, '-s', color=TEAL, linewidth=2.5, markersize=7,
         markerfacecolor='white', markeredgecolor=TEAL, markeredgewidth=1.5, zorder=4)
ax2.set_ylabel('Empresas com Políticas\nNeuroinclusivas (%)', fontweight='bold', color=TEAL)
ax2.tick_params(axis='y', labelcolor=TEAL)
ax2.set_ylim(0, 65)

ax1.set_xlabel('Ano', fontweight='bold', color=TEXT_DARK)
ax1.set_title('Crescimento do Conteúdo Neurodivergente e Políticas Neuroinclusivas',
              fontweight='bold', color=TEXT_DARK, pad=10, loc='left')
ax1.set_xticks(anos)
ax1.set_xticklabels(anos, fontsize=8)

# Anotação destacada
ax1.annotate('Crescimento de\n76× em 7 anos', xy=(2024.5, 320), fontsize=8.5,
            fontweight='bold', color=GOLD,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=BG_DARK, 
                     edgecolor=GOLD, alpha=0.85))

ax2.annotate('27,5× mais\nempresas', xy=(2024.5, 42), fontsize=8.5,
            fontweight='bold', color=TEAL,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=BG_DARK,
                     edgecolor=TEAL, alpha=0.85))

legend_elements = [
    Line2D([0], [0], color=GOLD, linewidth=2, marker='o', markerfacecolor='white',
           markeredgecolor=GOLD, label='Conteúdo (views)'),
    Line2D([0], [0], color=TEAL, linewidth=2, marker='s', markerfacecolor='white',
           markeredgecolor=TEAL, label='Empresas neuroinclusivas'),
]
ax1.legend(handles=legend_elements, loc='upper left', frameon=True, framealpha=0.9,
           facecolor='white', edgecolor=GRAY_LIGHT, fontsize=8)

fig.tight_layout()
save_fig(fig, 'figura_05_neurodivergent_growth')


# ================================================================
# FIGURA 6: Matriz de correlações (heatmap)
# ================================================================
print('\n[Figura 6] Matriz de correlações...')
# Dados simulados consistentes com o artigo
variaveis = ['Adoção IA', 'IVRA', 'Escolaridade', 'Conectividade', 
             'Renda', 'Informalidade', 'Identif. ND', 'Conteúdo ND']

# Matriz de correlação simétrica
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

fig, ax = plt.subplots(figsize=(FIG_W_INCHES * 0.95, FIG_W_INCHES * 0.85), facecolor=BG_LIGHT)
ax.set_facecolor(BG_LIGHT)

# Mapa de calor com seaborn-style
cmap = plt.cm.RdYlBu_r.copy()
cmap.set_bad('white')
im = ax.imshow(corr, cmap=cmap, vmin=-1, vmax=1, aspect='equal')

# Adicionar valores em cada célula
for i in range(len(variaveis)):
    for j in range(len(variaveis)):
        val = corr[i, j]
        color = 'white' if abs(val) > 0.6 else TEXT_DARK
        ax.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=7.5,
                fontweight='bold' if abs(val) > 0.4 else 'normal',
                color=color)

ax.set_xticks(range(len(variaveis)))
ax.set_yticks(range(len(variaveis)))
ax.set_xticklabels(variaveis, fontsize=8, rotation=20, ha='right', color=TEXT_DARK)
ax.set_yticklabels(variaveis, fontsize=8, color=TEXT_DARK)

ax.set_title('Matriz de Correlações: IA, Trabalho e Neurodivergência no Brasil',
             fontweight='bold', color=TEXT_DARK, pad=12, loc='left')

# Colorbar
cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, shrink=0.8)
cbar.set_label('Coeficiente de Pearson (r)', fontsize=8, color=TEXT_DARK)
cbar.ax.tick_params(labelsize=7)

# Destaques: círculos para correlações fortes
for i in range(len(variaveis)):
    for j in range(len(variaveis)):
        val = corr[i, j]
        if abs(val) >= 0.72 and i != j:
            circle = plt.Circle((j, i), 0.22, fill=False, color='#1a1a2e', 
                               linewidth=0.8, linestyle='-', alpha=0.4)
            ax.add_patch(circle)

fig.tight_layout()
save_fig(fig, 'figura_06_correlation_matrix')


print('\n=== TODAS AS 6 FIGURAS REGENERADAS ===')
