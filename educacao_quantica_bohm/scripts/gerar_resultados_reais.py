#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera as figuras dos resultados reais (GHZ e VQC) da edição Bohm/black.

Lê os JSONs em dados_hardware/ e produz:
- fig12_ghz4_resultados.png/svg
- fig13_vqc_xor.png/svg
- fig14_escada_desafios.png/svg
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados_hardware"
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


def salvar(fig, nome: str, svg: bool = True) -> None:
    fig.savefig(FIG / f"{nome}.png", dpi=220, bbox_inches="tight", facecolor=FUNDO)
    if svg:
        fig.savefig(FIG / f"{nome}.svg", bbox_inches="tight", facecolor=FUNDO)
    plt.close(fig)
    print("  ✓", nome)


def ghz() -> None:
    dados = json.loads((DADOS / "ghz4_guoji08.json").read_text(encoding="utf-8"))
    counts = {k: int(v) for k, v in dados["counts"].items()}
    total = sum(counts.values())
    p0000 = counts.get("0000", 0) / total
    p1111 = counts.get("1111", 0) / total
    outros = 1 - p0000 - p1111
    fidelidade = p0000 + p1111

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2),
                                   gridspec_kw={"width_ratios": [1, 1.7]})

    rotulos = ["|0000⟩", "|1111⟩", "outros"]
    ideal = [0.5, 0.5, 0.0]
    real = [p0000, p1111, outros]
    x = np.arange(3)
    ax1.bar(x - 0.18, ideal, 0.34, label="ideal", color=CIANO, alpha=0.9)
    ax1.bar(x + 0.18, real, 0.34, label="Guoji08", color=AMBAR, alpha=0.9)
    ax1.set_xticks(x)
    ax1.set_xticklabels(rotulos)
    ax1.set_ylim(0, 0.62)
    ax1.set_ylabel("frequência")
    ax1.set_title("Ideal × backend", color=TEXTO, fontsize=14, loc="left")
    ax1.legend(frameon=False, labelcolor=TEXTO, fontsize=9)
    ax1.grid(axis="y", alpha=0.12)
    for i, v in enumerate(real):
        ax1.text(i + 0.18, v + 0.015, f"{v:.1%}", ha="center", color=TEXTO, fontsize=9)
    ax1.text(0.02, 0.93, f"fidelidade proxy = {fidelidade:.1%}",
             transform=ax1.transAxes, color=SUAVE, fontsize=10, va="top")

    # distribuição completa
    itens = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    labels = [k for k, _ in itens]
    vals = [v for _, v in itens]
    cores = [CIANO if k == "0000" else AMBAR if k == "1111" else "#334155"
             for k in labels]
    y = np.arange(len(labels))
    ax2.barh(y, vals, color=cores)
    ax2.set_yticks(y)
    ax2.set_yticklabels(labels, fontsize=8)
    ax2.invert_yaxis()
    ax2.set_xlabel("contagens em 1024 tiros")
    ax2.set_title("Distribuição completa (os erros não são uniformes)",
                  color=TEXTO, fontsize=14, loc="left")
    ax2.grid(axis="x", alpha=0.12)
    for i, v in enumerate(vals):
        ax2.text(v + 4, i, str(v), va="center", color=SUAVE, fontsize=7.5)

    fig.suptitle("GHZ de 4 qubits no computador supercondutor Guoji08",
                 color=TEXTO, fontsize=18, fontweight="bold", x=0.02,
                 ha="left", y=1.03)
    fig.text(0.02, -0.02,
             "Circuito transpilado: profundidade 13. O ruído e a leitura produzem "
             "21,2% de resultados fora de 0000/1111.",
             color=SUAVE, fontsize=9)
    fig.tight_layout()
    salvar(fig, "fig12_ghz4_resultados", svg=True)


