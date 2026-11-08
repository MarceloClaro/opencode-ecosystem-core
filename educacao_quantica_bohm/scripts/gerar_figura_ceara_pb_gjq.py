#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagrama da rede Ceará → Paraíba (CIQuanta) → GJQ/Tiangong → livro."""
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
VERDE = "#34D399"
AMBAR = "#FBBF24"
CIANO = "#5EEAD4"
CORAL = "#FB7185"

plt.rcParams.update({
    "figure.facecolor": FUNDO,
    "axes.facecolor": FUNDO,
    "savefig.facecolor": FUNDO,
    "text.color": TEXTO,
    "font.family": "DejaVu Sans",
})


def caixa(ax, x, y, w, h, titulo, linhas, cor):
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        facecolor=PAINEL, edgecolor=cor, linewidth=2,
    ))
    ax.text(x, y + h / 2 - 0.28, titulo, ha="center", va="top",
            color=cor, fontsize=11, fontweight="bold")
    ax.text(x, y - 0.05, "\n".join(linhas), ha="center", va="center",
            color=SUAVE, fontsize=8.2, linespacing=1.35)


def seta(ax, x1, y1, x2, y2, cor=SUAVE, texto=""):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
        color=cor, linewidth=1.4, connectionstyle="arc3,rad=0.08",
    ))
    if texto:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.18, texto,
                ha="center", color=SUAVE, fontsize=7.5)


def main():
    fig, ax = plt.subplots(figsize=(12, 6.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("Rede de estudo: Ceará, Paraíba e GJQ/Tiangong",
                 color=TEXTO, fontsize=15, fontweight="bold", loc="left", pad=12)

    caixa(ax, 2.0, 5.0, 3.1, 1.6, "CEARÁ",
          ["UFC · UECE · IFCE", "rede estadual e mediação", "ensino e pesquisa local"],
          VERDE)
    caixa(ax, 6.0, 5.0, 3.2, 1.6, "PARAÍBA · CIQUANTA",
          ["centro público", "20 + 100 qubits (portal)", "acesso por política pública"],
          AMBAR)
    caixa(ax, 10.0, 5.0, 3.0, 1.6, "GJQ · TIANGONG",
          ["Guoji08 (20 q) · Baihua (156 q)", "QASM, API, Sessions, MPS", "task IDs auditáveis"],
          CIANO)
    caixa(ax, 6.0, 1.7, 4.2, 1.5, "ESTE LIVRO",
          ["simulação × hardware", "práticas, fichas e DOI", "código e resultados abertos"],
          CORAL)

    seta(ax, 3.6, 5.0, 4.3, 5.0, VERDE, "formação")
    seta(ax, 7.6, 5.0, 8.4, 5.0, AMBAR, "comparação")
    seta(ax, 2.6, 4.2, 4.6, 2.5, VERDE, "autoria")
    seta(ax, 6.0, 4.2, 6.0, 2.5, AMBAR, "dados")
    seta(ax, 9.4, 4.2, 7.4, 2.5, CIANO, "hardware")

    ax.text(6.0, 0.55,
            "Parceria de estudo e acesso — não é convênio institucional formal nem endosso das instituições.",
            ha="center", color=SUAVE, fontsize=8.5)

    fig.tight_layout()
    fig.savefig(FIG / "fig26_ceara_pb_gjq.png", dpi=220, bbox_inches="tight", facecolor=FUNDO)
    plt.close(fig)
    print("  ✓ fig26_ceara_pb_gjq")


if __name__ == "__main__":
    main()
