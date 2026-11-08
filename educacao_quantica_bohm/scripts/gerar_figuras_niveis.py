#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera as seis ilustrações da trilha "nível 0 → PhD".

Cada figura é um mapa visual do que muda quando o leitor avança:
- N0: bit, qubit e medição sem matemática;
- N1: onda piloto e franjas (modelo didático);
- N2: Bell/CHSH e correlações;
- N3: circuito, vetor de estado e matriz densidade;
- N4: relaxação, coerência e ruído;
- N5: pipeline de pesquisa e replicação com incerteza.

As figuras são decorativas/científicas: não substituem os dados do livro.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

RAIZ = Path(__file__).resolve().parents[1]
FIG = RAIZ / "livro" / "figuras_geradas"
FIG.mkdir(parents=True, exist_ok=True)

FUNDO = "#05070B"
PAINEL = "#0B1220"
TEXTO = "#E8F0FF"
SUAVE = "#94A3B8"
CIANO = "#5EEAD4"
AMBAR = "#FBBF24"
ROXO = "#A78BFA"
CORAL = "#FB7185"
VERDE = "#34D399"

plt.rcParams.update({
    "figure.facecolor": FUNDO,
    "axes.facecolor": FUNDO,
    "savefig.facecolor": FUNDO,
    "text.color": TEXTO,
    "axes.labelcolor": TEXTO,
    "xtick.color": TEXTO,
    "ytick.color": TEXTO,
    "axes.edgecolor": "#22304A",
    "grid.color": "#1E293B",
    "font.family": "DejaVu Sans",
})


def salvar(fig: plt.Figure, nome: str) -> None:
    fig.savefig(FIG / f"{nome}.png", dpi=220, bbox_inches="tight", facecolor=FUNDO)
    plt.close(fig)
    print("  ✓", nome)


def caixa(ax, x, y, w, h, texto, cor, fs=10):
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        facecolor=PAINEL, edgecolor=cor, linewidth=1.6,
    ))
    ax.text(x, y, texto, ha="center", va="center", color=cor, fontsize=fs)


def seta(ax, x1, y1, x2, y2, cor=SUAVE):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12,
        color=cor, linewidth=1.2,
    ))


# ------------------------------------------------------------------ N0
def nivel0() -> None:
    fig, eixos = plt.subplots(1, 3, figsize=(13, 4.4))
    for ax in eixos:
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

    ax = eixos[0]
    ax.set_title("BIT · duas possibilidades", color=CIANO, fontsize=13, loc="left")
    for x, rot in ((0.3, "0"), (0.7, "1")):
        ax.add_patch(Rectangle((x - 0.11, 0.40), 0.22, 0.22, facecolor=PAINEL,
                               edgecolor=CIANO, linewidth=2))
        ax.text(x, 0.51, rot, ha="center", va="center", color=CIANO, fontsize=26)
    ax.text(0.5, 0.20, "uma diferença registrada", ha="center", color=SUAVE, fontsize=10)
    seta(ax, 0.44, 0.51, 0.56, 0.51, CIANO)

    ax = eixos[1]
    ax.set_title("QUBIT · duas amplitudes", color=AMBAR, fontsize=13, loc="left")
    ax.add_patch(Circle((0.5, 0.52), 0.26, facecolor="none", edgecolor=AMBAR, linewidth=2))
    ax.plot([0.5, 0.5], [0.26, 0.78], color="#334155", linewidth=1)
    ax.plot([0.24, 0.76], [0.52, 0.52], color="#334155", linewidth=1)
    ax.add_patch(FancyArrowPatch((0.5, 0.52), (0.64, 0.70), arrowstyle="-|>",
                                 mutation_scale=14, color=AMBAR, linewidth=2))
    ax.text(0.5, 0.84, "|0⟩", ha="center", color=SUAVE, fontsize=11)
    ax.text(0.5, 0.14, "|1⟩", ha="center", color=SUAVE, fontsize=11)
    ax.text(0.66, 0.50, "θ", color=AMBAR, fontsize=13)
    ax.text(0.5, 0.03, "P(0)=cos²(θ/2) · P(1)=sen²(θ/2)", ha="center",
            color=SUAVE, fontsize=9)

    ax = eixos[2]
    ax.set_title("MEDIÇÃO · uma resposta", color=VERDE, fontsize=13, loc="left")
    ax.bar([0.35, 0.65], [0.75, 0.25], width=0.18, color=[VERDE, CORAL])
    ax.set_ylim(0, 1)
    ax.set_xlim(0, 1)
    ax.set_xticks([0.35, 0.65])
    ax.set_xticklabels(["0", "1"], fontsize=12)
    ax.set_yticks([0, 0.5, 1])
    ax.set_ylabel("probabilidade")
    ax.text(0.5, 0.92, "o resultado é 0 ou 1", ha="center", color=SUAVE, fontsize=10)

    fig.suptitle("NÍVEL 0 · o mapa mínimo: bit, qubit, medição",
                 color=TEXTO, fontsize=16, fontweight="bold", x=0.02, ha="left")
    fig.text(0.02, -0.02, "Sem matemática: a pergunta é o que existe antes de medir e o que a medição entrega.",
             color=SUAVE, fontsize=9)
    fig.tight_layout()
    salvar(fig, "fig17_nivel0")