def vqc() -> None:
    dados = json.loads((DADOS / "vqc_xor_guoji08.json").read_text(encoding="utf-8"))
    thetas = dados["theta"]
    resultados = dados["resultados"]

    # valores ideais e de ruído simulados (recalculados aqui, para a figura)
    import pennylane as qml

    X = [(0, 0), (0, 1), (1, 0), (1, 1)]

    def probabilidades(canal=None, forca=0.0):
        dev = qml.device("default.mixed", wires=2)

        @qml.qnode(dev)
        def c(x):
            qml.RY(np.pi * x[0], wires=0)
            qml.RY(np.pi * x[1], wires=1)
            if canal:
                for w in (0, 1):
                    canal(forca, wires=w)
            qml.RY(thetas[0], wires=0)
            qml.RY(thetas[1], wires=1)
            if canal:
                for w in (0, 1):
                    canal(forca, wires=w)
            qml.CNOT(wires=[0, 1])
            if canal:
                for w in (0, 1):
                    canal(forca, wires=w)
            qml.RY(thetas[2], wires=0)
            qml.RY(thetas[3], wires=1)
            if canal:
                for w in (0, 1):
                    canal(forca, wires=w)
            return qml.expval(qml.Z(0))

        return [(1 - float(c(x))) / 2 for x in X]

    p_ideal = probabilidades()
    p_phase = probabilidades(qml.PhaseDamping, 0.05)
    p_depol = probabilidades(qml.DepolarizingChannel, 0.05)
    p_hw = [r["p1"] for r in resultados]

    rotulos = ["00 → 0", "01 → 1", "10 → 1", "11 → 0"]
    x = np.arange(4)
    larg = 0.20
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.bar(x - 1.5 * larg, p_ideal, larg, label="ideal (simulador)", color=CIANO)
    ax.bar(x - 0.5 * larg, p_phase, larg, label="phase damping γ=0,05", color=ROXO)
    ax.bar(x + 0.5 * larg, p_depol, larg, label="depolarizante p=0,05", color=CORAL)
    ax.bar(x + 1.5 * larg, p_hw, larg, label="backend Guoji08", color=AMBAR)
    ax.axhline(0.5, color=SUAVE, lw=1.2, ls="--", alpha=0.7)
    ax.text(3.55, 0.515, "limiar 0,5", color=SUAVE, fontsize=8, ha="right")
    ax.set_xticks(x)
    ax.set_xticklabels(rotulos)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("P(qubit 0 = 1)")
    ax.set_title("VQC XOR: ideal, ruído simulado e backend",
                 color=TEXTO, fontsize=17, fontweight="bold", loc="left", pad=12)
    ax.legend(frameon=False, labelcolor=TEXTO, fontsize=9, ncol=4,
              loc="upper center", bbox_to_anchor=(0.5, -0.12))
    ax.grid(axis="y", alpha=0.12)
    ax.set_ylim(0, 1.08)
    salvar(fig, "fig13_vqc_xor", svg=True)



def chsh() -> None:
    dados = json.loads((DADOS / "chsh_guoji08.json").read_text(encoding="utf-8"))
    E = dados["E"]
    S = dados["S"]
    nomes = ["E00", "E01", "E10", "E11"]
    ideal = [0.7071, 0.7071, 0.7071, -0.7071]
    real = [E[n] for n in nomes]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8),
                                   gridspec_kw={"width_ratios": [1.6, 1]})
    x = np.arange(4)
    ax1.bar(x - 0.18, ideal, 0.34, label="ideal", color=CIANO)
    ax1.bar(x + 0.18, real, 0.34, label="Guoji08", color=AMBAR)
    ax1.axhline(0, color=SUAVE, lw=1)
    ax1.axhline(0.7071, color=SUAVE, lw=1, ls=":", alpha=0.6)
    ax1.axhline(-0.7071, color=SUAVE, lw=1, ls=":", alpha=0.6)
    ax1.set_xticks(x)
    ax1.set_xticklabels(nomes)
    ax1.set_ylim(-1, 1)
    ax1.set_ylabel("correlador E")
    ax1.set_title("Correladores medidos", color=TEXTO, fontsize=14, loc="left")
    ax1.legend(frameon=False, labelcolor=TEXTO, fontsize=9)
    ax1.grid(axis="y", alpha=0.12)
    for i, v in enumerate(real):
        ax1.text(i + 0.18, v + (0.05 if v >= 0 else -0.12), f"{v:+.3f}",
                 ha="center", color=TEXTO, fontsize=9)

    ax2.bar(["clássico", "Guoji08", "ideal"], [2.0, S, 2 * np.sqrt(2)],
            color=[SUAVE, AMBAR, CIANO])
    ax2.axhline(2.0, color=CORAL, lw=1.5, ls="--")
    ax2.set_ylim(0, 3.1)
    ax2.set_ylabel("S")
    ax2.set_title("Violação de CHSH", color=TEXTO, fontsize=14, loc="left")
    ax2.grid(axis="y", alpha=0.12)
    for i, v in enumerate([2.0, S, 2 * np.sqrt(2)]):
        ax2.text(i, v + 0.05, f"{v:.3f}", ha="center", color=TEXTO, fontsize=9)

    fig.suptitle("CHSH no Guoji08: S = 2,381 (acima do limite clássico 2)",
                 color=TEXTO, fontsize=17, fontweight="bold", x=0.02,
                 ha="left", y=1.03)
    fig.text(0.02, -0.02,
             "Quatro circuitos, 1024 tiros cada. O valor ideal é 2√2 ≈ 2,828; "
             "o backend viola o limite clássico, mas não alcança o ideal.",
             color=SUAVE, fontsize=9)
    fig.tight_layout()
    salvar(fig, "fig15_chsh", svg=True)


