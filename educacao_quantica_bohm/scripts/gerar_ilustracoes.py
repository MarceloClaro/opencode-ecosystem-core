#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera as ilustrações da edição Bohm (design black) com código.

- PennyLane, Cirq e Qiskit desenham/simulam o mesmo estado de Bell.
- NumPy/Matplotlib geram as figuras didáticas de onda piloto, interferência,
  holograma (analogia da ordem implicada) e roda de diálogo.
- PIL compõe o painel "três linguagens, um estado".

Execute com o ambiente que tem as três bibliotecas:

    .venv-quantum/bin/python educacao_quantica_bohm/scripts/gerar_ilustracoes.py
"""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
from PIL import Image, ImageDraw, ImageFont

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


def salvar(fig: plt.Figure, nome: str, svg: bool = True) -> None:
    fig.savefig(FIG / f"{nome}.png", dpi=220, bbox_inches="tight", facecolor=FUNDO)
    if svg:
        fig.savefig(FIG / f"{nome}.svg", bbox_inches="tight", facecolor=FUNDO)
    plt.close(fig)
    print("  ✓", nome)


def _titulo(fig: plt.Figure, titulo: str, sub: str = "") -> None:
    fig.text(0.02, 0.98, titulo, ha="left", va="top", fontsize=22,
             fontweight="bold", color=TEXTO)
    if sub:
        fig.text(0.02, 0.925, sub, ha="left", va="top", fontsize=13, color=SUAVE)


# ---------------------------------------------------------------------------
# 1. Capa
# ---------------------------------------------------------------------------

def capa() -> None:
    fig = plt.figure(figsize=(8.27, 11.69), facecolor=FUNDO)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # grade sutil
    for x in np.linspace(0.05, 0.95, 12):
        ax.plot([x, x], [0, 1], color="#FFFFFF", alpha=0.035, lw=0.8)
    for y in np.linspace(0.05, 0.95, 16):
        ax.plot([0, 1], [y, y], color="#FFFFFF", alpha=0.035, lw=0.8)

    # holograma fantasma (B reconstruído)
    letra = _letra_b(256)
    F = np.fft.fftshift(np.fft.fft2(letra))
    yy, xx = np.mgrid[0:256, 0:256]
    cy = cx = 128
    mask = ((xx - cx) ** 2 + (yy - cy) ** 2) < (0.06 * 256) ** 2
    rec = np.abs(np.fft.ifft2(np.fft.ifftshift(F * mask)))
    ax.imshow(rec, cmap="gray", extent=(0.36, 0.94, 0.38, 0.80),
              alpha=0.22, origin="lower", aspect="auto")

    # frentes de onda
    x = np.linspace(0, 1, 900)
    for i, (cor, fase, alpha) in enumerate([(CIANO, 0.0, 0.55), (AMBAR, math.pi, 0.35)]):
        y = 0.24 + 0.045 * np.sin(2 * np.pi * 7 * x + fase)
        ax.plot(x, y, color=cor, lw=2.2, alpha=alpha)
        ax.plot(x, y + 0.022, color=cor, lw=1.0, alpha=alpha * 0.35)

    # esfera quântica
    for r, a in [(0.20, 0.10), (0.155, 0.16), (0.11, 0.22), (0.075, 0.35)]:
        ax.add_patch(Circle((0.5, 0.60), r, fill=False, ec=CIANO, lw=1.2, alpha=a))
    ax.add_patch(Circle((0.5, 0.60), 0.045, color=CIANO, alpha=0.85))
    ax.add_patch(Circle((0.5, 0.60), 0.085, color=CIANO, alpha=0.10))

    # órbitas
    theta = np.linspace(0, 2 * np.pi, 400)
    ax.plot(0.5 + 0.23 * np.cos(theta), 0.60 + 0.075 * np.sin(theta),
            color=ROXO, lw=1.4, alpha=0.55)
    ax.plot(0.5 + 0.075 * np.cos(theta), 0.60 + 0.23 * np.sin(theta),
            color=AMBAR, lw=1.1, alpha=0.40)

    # pontos
    rng = np.random.default_rng(7)
    for _ in range(30):
        ax.scatter(rng.uniform(0.05, 0.95), rng.uniform(0.05, 0.95),
                   s=rng.uniform(1, 7), color="#FFFFFF", alpha=rng.uniform(0.1, 0.4))

    fig.savefig(FIG / "capa_bohm.png", dpi=220, facecolor=FUNDO)
    plt.close(fig)
    print("  ✓ capa_bohm")


# ---------------------------------------------------------------------------
# 2. Onda piloto (modelo didático)
# ---------------------------------------------------------------------------

def onda_piloto() -> None:
    fig = plt.figure(figsize=(11, 6.2))
    ax = fig.add_axes([0.055, 0.12, 0.61, 0.76])
    axi = fig.add_axes([0.70, 0.12, 0.24, 0.76])
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.52, 0.52)
    ax.set_facecolor(FUNDO)
    for s in ax.spines.values():
        s.set_color("#22304A")

    # parede com duas fendas
    ax.plot([0.18, 0.18], [-0.52, -0.155], color="#94A3B8", lw=7, solid_capstyle="butt")
    ax.plot([0.18, 0.18], [0.155, 0.52], color="#94A3B8", lw=7, solid_capstyle="butt")
    ax.plot([0.18, 0.18], [-0.045, 0.045], color="#94A3B8", lw=7, solid_capstyle="butt")
    ax.annotate("fenda 1", xy=(0.18, 0.10), xytext=(0.25, 0.24),
                color=SUAVE, fontsize=12, ha="left",
                arrowprops=dict(arrowstyle="-", color=SUAVE, lw=1, alpha=0.6))
    ax.annotate("fenda 2", xy=(0.18, -0.10), xytext=(0.25, -0.26),
                color=SUAVE, fontsize=12, ha="left",
                arrowprops=dict(arrowstyle="-", color=SUAVE, lw=1, alpha=0.6))
    ax.annotate("", xy=(0.16, 0.0), xytext=(0.045, 0.0),
                arrowprops=dict(arrowstyle="->", color=CIANO, lw=2))
    ax.scatter([0.04], [0.0], s=40, color=CIANO)
    ax.text(0.035, 0.045, "fonte", color=SUAVE, fontsize=12, ha="left")

    # trajetórias guiadas por um campo estilizado
    lam = 0.20
    def vy(y, x):
        return -0.92 * np.sin(2 * np.pi * y / lam) * np.exp(-((x - 0.55) / 0.42) ** 2)

    for s, cor in [(-1, AMBAR), (1, CIANO)]:
        for off in np.linspace(-0.045, 0.045, 11):
            y = s * 0.10 + off
            xs, ys = [0.20], [y]
            for x in np.linspace(0.20, 0.98, 650)[1:]:
                y = y + (0.78 / 650) * vy(y, x)
                if abs(y) > 0.50:
                    break
                xs.append(x)
                ys.append(y)
            ax.plot(xs, ys, color=cor, lw=0.9, alpha=0.78)

    # intensidade no anteparo
    y = np.linspace(-0.5, 0.5, 2000)
    I = (0.08 + 0.92 * np.cos(2 * np.pi * y / lam) ** 2) * np.exp(-(y / 0.42) ** 2)
    I = I / I.max()
    axi.fill_betweenx(y, 0, I, color=CIANO, alpha=0.22)
    axi.plot(I, y, color=CIANO, lw=2)
    axi.set_ylim(-0.52, 0.52)
    axi.set_xlim(0, 1.05)
    axi.set_xticks([])
    axi.set_yticks([])
    axi.set_facecolor(PAINEL)
    for s in axi.spines.values():
        s.set_color("#22304A")
    axi.set_title("intensidade", color=SUAVE, fontsize=11, pad=8)
    axi.text(0.5, -0.50, "anteparo", color=SUAVE, fontsize=10, ha="center")

    # franjas
    for k in range(-2, 3):
        ax.axhline(k * lam, color=CIANO, lw=0.5, alpha=0.12, ls=":")

    _titulo(fig, "A onda piloto em duas fendas",
            "trajetórias didáticas guiadas por um campo de fase; o padrão de franjas está à direita")
    fig.text(0.02, 0.02, "Modelo estilizado para sala de aula — não é uma integração numérica da equação de Bohm.",
             color=SUAVE, fontsize=10.5)
    ax.set_xlabel("posição x", color=SUAVE, fontsize=12)
    ax.set_ylabel("posição y", color=SUAVE, fontsize=12)
    salvar(fig, "fig01_onda_piloto", svg=False)


# ---------------------------------------------------------------------------
# 3. Interferência (padrão correto)
# ---------------------------------------------------------------------------

def interferencia() -> None:
    fig, ax = plt.subplots(figsize=(11, 4.2))
    y = np.linspace(-0.5, 0.5, 4000)
    d, a, lam = 0.10, 0.03, 0.006
    theta = np.arctan(y / 1.0)
    I = (np.cos(np.pi * d * np.sin(theta) / lam) ** 2) * (
        np.sinc(np.pi * a * np.sin(theta) / lam) ** 2
    )
    ax.plot(y, I, color=CIANO, lw=2)
    ax.fill_between(y, 0, I, color=CIANO, alpha=0.18)
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("posição no anteparo", color=SUAVE)
    ax.set_ylabel("intensidade relativa", color=SUAVE)
    ax.set_title("Padrão de interferência de duas fendas", color=TEXTO,
                 fontsize=21, fontweight="bold", loc="left", pad=12)
    ax.grid(alpha=0.12)
    for s in ax.spines.values():
        s.set_color("#22304A")
    ax.text(0.01, 0.95, "curva calculada: cos²(π d senθ/λ) · sinc²(π a senθ/λ)",
            transform=ax.transAxes, color=SUAVE, fontsize=11, va="top")
    salvar(fig, "fig02_interferencia", svg=True)


# ---------------------------------------------------------------------------
# 4. Holograma / ordem implicada
# ---------------------------------------------------------------------------

def _letra_b(tam: int = 256) -> np.ndarray:
    img = Image.new("L", (tam, tam), 0)
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(tam * 0.74)
    )
    bbox = d.textbbox((0, 0), "B", font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((tam - w) / 2 - bbox[0], (tam - h) / 2 - bbox[1]), "B", fill=255, font=font)
    return np.asarray(img, dtype=float) / 255.0


def holograma() -> None:
    tam = 256
    letra = _letra_b(tam)
    F = np.fft.fftshift(np.fft.fft2(letra))
    mag = np.log1p(np.abs(F))
    yy, xx = np.mgrid[0:tam, 0:tam]
    cy = cx = tam // 2
    mask = ((xx - cx) ** 2 + (yy - cy) ** 2) < (0.06 * tam) ** 2
    rec = np.abs(np.fft.ifft2(np.fft.ifftshift(F * mask)))

    fig, axs = plt.subplots(1, 3, figsize=(12, 4.2))
    fig.patch.set_facecolor(FUNDO)
    for ax in axs:
        ax.set_facecolor(FUNDO)
        ax.axis("off")
    axs[0].imshow(letra, cmap="gray", vmin=0, vmax=1)
    axs[0].set_title("imagem original", color=TEXTO, fontsize=17)
    axs[1].imshow(mag, cmap="magma")
    axs[1].set_title("espectro de Fourier", color=TEXTO, fontsize=17)
    axs[2].imshow(rec, cmap="gray")
    axs[2].set_title(f"reconstrução com {mask.mean():.1%} dos coeficientes", color=TEXTO, fontsize=17)
    fig.suptitle("O todo em cada parte — uma analogia computacional",
                 color=TEXTO, fontsize=21, fontweight="bold", x=0.02, ha="left", y=1.02)
    fig.text(0.02, -0.02, "Cada pequeno conjunto de coeficientes carrega informação global. "
             "É uma analogia da ordem implicada, não uma holografia física.",
             color=SUAVE, fontsize=10.5)
    fig.tight_layout()
    salvar(fig, "fig03_holograma", svg=False)


# ---------------------------------------------------------------------------
# 5. Roda de diálogo
# ---------------------------------------------------------------------------

def dialogo() -> None:
    fig, ax = plt.subplots(figsize=(8.6, 8.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_aspect("equal")

    rotulos = [
        "suspender\nsuposições",
        "escutar\nsem julgar",
        "falar com\nhonestidade",
        "não buscar\nconsenso",
        "observar\no pensamento",
        "desacelerar",
        "acolher\no silêncio",
        "pergunta\ncompartilhada",
    ]
    centro = np.array([0.5, 0.5])
    raio = 0.34
    pontos = []
    for i in range(8):
        ang = -np.pi / 2 + i * 2 * np.pi / 8
        p = centro + raio * np.array([np.cos(ang), np.sin(ang)])
        pontos.append(p)

    for i, (p, rotulo) in enumerate(zip(pontos, rotulos)):
        cor = [CIANO, AMBAR, ROXO, VERDE][i % 4]
        ax.add_patch(Circle(p, 0.074, facecolor=PAINEL, edgecolor=cor, lw=1.8, alpha=0.98))
        ax.text(p[0], p[1], rotulo, ha="center", va="center", fontsize=8.9,
                color=TEXTO, linespacing=1.15)
        q = pontos[(i + 1) % 8]
        v = (q - p) / np.linalg.norm(q - p)
        inicio = p + v * 0.070
        fim = q - v * 0.070
        ax.add_patch(FancyArrowPatch(
            inicio, fim, connectionstyle="arc3,rad=-0.18",
            arrowstyle="-|>", mutation_scale=10, lw=1.1, color=cor, alpha=0.55,
        ))

    ax.add_patch(Circle(centro, 0.115, facecolor="#0B1220", edgecolor=CIANO, lw=2))
    ax.text(centro[0], centro[1] + 0.018, "diálogo", ha="center", va="center",
            fontsize=19, fontweight="bold", color=CIANO)
    ax.text(centro[0], centro[1] - 0.035, "bohminiano", ha="center", va="center",
            fontsize=11.5, color=SUAVE)

    ax.set_title("Oito gestos de uma roda de diálogo", color=TEXTO,
                 fontsize=23, fontweight="bold", pad=18)
    ax.text(0.5, 0.035, "Não é debate: é investigação coletiva das próprias suposições.",
            ha="center", color=SUAVE, fontsize=11.5)
    salvar(fig, "fig04_dialogo", svg=True)


# ---------------------------------------------------------------------------
# 6. PennyLane, Cirq e Qiskit
# ---------------------------------------------------------------------------

def _estado_bell_pl():
    import pennylane as qml

    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuito():
        qml.Hadamard(wires=0)
        qml.CNOT(wires=[0, 1])
        return qml.state()

    return circuito


def pennylane_circuito():
    import pennylane as qml

    circuito = _estado_bell_pl()
    fig, ax = qml.draw_mpl(circuito, style="black_white")()
    fig.set_facecolor(FUNDO)
    for a in fig.axes:
        a.set_facecolor(FUNDO)
        for line in a.get_lines():
            line.set_color(CIANO)
        for t in a.texts:
            if t.get_text().strip().isdigit():
                t.set_color(TEXTO)
    fig.suptitle("PennyLane · estado de Bell", color=TEXTO, fontsize=19,
                 fontweight="bold", x=0.02, ha="left", y=1.02)
    fig.text(0.02, -0.02, "H(0) + CNOT(0,1) · default.qubit", color=SUAVE, fontsize=10.5)
    salvar(fig, "fig05_pennylane", svg=True)


def cirq_circuito():
    import cirq

    q0, q1 = cirq.LineQubit.range(2)
    circuito = cirq.Circuit(
        cirq.H(q0),
        cirq.CNOT(q0, q1),
        cirq.measure(q0, q1, key="m"),
    )
    texto = str(circuito)
    fig, ax = plt.subplots(figsize=(8.4, 2.4))
    ax.axis("off")
    ax.text(0.01, 0.5, texto, family="DejaVu Sans Mono", fontsize=16,
            color=TEXTO, va="center")
    fig.suptitle("Cirq · estado de Bell", color=TEXTO, fontsize=15,
                 fontweight="bold", x=0.02, ha="left", y=1.05)
    fig.text(0.02, -0.04, "H(q0) + CNOT(q0,q1) + medida", color=SUAVE, fontsize=10.5)
    salvar(fig, "fig06_cirq", svg=True)


def qiskit_circuito():
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    style = {
        "backgroundcolor": FUNDO,
        "textcolor": TEXTO,
        "linecolor": CIANO,
        "gatefacecolor": "#1E293B",
        "gatetextcolor": TEXTO,
        "barrierfacecolor": "#1E293B",
        "subtextcolor": SUAVE,
    }
    fig = qc.draw("mpl", style=style)
    fig.set_facecolor(FUNDO)
    fig.suptitle("Qiskit · estado de Bell", color=TEXTO, fontsize=19,
                 fontweight="bold", x=0.02, ha="left", y=1.02)
    fig.text(0.02, -0.02, "qc.h(0); qc.cx(0,1) · Statevector", color=SUAVE, fontsize=10.5)
    salvar(fig, "fig07_qiskit", svg=True)


def tres_frameworks() -> None:
    caminhos = [
        FIG / "fig05_pennylane.png",
        FIG / "fig06_cirq.png",
        FIG / "fig07_qiskit.png",
    ]
    titulos = ["PennyLane", "Cirq", "Qiskit"]
    largura = 1600
    margem = 60
    altura_painel = 430
    altura = 140 + len(caminhos) * (altura_painel + 100) + 40

    canvas = Image.new("RGB", (largura, altura), FUNDO)
    draw = ImageDraw.Draw(canvas)
    fonte = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42
    )
    fonte_sub = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22
    )
    draw.text((margem, 30), "Três linguagens, um mesmo estado",
              font=fonte, fill="#E8F0FF")
    draw.text((margem, 82), "o mesmo circuito de Bell desenhado por três bibliotecas",
              font=fonte_sub, fill="#94A3B8")

    y = 140
    for caminho, titulo, cor in zip(caminhos, titulos, [CIANO, AMBAR, ROXO]):
        img = Image.open(caminho).convert("RGB")
        img.thumbnail((largura - 2 * margem, altura_painel))
        x = margem + (largura - 2 * margem - img.width) // 2
        canvas.paste(img, (x, y + 50))
        draw.rectangle([margem, y + 40, largura - margem, y + 50 + altura_painel],
                       outline=cor, width=2)
        draw.text((margem + 16, y), titulo, font=fonte, fill=cor)
        y += altura_painel + 100

    canvas.save(FIG / "fig08_tres_frameworks.png")
    print("  ✓ fig08_tres_frameworks")


# ---------------------------------------------------------------------------
# 7. Probabilidades e emaranhamento
# ---------------------------------------------------------------------------

def probabilidades() -> None:
    import cirq
    import pennylane as qml
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector

    # PennyLane: probabilidades exatas
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuito_pl():
        qml.Hadamard(wires=0)
        qml.CNOT(wires=[0, 1])
        return qml.probs(wires=[0, 1])

    p_pl = np.asarray(circuito_pl())

    # Cirq: 2000 medições
    q0, q1 = cirq.LineQubit.range(2)
    c = cirq.Circuit(cirq.H(q0), cirq.CNOT(q0, q1), cirq.measure(q0, q1, key="m"))
    res = cirq.Simulator().run(c, repetitions=2000)
    medidas = res.measurements["m"]
    p_cirq = np.zeros(4)
    for a, b in medidas:
        p_cirq[2 * int(a) + int(b)] += 1
    p_cirq /= p_cirq.sum()

    # Qiskit: amostragem do Statevector
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    contagens = Statevector(qc).sample_counts(2000, qargs=[0, 1])
    p_qiskit = np.zeros(4)
    for chave, valor in contagens.items():
        p_qiskit[int(str(chave), 2)] = valor
    p_qiskit /= p_qiskit.sum()

    rotulos = ["|00⟩", "|01⟩", "|10⟩", "|11⟩"]
    x = np.arange(4)
    larg = 0.26
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.bar(x - larg, p_pl, larg, label="PennyLane (exato)", color=CIANO)
    ax.bar(x, p_cirq, larg, label="Cirq (2000 tiros)", color=AMBAR)
    ax.bar(x + larg, p_qiskit, larg, label="Qiskit (2000 tiros)", color=ROXO)
    ax.axhline(0.5, color=SUAVE, lw=1, ls="--", alpha=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(rotulos)
    ax.set_ylim(0, 0.62)
    ax.set_ylabel("probabilidade / frequência")
    ax.set_title("Mesmo estado, três motores", color=TEXTO, fontsize=21,
                 fontweight="bold", loc="left", pad=12)
    ax.legend(frameon=False, labelcolor=TEXTO, fontsize=11, loc="upper right")
    ax.grid(axis="y", alpha=0.12)
    for s in ax.spines.values():
        s.set_color("#22304A")
    ax.text(0.01, 0.92, "os dois picos esperados: |00⟩ e |11⟩ com 50% cada",
            transform=ax.transAxes, color=SUAVE, fontsize=11, va="top")
    salvar(fig, "fig09_probabilidades", svg=True)


def bloch() -> None:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
    from qiskit.visualization import plot_bloch_multivector

    qc = QuantumCircuit(1)
    qc.h(0)
    fig = plot_bloch_multivector(Statevector(qc))
    fig.patch.set_facecolor(FUNDO)
    for ax in fig.axes:
        ax.set_facecolor(FUNDO)
        ax.set_title("")
        for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
            pane.set_facecolor((0, 0, 0, 0))
            pane.set_edgecolor("#22304A")
        ax.tick_params(colors=TEXTO)
        for t in ax.texts:
            t.set_color(TEXTO)
        for label in (ax.xaxis.label, ax.yaxis.label, ax.zaxis.label):
            label.set_color(TEXTO)
        for line in ax.get_lines():
            line.set_color(CIANO)
    fig.suptitle("Qiskit · esfera de Bloch de H|0⟩", color=TEXTO, fontsize=20,
                 fontweight="bold", x=0.02, ha="left", y=1.02)
    salvar(fig, "fig10_bloch", svg=False)


def emaranhamento() -> None:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    contagens = Statevector(qc).sample_counts(4000, qargs=[0, 1])
    matriz = np.zeros((2, 2))
    for chave, valor in contagens.items():
        s = str(chave)
        matriz[int(s[0]), int(s[1])] = valor
    matriz /= matriz.sum()

    fig, ax = plt.subplots(figsize=(5.8, 5.0))
    im = ax.imshow(matriz, cmap="magma", vmin=0, vmax=0.55)
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Bob 0", "Bob 1"])
    ax.set_yticklabels(["Alice 0", "Alice 1"])
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{matriz[i, j]:.1%}", ha="center", va="center",
                    color=TEXTO if matriz[i, j] < 0.3 else "#05070B",
                    fontsize=21, fontweight="bold")
    ax.set_title("Correlações do estado de Bell", color=TEXTO,
                 fontsize=20, fontweight="bold", pad=12)
    ax.text(0.5, -0.18, "Qiskit · 4000 amostras · só |00⟩ e |11⟩ aparecem",
            transform=ax.transAxes, ha="center", color=SUAVE, fontsize=11)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(colors=TEXTO)
    cbar.outline.set_edgecolor("#22304A")
    salvar(fig, "fig11_emaranhamento", svg=False)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Gerando ilustrações Bohm/black…")
    capa()
    onda_piloto()
    interferencia()
    holograma()
    dialogo()
    pennylane_circuito()
    cirq_circuito()
    qiskit_circuito()
    tres_frameworks()
    probabilidades()
    bloch()
    emaranhamento()
    print(f"Pronto: {FIG}")


if __name__ == "__main__":
    main()