# ------------------------------------------------------------------ N1
def nivel1() -> None:
    fig, ax = plt.subplots(figsize=(12, 5.2))
    ax.set_xlim(-1.0, 1.0)
    ax.set_ylim(-0.8, 0.8)
    ax.axis("off")
    ax.set_title("NÍVEL 0b · onda piloto, duas fendas e franjas",
                 color=CIANO, fontsize=16, fontweight="bold", loc="left")

    # fonte
    ax.add_patch(Circle((-0.86, 0), 0.055, facecolor=AMBAR, edgecolor=AMBAR))
    ax.text(-0.86, -0.14, "fonte", ha="center", color=SUAVE, fontsize=9)

    # barreira com fendas
    ax.plot([-0.30, -0.30], [-0.70, -0.12], color=TEXTO, linewidth=4)
    ax.plot([-0.30, -0.30], [0.12, 0.70], color=TEXTO, linewidth=4)
    ax.text(-0.30, 0.76, "barreira", ha="center", color=SUAVE, fontsize=9)
    ax.text(-0.30, 0.0, "fendas", ha="center", color=AMBAR, fontsize=9, rotation=90)

    # trajetórias guiadas por fase
    rng = np.random.default_rng(7)
    for alvo in [-0.55, -0.38, -0.20, 0.02, 0.22, 0.40, 0.57]:
        fenda = -0.055 if rng.random() < 0.5 else 0.055
        x = np.linspace(-0.80, 0.80, 200)
        y = alvo * ((x + 0.80) / 1.60) ** 0.7
        y += 0.10 * np.sin(8 * np.pi * (x + 0.8)) * (1 - (x + 0.8) / 1.6)
        ax.plot(x, y, color=CIANO, alpha=0.55, linewidth=1.0)
        ax.plot([-0.30, -0.30], [0, fenda], color=CIANO, alpha=0.35, linewidth=1)

    # tela e franjas
    ax.plot([0.80, 0.80], [-0.70, 0.70], color=TEXTO, linewidth=4)
    ys = np.linspace(-0.70, 0.70, 400)
    intensidade = np.cos(9 * np.pi * ys) ** 2
    for y, i in zip(ys[::8], intensidade[::8]):
        ax.plot([0.80, 0.80 + 0.16 * i], [y, y], color=VERDE, linewidth=2, alpha=0.75)
    ax.text(0.92, 0.76, "tela", ha="center", color=SUAVE, fontsize=9)
    ax.text(0.93, 0.0, "franjas", ha="center", color=VERDE, fontsize=9, rotation=90)

    ax.text(0.0, -0.75,
            "Modelo didático: a fase guia trajetórias; a interferência aparece na tela. "
            "Não é uma solução completa da equação de Bohm.",
            ha="center", color=SUAVE, fontsize=9)
    fig.tight_layout()
    salvar(fig, "fig18_nivel1")