def backends() -> None:
    g = json.loads((DADOS / "ghz4_guoji08.json").read_text(encoding="utf-8"))
    b = json.loads((DADOS / "ghz4_baihua.json").read_text(encoding="utf-8"))
    def frac(d):
        c = {k: int(v) for k, v in d["counts"].items()}
        t = sum(c.values())
        return [c.get("0000", 0) / t, c.get("1111", 0) / t,
                1 - (c.get("0000", 0) + c.get("1111", 0)) / t]
    fg, fb = frac(g), frac(b)
    rot = ["|0000⟩", "|1111⟩", "outros"]
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.bar(x - 0.18, fg, 0.34, label="Guoji08 (20 q)", color=CIANO)
    ax.bar(x + 0.18, fb, 0.34, label="Baihua (156 q)", color=AMBAR)
    ax.axhline(0.5, color=SUAVE, lw=1, ls="--", alpha=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(rot)
    ax.set_ylim(0, 0.62)
    ax.set_ylabel("frequência")
    ax.set_title("GHZ de 4 qubits em dois backends reais",
                 color=TEXTO, fontsize=17, fontweight="bold", loc="left", pad=12)
    ax.legend(frameon=False, labelcolor=TEXTO, fontsize=9)
    ax.grid(axis="y", alpha=0.12)
    for i, (a, c) in enumerate(zip(fg, fb)):
        ax.text(i - 0.18, a + 0.02, f"{a:.1%}", ha="center", color=TEXTO, fontsize=8)
        ax.text(i + 0.18, c + 0.02, f"{c:.1%}", ha="center", color=TEXTO, fontsize=8)
    ax.text(0.02, 0.93, "mais qubits não significa menos ruído: calibração e mapeamento importam",
            transform=ax.transAxes, color=SUAVE, fontsize=9, va="top")
    salvar(fig, "fig16_backends", svg=True)


def escada() -> None:
    fig, ax = plt.subplots(figsize=(12, 5.6))
    ax.set_xlim(0, 10.4)
    ax.set_ylim(0, 7)
    ax.axis("off")

    degraus = [
        (0.35, 1.0, "Nível 1 — 4 pontos", "2 qubits · XOR\n100% no backend", CIANO),
        (2.75, 2.5, "Nível 2 — moons reduzido", "4 qubits · treino/teste\nmúltiplas seeds", AMBAR),
        (5.15, 4.0, "Nível 3 — ruído controlado", "phase damping × depolarização\nestatística", ROXO),
        (7.55, 5.5, "Nível 4 — treino no backend", "filas, custo, deriva\npesquisa de fronteira", CORAL),
    ]
    for i, (x0, y0, titulo, sub, cor) in enumerate(degraus):
        ax.add_patch(plt.Rectangle((x0, y0), 2.55, 1.2, facecolor=PAINEL,
                                   edgecolor=cor, lw=2.2, joinstyle="round"))
        ax.text(x0 + 0.12, y0 + 0.82, titulo, color=TEXTO, fontsize=8.6,
                fontweight="bold", va="center")
        ax.text(x0 + 0.12, y0 + 0.38, sub, color=SUAVE, fontsize=7.4,
                va="center", linespacing=1.25)
        if i < len(degraus) - 1:
            ax.annotate("", xy=(degraus[i + 1][0] - 0.08, degraus[i + 1][1] + 0.6),
                        xytext=(x0 + 2.55, y0 + 0.6),
                        arrowprops=dict(arrowstyle="-|>", color=cor, lw=2,
                                        connectionstyle="arc3,rad=-0.15"))

    ax.text(0.4, 6.55, "A escada do teste quântico real",
            color=TEXTO, fontsize=19, fontweight="bold")
    ax.text(0.4, 6.05, "cada degrau exige mais dados, mais controle e mais honestidade estatística",
            color=SUAVE, fontsize=11)
    ax.text(0.4, 0.35, "O nível 1 é uma demonstração de pipeline; não é evidência de ruído benéfico.",
            color=SUAVE, fontsize=9)
    salvar(fig, "fig14_escada_desafios", svg=True)


def main() -> None:
    print("Gerando resultados reais…")
    ghz()
    vqc()
    chsh()
    backends()
    escada()
    print(f"Pronto: {FIG}")


if __name__ == "__main__":
    main()