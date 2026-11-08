#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Desenha os circuitos do manual do leitor (GHZ, CHSH, SWAP, VQC)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit

RAIZ = Path(__file__).resolve().parents[1]
FIG = RAIZ / "livro" / "figuras_geradas"
FIG.mkdir(parents=True, exist_ok=True)

FUNDO = "#05070B"
TEXTO = "#E8F0FF"
CIANO = "#5EEAD4"
SUAVE = "#94A3B8"

ESTILO = {
    "backgroundcolor": FUNDO,
    "textcolor": TEXTO,
    "linecolor": CIANO,
    "gatefacecolor": "#1E293B",
    "gatetextcolor": TEXTO,
    "barrierfacecolor": "#1E293B",
    "subtextcolor": SUAVE,
}


def salvar(fig, nome: str) -> None:
    fig.set_facecolor(FUNDO)
    fig.savefig(FIG / f"{nome}.png", dpi=220, bbox_inches="tight", facecolor=FUNDO)
    plt.close(fig)
    print(f"  ✓ {nome}")


def ghz() -> None:
    qc = QuantumCircuit(4, 4)
    qc.h(0)
    for q in (1, 2, 3):
        qc.cx(0, q)
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    fig = qc.draw("mpl", style=ESTILO)
    fig.suptitle("GHZ de 4 qubits · Guoji08 · 1024 tiros", color=TEXTO,
                 fontsize=15, fontweight="bold", x=0.02, ha="left", y=1.02)
    fig.text(0.02, -0.03, "H(0) + CNOT(0,1) + CNOT(0,2) + CNOT(0,3) + medida",
             color=SUAVE, fontsize=9)
    salvar(fig, "fig29_circuito_ghz")


def chsh() -> None:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.ry(-np.pi / 4, 1)
    qc.measure([0, 1], [0, 1])
    fig = qc.draw("mpl", style=ESTILO)
    fig.suptitle("CHSH · configuração E00 · Guoji08", color=TEXTO,
                 fontsize=15, fontweight="bold", x=0.02, ha="left", y=1.02)
    fig.text(0.02, -0.03, "H(0) + CNOT(0,1) + Ry(-π/4,1) + medida",
             color=SUAVE, fontsize=9)
    salvar(fig, "fig30_circuito_chsh")


def swap() -> None:
    qc = QuantumCircuit(3, 1)
    qc.ry(1.0, 2)
    qc.h(0)
    qc.cswap(0, 1, 2)
    qc.h(0)
    qc.measure(0, 0)
    fig = qc.draw("mpl", style=ESTILO)
    fig.suptitle("SWAP test · sobreposição de dois estados", color=TEXTO,
                 fontsize=15, fontweight="bold", x=0.02, ha="left", y=1.02)
    fig.text(0.02, -0.03, "Ry(1,0)(2) + H(0) + CSWAP(0,1,2) + H(0) + medida",
             color=SUAVE, fontsize=9)
    salvar(fig, "fig31_circuito_swap")


def vqc() -> None:
    qc = QuantumCircuit(2, 1)
    theta = [1.5708, 1.5708, -1.5708, 2.819]
    qc.ry(0.0, 0)
    qc.ry(0.0, 1)
    qc.ry(theta[0], 0)
    qc.ry(theta[1], 1)
    qc.cx(0, 1)
    qc.ry(theta[2], 0)
    qc.ry(theta[3], 1)
    qc.measure(0, 0)
    fig = qc.draw("mpl", style=ESTILO)
    fig.suptitle("VQC XOR · circuito mínimo de 2 qubits", color=TEXTO,
                 fontsize=15, fontweight="bold", x=0.02, ha="left", y=1.02)
    fig.text(0.02, -0.03, "Ry de codificação + uma camada variacional + CNOT; o treino usa 3 camadas",
             color=SUAVE, fontsize=9)
    salvar(fig, "fig32_circuito_vqc")


def main() -> None:
    ghz()
    chsh()
    swap()
    vqc()


if __name__ == "__main__":
    main()
