#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera a figura de calibração a partir de `dados_hardware/calibracao_basica.csv`.

O CSV não declara backend, data nem unidades. A figura usa:
- T1/T2 em µs (unidade usual; confirmar no console);
- fidelidades em %;
- frequências em GHz.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "dados_hardware" / "calibracao_basica.csv"
FIG = RAIZ / "livro" / "figuras_geradas"
FIG.mkdir(parents=True, exist_ok=True)

FUNDO = "#05070B"
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


def ler():
    with CSV.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def faixa(ax, minimo, maximo, media, cor, titulo, unidade, xlim=None, log=False):
    ax.plot([minimo, maximo], [0, 0], color=cor, linewidth=8, solid_capstyle="round", alpha=0.9)
    ax.scatter([media], [0], color="white", s=30, zorder=5)
    ax.set_yticks([])
    ax.set_ylim(-0.5, 0.5)
    if xlim:
        ax.set_xlim(*xlim)
    if log:
        ax.set_xscale("log")
    ax.set_title(titulo, color=cor, fontsize=11, loc="left")
    ax.set_xlabel(unidade)
    ax.grid(axis="x", alpha=0.12)
    texto = f"{minimo:.2f}–{maximo:.2f}\nmédia {media:.2f}".replace(".", ",")
    ax.text(0.03, 0.78, texto, transform=ax.transAxes, color=SUAVE,
            fontsize=8.5, ha="left", va="top")


def main():
    dados = {d["Parameter"].strip(): d for d in ler()}
    fig, eixos = plt.subplots(2, 3, figsize=(13, 6.2))
    axs = eixos.ravel()

    itens = [
        ("relaxation time T1", "T1", "µs", CIANO, (0.3, 300), True),
        ("decoherence time T2", "T2", "µs", AMBAR, (0.3, 100), True),
        ("single qubit fidelity", "Fidelidade 1 qubit", "%", VERDE, (85, 100.5), False),
        ("double gate fidelit", "Fidelidade 2 qubits", "%", ROXO, (85, 100.5), False),
        ("bit frequency", "Frequência do bit", "GHz", AMBAR, (3, 8), False),
        ("cavity frequency", "Frequência da cavidade", "GHz", CORAL, (3, 8), False),
    ]
    for ax, (chave, titulo, unidade, cor, xlim, log) in zip(axs, itens):
        d = dados[chave]
        faixa(ax, float(d["Minimum"]), float(d["Maximum"]), float(d["Average"]),
              cor, titulo, unidade, xlim, log)

    fig.suptitle("Calibração do backend: uma fotografia, não uma garantia",
                 color=TEXTO, fontsize=15, fontweight="bold", x=0.02, ha="left")
    fig.text(0.02, 0.01,
             "Fonte: Basic information.csv (backend e data não declarados). "
             "Unidades inferidas; confirme no console.",
             color=SUAVE, fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(FIG / "fig23_calibracao.png", dpi=220, bbox_inches="tight", facecolor=FUNDO)
    plt.close(fig)
    print("  ✓ fig23_calibracao")


if __name__ == "__main__":
    main()