# ------------------------------------------------------------------ N2
def nivel2() -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8),
                                   gridspec_kw={"width_ratios": [1, 1.5]})

    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis("off")
    ax1.set_title("Bell · duas estações", color=AMBAR, fontsize=13, loc="left")
    caixa(ax1, 0.18, 0.50, 0.20, 0.16, "Alice", CIANO, 11)
    caixa(ax1, 0.82, 0.50, 0.20, 0.16, "Bob", CORAL, 11)
    ax1.add_patch(Circle((0.50, 0.50), 0.075, facecolor=PAINEL,
                         edgecolor=AMBAR, linewidth=2))
    ax1.text(0.50, 0.50, "φ", ha="center", va="center", color=AMBAR, fontsize=14)
    seta(ax1, 0.29, 0.50, 0.42, 0.50, AMBAR)
    seta(ax1, 0.58, 0.50, 0.71, 0.50, AMBAR)
    ax1.text(0.50, 0.31, "par emaranhado", ha="center", color=SUAVE, fontsize=9)
    ax1.text(0.18, 0.31, "ângulo a", ha="center", color=CIANO, fontsize=9)
    ax1.text(0.82, 0.31, "ângulo b", ha="center", color=CORAL, fontsize=9)
    ax1.text(0.50, 0.10, "medir nos dois lados e comparar", ha="center",
             color=SUAVE, fontsize=9)

    theta = np.linspace(0, 2 * np.pi, 400)
    ax2.plot(theta, np.cos(theta), color=CIANO, linewidth=2, label="E(θ)=cos θ")
    ax2.axhline(0, color=SUAVE, linewidth=0.8)
    ax2.axhline(0.7071, color=SUAVE, linewidth=1, linestyle=":")
    ax2.axhline(-0.7071, color=SUAVE, linewidth=1, linestyle=":")
    pontos = [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4]
    vals = [np.cos(p) for p in pontos]
    ax2.scatter(pontos, vals, color=AMBAR, zorder=5)
    for p, v in zip(pontos, vals):
        ax2.annotate(f"{v:+.3f}", (p, v), textcoords="offset points",
                     xytext=(5, 8), color=AMBAR, fontsize=8)
    ax2.set_xlim(0, 2 * np.pi)
    ax2.set_ylim(-1.15, 1.15)
    ax2.set_xticks([0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi])
    ax2.set_xticklabels(["0", "π/2", "π", "3π/2", "2π"])
    ax2.set_ylabel("correlação E")
    ax2.set_title("CHSH · quatro correlações, um S", color=AMBAR, fontsize=13, loc="left")
    ax2.grid(alpha=0.12)
    ax2.legend(frameon=False, labelcolor=TEXTO, fontsize=9, loc="lower left")

    fig.suptitle("NÍVEL 1 · correlação não é mensagem",
                 color=TEXTO, fontsize=16, fontweight="bold", x=0.02, ha="left")
    fig.tight_layout()
    salvar(fig, "fig19_nivel2")


# ------------------------------------------------------------------ N3
def nivel3() -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.0),
                                   gridspec_kw={"width_ratios": [1.2, 1]})

    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 6)
    ax1.axis("off")
    ax1.set_title("Circuito · portas e medição", color=ROXO, fontsize=13, loc="left")
    # linhas
    for y, rot in [(4.4, "q0"), (2.8, "q1")]:
        ax1.plot([1.0, 9.0], [y, y], color="#334155", linewidth=2)
        ax1.text(0.6, y, rot, color=SUAVE, fontsize=10, va="center")
    # H
    ax1.add_patch(Rectangle((2.2, 4.0), 0.8, 0.8, facecolor=PAINEL,
                            edgecolor=CIANO, linewidth=1.8))
    ax1.text(2.6, 4.4, "H", ha="center", va="center", color=CIANO, fontsize=13)
    # CNOT
    ax1.plot([4.6, 4.6], [2.8, 4.4], color=AMBAR, linewidth=1.8)
    ax1.add_patch(Circle((4.6, 4.4), 0.12, facecolor=AMBAR, edgecolor=AMBAR))
    ax1.add_patch(Circle((4.6, 2.8), 0.20, facecolor="none", edgecolor=AMBAR, linewidth=1.8))
    ax1.plot([4.4, 4.8], [2.8, 2.8], color=AMBAR, linewidth=1.8)
    ax1.plot([4.6, 4.6], [2.6, 3.0], color=AMBAR, linewidth=1.8)
    # medida
    for y in (4.4, 2.8):
        ax1.add_patch(Rectangle((6.6, y - 0.35), 0.9, 0.7, facecolor=PAINEL,
                                edgecolor=VERDE, linewidth=1.6))
        ax1.text(7.05, y, "M", ha="center", va="center", color=VERDE, fontsize=11)
    ax1.text(5.6, 1.7, "H → CNOT → medição", ha="center", color=SUAVE, fontsize=10)

    # density matrix of Bell state
    psi = np.array([1, 0, 0, 1]) / np.sqrt(2)
    rho = np.outer(psi, psi.conj()).real
    im = ax2.imshow(rho, cmap="magma", vmin=-0.1, vmax=0.6)
    ax2.set_xticks(range(4))
    ax2.set_yticks(range(4))
    ax2.set_xticklabels(["00", "01", "10", "11"])
    ax2.set_yticklabels(["00", "01", "10", "11"])
    ax2.set_title("Matriz densidade do estado de Bell", color=ROXO, fontsize=13, loc="left")
    for i in range(4):
        for j in range(4):
            ax2.text(j, i, f"{rho[i, j]:.2f}", ha="center", va="center",
                     color="white" if rho[i, j] > 0.3 else SUAVE, fontsize=9)
    fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)

    fig.suptitle("NÍVEL 1b · o estado também é uma matriz",
                 color=TEXTO, fontsize=16, fontweight="bold", x=0.02, ha="left")
    fig.tight_layout()
    salvar(fig, "fig20_nivel3")


