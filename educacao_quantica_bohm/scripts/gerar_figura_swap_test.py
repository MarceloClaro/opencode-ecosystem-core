#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura da prática SWAP test: P(0) e sobreposição ideal/sim/backend."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
FIG = RAIZ / "livro" / "figuras_geradas"
FIG.mkdir(parents=True, exist_ok=True)

FUNDO = "#05070B"
TEXTO = "#E8F0FF"
SUAVE = "#94A3B8"
CIANO = "#5EEAD4"
AMBAR = "#FBBF24"
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


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
    rot = ["ideal", "simulado", "backend"]
    p0 = [0.8851, 0.8851, 0.8145]
    ov = [0.7702, 0.7702, 0.6289]
    cores = [SUAVE, CIANO, AMBAR]

    ax1.bar(rot, p0, color=cores)
    ax1.axhline(0.5, color="#FB7185", linestyle="--", linewidth=1.2)
    ax1.set_ylim(0, 1)
    ax1.set_ylabel("P(0) na ancilla")
    ax1.set_title("SWAP test: probabilidade", color=CIANO, fontsize=12, loc="left")
    ax1.grid(axis="y", alpha=0.12)
    for i, v in enumerate(p0):
        ax1.text(i, v + 0.03, f"{v:.4f}".replace(".", ","), ha="center", color=TEXTO, fontsize=9)

    ax2.bar(rot, ov, color=cores)
    ax2.axhline(0, color=SUAVE, linewidth=0.8)
    ax2.set_ylim(0, 1)
    ax2.set_ylabel("sobreposição estimada")
    ax2.set_title("SWAP test: sobreposição", color=AMBAR, fontsize=12, loc="left")
    ax2.grid(axis="y", alpha=0.12)
    for i, v in enumerate(ov):
        ax2.text(i, v + 0.03, f"{v:.4f}".replace(".", ","), ha="center", color=TEXTO, fontsize=9)

    fig.suptitle("SWAP test: a diferença entre simulação e hardware",
                 color=TEXTO, fontsize=15, fontweight="bold", x=0.02, ha="left")
    fig.text(0.02, -0.02,
             "Ideal: P(0)=0,8851 e overlap=0,7702. Backend Guoji08, 1024 tiros: P(0)=0,8145 e overlap=0,6289.",
             color=SUAVE, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "fig24_swap_test.png", dpi=220, bbox_inches="tight", facecolor=FUNDO)
    plt.close(fig)
    print("  ✓ fig24_swap_test")


if __name__ == "__main__":
    main()