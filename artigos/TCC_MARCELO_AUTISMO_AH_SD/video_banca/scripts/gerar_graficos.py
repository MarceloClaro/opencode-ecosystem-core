#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os gráficos do vídeo a partir dos CSVs oficiais do TCC."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

BASE = Path(__file__).resolve().parent.parent
DADOS = BASE.parent / "dados"
OUT = BASE / "charts"
OUT.mkdir(exist_ok=True)

NAVY = "#0B1F3A"
TEAL = "#5BC0BE"
AMBER = "#F2B84B"
CORAL = "#D95D39"
OFF = "#F5F1E8"
MUTED = "#A8B8C8"
GRID = "#2A4A6A"

plt.rcParams.update({
    "font.family": "Liberation Sans",
    "text.color": OFF,
    "axes.labelcolor": OFF,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.edgecolor": GRID,
    "figure.facecolor": NAVY,
    "axes.facecolor": NAVY,
    "savefig.facecolor": NAVY,
})


def ler_csv(nome: str) -> list[dict]:
    with (DADOS / nome).open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def estilo(ax):
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(GRID)
    ax.grid(axis="y", color=GRID, linestyle="--", linewidth=0.8, alpha=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=13)


def grafico_nacional():
    serie = ler_csv("serie_nacional.csv")
    anos = [int(r["ano"]) for r in serie]
    tea = [int(r["tea_total"]) for r in serie]
    ah = [int(r["ahsd_total"]) for r in serie]
    tea_idx = [100 * v / tea[0] for v in tea]
    ah_idx = [100 * v / ah[0] for v in ah]

    fig, ax = plt.subplots(figsize=(9.2, 4.8), dpi=200)
    estilo(ax)
    ax.plot(anos, tea_idx, color=TEAL, lw=4, marker="o", ms=9, label="TEA")
    ax.plot(anos, ah_idx, color=AMBER, lw=4, marker="o", ms=9, label="AH/SD")
    ax.axhline(100, color=MUTED, lw=1, ls=":", alpha=0.6)
    ax.set_xlim(2020.7, 2024.55)
    ax.set_ylim(80, 340)
    ax.set_xticks(anos)
    ax.set_ylabel("índice (2021 = 100)", fontsize=13)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}"))
    ax.legend(loc="upper left", frameon=False, fontsize=14, handlelength=1.6)
    ax.annotate(f"{tea_idx[-1]:.0f}", (anos[-1], tea_idx[-1]), xytext=(10, 2),
                textcoords="offset points", color=TEAL, fontsize=22, fontweight="bold")
    ax.annotate(f"{ah_idx[-1]:.0f}", (anos[-1], ah_idx[-1]), xytext=(10, -4),
                textcoords="offset points", color=AMBER, fontsize=22, fontweight="bold")
    fig.subplots_adjust(left=0.10, right=0.93, top=0.90, bottom=0.16)
    fig.savefig(OUT / "national.png")
    plt.close(fig)


def grafico_ratio():
    serie = ler_csv("serie_nacional.csv")
    anos = [int(r["ano"]) for r in serie]
    razao = [float(r["razao_tea_ahsd"]) for r in serie]
    cores = [TEAL] * (len(razao) - 1) + [AMBER]

    fig, ax = plt.subplots(figsize=(9.2, 4.8), dpi=200)
    estilo(ax)
    barras = ax.bar([str(a) for a in anos], razao, color=cores, width=0.55)
    for b, v in zip(barras, razao):
        ax.annotate(f"{v:.1f}".replace(".", ","), (b.get_x() + b.get_width()/2, v),
                    xytext=(0, 5), textcoords="offset points", ha="center",
                    color=OFF, fontsize=18, fontweight="bold")
    ax.set_ylim(0, 25)
    ax.set_ylabel("razão TEA/AH/SD", fontsize=13)
    ax.tick_params(axis="x", labelsize=15)
    fig.subplots_adjust(left=0.10, right=0.97, top=0.92, bottom=0.14)
    fig.savefig(OUT / "ratio.png")
    plt.close(fig)


def grafico_regioes():
    regs = ler_csv("regioes_2024.csv")
    nomes = [r["regiao"] for r in regs]
    vals = [float(r["razao_tea_ahsd"]) for r in regs]
    cores = []
    for n in nomes:
        if n == "Nordeste":
            cores.append(AMBER)
        elif n == "Sul":
            cores.append(TEAL)
        else:
            cores.append("#3E6B8C")

    fig, ax = plt.subplots(figsize=(9.2, 4.8), dpi=200)
    estilo(ax)
    ax.grid(axis="x", color=GRID, linestyle="--", linewidth=0.8, alpha=0.6)
    ax.grid(axis="y", visible=False)
    barras = ax.barh(nomes[::-1], vals[::-1], color=cores[::-1], height=0.55)
    for b, v in zip(barras, vals[::-1]):
        ax.annotate(f"{v:.1f}".replace(".", ","), (v, b.get_y() + b.get_height()/2),
                    xytext=(6, 0), textcoords="offset points", va="center",
                    color=OFF, fontsize=17, fontweight="bold")
    ax.set_xlim(0, 55)
    ax.set_xlabel("razão TEA/AH/SD", fontsize=13)
    ax.tick_params(axis="y", labelsize=14)
    fig.subplots_adjust(left=0.22, right=0.93, top=0.92, bottom=0.14)
    fig.savefig(OUT / "regions.png")
    plt.close(fig)


def grafico_estados():
    estados = ler_csv("estados_2024.csv")
    por_uf = {r["uf"]: float(r["razao"]) for r in estados}
    ordem = ["Ceará", "Pernambuco", "São Paulo", "Minas Gerais",
             "Espírito Santo", "Santa Catarina", "Distrito Federal", "Paraná"]
    vals = [por_uf[uf] for uf in ordem]
    cores = [AMBER if uf == "Ceará" else TEAL if uf == "Paraná" else "#3E6B8C" for uf in ordem]

    fig, ax = plt.subplots(figsize=(9.2, 4.8), dpi=200)
    estilo(ax)
    ax.grid(axis="x", color=GRID, linestyle="--", linewidth=0.8, alpha=0.6)
    ax.grid(axis="y", visible=False)
    barras = ax.barh(ordem[::-1], vals[::-1], color=cores[::-1], height=0.55)
    for b, v in zip(barras, vals[::-1]):
        ax.annotate(f"{v:.1f}".replace(".", ","), (v, b.get_y() + b.get_height()/2),
                    xytext=(6, 0), textcoords="offset points", va="center",
                    color=OFF, fontsize=16, fontweight="bold")
    ax.set_xlim(0, 145)
    ax.set_xlabel("razão TEA/AH/SD", fontsize=13)
    ax.tick_params(axis="y", labelsize=14)
    fig.subplots_adjust(left=0.26, right=0.92, top=0.92, bottom=0.14)
    fig.savefig(OUT / "states.png")
    plt.close(fig)


def main() -> int:
    grafico_nacional()
    grafico_ratio()
    grafico_regioes()
    grafico_estados()
    print("OK:", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