# ------------------------------------------------------------------ N4
def nivel4() -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8))

    t = np.linspace(0, 5, 400)
    ax1.plot(t, np.exp(-t / 2.0), color=CIANO, linewidth=2, label="T1 · população")
    ax1.plot(t, np.exp(-t / 1.2), color=CORAL, linewidth=2, label="T2 · coerência")
    ax1.set_xlabel("tempo (unidades de T)")
    ax1.set_ylabel("sinal")
    ax1.set_ylim(0, 1.05)
    ax1.set_title("Relaxação e coerência", color=CORAL, fontsize=13, loc="left")
    ax1.grid(alpha=0.12)
    ax1.legend(frameon=False, labelcolor=TEXTO, fontsize=9)
    ax1.text(2.5, 0.55, "T2 ≤ 2T1", color=SUAVE, fontsize=10)

    ax2.set_xlim(-1.2, 1.2)
    ax2.set_ylim(-1.2, 1.2)
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.set_title("Vetor de Bloch perdendo comprimento", color=CORAL, fontsize=13, loc="left")
    ax2.add_patch(Circle((0, 0), 1.0, facecolor="none", edgecolor="#334155", linewidth=1.5))
    ax2.plot([-1.1, 1.1], [0, 0], color="#334155", linewidth=0.8)
    ax2.plot([0, 0], [-1.1, 1.1], color="#334155", linewidth=0.8)
    for escala, cor, rot in [(1.0, CIANO, "t=0"), (0.7, AMBAR, "t=T2"), (0.35, CORAL, "t=3T2")]:
        ax2.add_patch(FancyArrowPatch((0, 0), (0.75 * escala, 0.66 * escala),
                                      arrowstyle="-|>", mutation_scale=13,
                                      color=cor, linewidth=2))
        ax2.text(0.78 * escala, 0.70 * escala, rot, color=cor, fontsize=9)
    ax2.text(0, -1.15, "a pureza cai; o estado mistura", ha="center", color=SUAVE, fontsize=9)

    fig.suptitle("NÍVEL 2 · ruído tem tipo e tempo",
                 color=TEXTO, fontsize=16, fontweight="bold", x=0.02, ha="left")
    fig.tight_layout()
    salvar(fig, "fig21_nivel4")


# ------------------------------------------------------------------ N5
def nivel5() -> None:
    fig = plt.figure(figsize=(13, 5.2))
    ax = fig.add_axes([0.04, 0.40, 0.92, 0.46])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2)
    ax.axis("off")
    ax.set_title("Pipeline de pesquisa", color=VERDE, fontsize=13, loc="left")

    etapas = [
        ("Pergunta", 0.7), ("Circuito", 2.0), ("Transpilação", 3.4),
        ("Backend", 4.8), ("Counts", 6.2), ("Estatística", 7.6), ("Réplica", 9.0),
    ]
    for i, (rot, x) in enumerate(etapas):
        caixa(ax, x, 1.0, 1.0, 0.55, rot, CIANO if i < 4 else AMBAR, 9)
        if i < len(etapas) - 1:
            seta(ax, x + 0.52, 1.0, etapas[i + 1][1] - 0.52, 1.0, SUAVE)

    ax2 = fig.add_axes([0.10, 0.08, 0.82, 0.24])
    rng = np.random.default_rng(3)
    replicas = 5
    S = 2.38 + rng.normal(0, 0.06, replicas)
    ax2.errorbar(range(1, replicas + 1), S, yerr=0.06, fmt="o", color=AMBAR,
                 ecolor=CORAL, capsize=4, label="S por réplica")
    ax2.axhline(2.828, color=CIANO, linestyle="--", linewidth=1.5, label="ideal 2√2")
    ax2.axhline(2.0, color=CORAL, linestyle=":", linewidth=1.5, label="clássico 2")
    ax2.set_xlim(0.5, replicas + 0.5)
    ax2.set_ylim(1.8, 3.0)
    ax2.set_xlabel("réplica")
    ax2.set_ylabel("S")
    ax2.set_title("Replicação com incerteza", color=AMBAR, fontsize=12, loc="left")
    ax2.grid(alpha=0.12)
    ax2.legend(frameon=False, labelcolor=TEXTO, fontsize=8, ncol=3, loc="upper right")

    fig.suptitle("NÍVEL 2b · da execução à evidência replicável",
                 color=TEXTO, fontsize=16, fontweight="bold", x=0.02, ha="left")
    salvar(fig, "fig22_nivel5")


def main() -> None:
    print("Gerando ilustrações dos níveis…")
    nivel0()
    nivel1()
    nivel2()
    nivel3()
    nivel4()
    nivel5()
    print(f"Pronto: {FIG}")


if __name__ == "__main__":
    main()