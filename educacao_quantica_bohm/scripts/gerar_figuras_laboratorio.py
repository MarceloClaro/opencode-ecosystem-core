#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura 27: seis esferas de Bloch em projeção XZ, ideal vs hardware."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
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


def main():
    d = json.loads(DADOS.read_text(encoding="utf-8"))
    sim = d["simulado"]
    hw = d.get("hardware", {})
    fig, eixos = plt.subplots(2, 3, figsize=(12, 7.2))
    for ax, (codigo, s), cor in zip(eixos.ravel(), sim.items(), CORES):
        v = s["componentes"]
        w = hw.get(codigo, {}).get("componentes", {})
        eixo_h = "Y" if abs(v["y"]) > abs(v["x"]) and abs(v["y"]) > abs(v["z"]) else "X"
        hs = v["y"] if eixo_h == "Y" else v["x"]
        hwv = w.get("y", 0.0) if eixo_h == "Y" else w.get("x", 0.0)
        ax.add_patch(plt.Circle((0, 0), 1.0, fill=False, color="#334155", linewidth=1.2))
        ax.plot([-1.1, 1.1], [0, 0], color="#22304A", linewidth=0.8)
        ax.plot([0, 0], [-1.1, 1.1], color="#22304A", linewidth=0.8)
        ax.annotate("", xy=(hs, v["z"]), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color=cor, lw=2))
        if w:
            ax.annotate("", xy=(hwv, w["z"]), xytext=(0, 0),
                        arrowprops=dict(arrowstyle="-|>", color=cor, lw=1.2, ls="--"))
        ax.set_xlim(-1.15, 1.15)
        ax.set_ylim(-1.15, 1.15)
        ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"{codigo} — {s['rotulo']}", color=cor, fontsize=10, loc="left")
        ax.text(0.02, 0.04, f"{eixo_h}Z · y = {v['y']:+.2f}".replace(".", ","),
                transform=ax.transAxes, color=SUAVE, fontsize=8)
    fig.suptitle("Esferas de Bloch: projeções XZ/YZ, ideal (forte) e hardware (tracejado)",
                 color=TEXTO, fontsize=14, fontweight="bold", x=0.02, ha="left")
    fig.text(0.02, 0.01, "O eixo vertical é Z; o horizontal é X ou Y, indicado no rodapé de cada painel.",
             color=SUAVE, fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(FIG / "fig27_bloch_paineis.png", dpi=220, bbox_inches="tight", facecolor=FUNDO)
    plt.close(fig)
    print("  ✓ fig27_bloch_paineis")


if __name__ == "__main__":
    main()
