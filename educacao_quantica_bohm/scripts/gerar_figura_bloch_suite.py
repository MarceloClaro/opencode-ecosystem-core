#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura da suíte de Bloch: vetores ideais/simulados e hardware + comprimentos."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados_hardware" / "bloch_suite_guoji08.json"
FIG = RAIZ / "livro" / "figuras_geradas"
FIG.mkdir(parents=True, exist_ok=True)

FUNDO = "#05070B"
TEXTO = "#E8F0FF"
SUAVE = "#94A3B8"
CORES = ["#5EEAD4", "#FBBF24", "#A78BFA", "#FB7185", "#34D399", "#60A5FA"]

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


def esfera(ax):
    u = np.linspace(0, 2 * np.pi, 40)
    v = np.linspace(0, np.pi, 20)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(x, y, z, color="#1E293B", linewidth=0.4, alpha=0.55)
    ax.plot([-1, 1], [0, 0], [0, 0], color="#334155", linewidth=0.8)
    ax.plot([0, 0], [-1, 1], [0, 0], color="#334155", linewidth=0.8)
    ax.plot([0, 0], [0, 0], [-1, 1], color="#334155", linewidth=0.8)
    ax.set_xlim(-1.05, 1.05); ax.set_ylim(-1.05, 1.05); ax.set_zlim(-1.05, 1.05)
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=22, azim=35)
    ax.grid(False)
    for eixo in (ax.xaxis, ax.yaxis, ax.zaxis):
        eixo.pane.set_facecolor((0, 0, 0, 0))
        eixo.pane.set_edgecolor("#22304A")
    ax.set_facecolor(FUNDO)


def main():
    d = json.loads(DADOS.read_text(encoding="utf-8"))
    sim = d["simulado"]
    hw = d.get("hardware", {})

    fig = plt.figure(figsize=(13, 5.8))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    esfera(ax)

    for i, (codigo, s) in enumerate(sim.items()):
        cor = CORES[i % len(CORES)]
        v = s["componentes"]
        ax.quiver(0, 0, 0, v["x"], v["y"], v["z"], color=cor, linewidth=2,
                  arrow_length_ratio=0.12, alpha=0.95)
        ax.text(v["x"] * 1.08, v["y"] * 1.08, v["z"] * 1.08, codigo,
                color=cor, fontsize=8)
        if codigo in hw:
            w = hw[codigo]["componentes"]
            ax.quiver(0, 0, 0, w["x"], w["y"], w["z"], color=cor, linewidth=1,
                      arrow_length_ratio=0.12, alpha=0.45, linestyle="--")
    ax.set_title("Vetores de Bloch: ideal (forte) e hardware (tracejado)",
                 color=TEXTO, fontsize=11, loc="left")

    ax2 = fig.add_subplot(1, 2, 2)
    codigos = list(sim.keys())
    ideais = [sim[c]["comprimento"] for c in codigos]
    reais = [hw.get(c, {}).get("comprimento", np.nan) for c in codigos]
    x = np.arange(len(codigos))
    ax2.bar(x - 0.18, ideais, 0.34, label="simulado", color="#5EEAD4")
    ax2.bar(x + 0.18, reais, 0.34, label="hardware", color="#FBBF24")
    ax2.set_xticks(x)
    ax2.set_xticklabels(codigos)
    ax2.axhline(1.0, color="#FB7185", linestyle=":", linewidth=1)
    ax2.set_ylim(0, 1.10)
    ax2.set_ylabel("|r| = √(x²+y²+z²)")
    ax2.set_title("Norma estimada: ruído e viés", color=TEXTO, fontsize=11, loc="left")
    ax2.legend(frameon=False, labelcolor=TEXTO, fontsize=8)
    ax2.grid(axis="y", alpha=0.12)

    fig.suptitle("Esfera de Bloch: seis circuitos, simulação e hardware",
                 color=TEXTO, fontsize=15, fontweight="bold", x=0.02, ha="left")
    fig.tight_layout()
    fig.savefig(FIG / "fig25_bloch_suite.png", dpi=220, bbox_inches="tight", facecolor=FUNDO)
    plt.close(fig)
    print("  ✓ fig25_bloch_suite")


if __name__ == "__main__":
    main()
