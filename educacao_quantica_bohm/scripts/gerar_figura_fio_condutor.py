#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura 28: fio condutor da obra em 10 estações."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

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
VERDE = "#34D399"
CORAL = "#FB7185"

plt.rcParams.update({
    "figure.facecolor": FUNDO,
    "axes.facecolor": FUNDO,
    "savefig.facecolor": FUNDO,
    "text.color": TEXTO,
    "font.family": "DejaVu Sans",
})


def caixa(ax, x, y, texto, cor):
    ax.add_patch(FancyBboxPatch(
        (x - 0.85, y - 0.28), 1.7, 0.56,
        boxstyle="round,pad=0.02,rounding_size=0.10",
        facecolor=PAINEL, edgecolor=cor, linewidth=1.8,
    ))
    ax.text(x, y, texto, ha="center", va="center", color=cor, fontsize=8.5)


def seta(ax, x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12,
        color=SUAVE, linewidth=1.2,
    ))


def main():
    fig, ax = plt.subplots(figsize=(13, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")
    ax.set_title("O fio condutor: da informação ao projeto",
                 color=TEXTO, fontsize=15, fontweight="bold", loc="left", pad=10)

    linha1 = [
        ("1. Informação", CIANO), ("2. Medida", CIANO), ("3. Fase", CIANO),
        ("4. Emaranhamento", CIANO), ("5. Circuito", ROXO),
    ]
    linha2 = [
        ("6. Ruído", AMBAR), ("7. Hardware", AMBAR), ("8. Evidência", VERDE),
        ("9. Ética", CORAL), ("10. Projeto", VERDE),
    ]
    xs = [1.0, 3.0, 5.0, 7.0, 9.0]
    for x, (texto, cor) in zip(xs, linha1):
        caixa(ax, x, 3.0, texto, cor)
    xs2 = [9.0, 7.0, 5.0, 3.0, 1.0]
    for x, (texto, cor) in zip(xs2, linha2):
        caixa(ax, x, 1.4, texto, cor)

    for i in range(4):
        seta(ax, xs[i] + 0.88, 3.0, xs[i + 1] - 0.88, 3.0)
        seta(ax, xs2[i] - 0.88, 1.4, xs2[i + 1] + 0.88, 1.4)
    seta(ax, xs[-1], 2.68, xs2[0], 1.72)

    ax.text(5.0, 0.45,
            "Cada estação volta nos três níveis: N0 (imagem), N1 (circuito) e N2 (pesquisa).",
            ha="center", color=SUAVE, fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "fig28_fio_condutor.png", dpi=220, bbox_inches="tight", facecolor=FUNDO)
    plt.close(fig)
    print("  ✓ fig28_fio_condutor")


if __name__ == "__main__":
    main()
