#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o notebook de laboratório da edição Bohm/black."""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "notebooks" / "AULA_BOHM_LABORATORIO.ipynb"

CELULAS: list[tuple[str, str]] = []


def md(texto: str) -> None:
    CELULAS.append(("md", texto.strip("\n")))


def code(texto: str) -> None:
    CELULAS.append(("code", texto.strip("\n")))


md(r"""
# 🌊 Bohm na Escola — Laboratório Black
### Onda piloto, diálogo e três bibliotecas: PennyLane · Cirq · Qiskit

**Público:** 9º ano do Ensino Fundamental e Ensino Médio.
**Duração:** 100 minutos (ou 2 × 50 min).
**Design:** black — fundo escuro, alto contraste, figuras geradas por código.

> **Antes de rodar.** Este notebook usa três bibliotecas externas. No Google
> Colab, execute uma vez:
> ```bash
> !pip install -q pennylane qiskit cirq pylatexenc
> ```
> Depois, execute as células em ordem. Se alguma biblioteca faltar, a primeira
> célula avisa e interrompe com uma mensagem clara.

## O que você vai fazer

- [ ] Criar o estado de Bell em **PennyLane**, **Cirq** e **Qiskit**.
- [ ] Comparar as probabilidades e as convenções de cada biblioteca.
- [ ] Ver a esfera de Bloch e a matriz de correlações.
- [ ] Construir um modelo didático de **onda piloto** em duas fendas.
- [ ] Construir uma **analogia computacional** da ordem implicada.
- [ ] Rodar uma **roda de diálogo** bohminiana e registrar suposições.
- [ ] Montar um projeto final com pergunta, experimento, evidência e limite.

> **Nota de honestidade.** Bohm é uma interpretação entre várias. As três
> bibliotecas calculam previsões; nenhuma delas prova que a onda piloto é a
> descrição correta do mundo. O valor está em comparar modelos e declarar limites.
""")

md(r"""
---
## ⚙️ Prática 0 — Ambiente

Esta célula confere as versões e define o estilo visual black. Se faltar alguma
biblioteca, siga a instrução impressa e reinicie o ambiente.
""")

code(r"""
import sys
import numpy as np
import matplotlib.pyplot as plt

try:
    import pennylane as qml
    import cirq
    import qiskit
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
except ImportError as exc:
    print("Biblioteca ausente:", exc)
    print("No Colab, rode: !pip install -q pennylane qiskit cirq pylatexenc")
    raise

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

print("Python:", sys.version.split()[0])
print("PennyLane:", qml.__version__)
print("Cirq:", cirq.__version__)
print("Qiskit:", qiskit.__version__)
print("✅ PRÁTICA 0 — ambiente pronto")
""")

md(r"""
---
# Prática 1 — PennyLane
### O circuito como função

PennyLane descreve circuitos como funções decoradas com `@qml.qnode`. A medição
é o retorno da função. Vamos criar o estado de Bell e ver as probabilidades.
""")

code(r"""
dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def bell_pl():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.probs(wires=[0, 1])

p_pl = np.asarray(bell_pl())
print("Probabilidades [|00>, |01>, |10>, |11>]:", np.round(p_pl, 3))

fig, ax = qml.draw_mpl(bell_pl, style="black_white")()
fig.set_facecolor(FUNDO)
for a in fig.axes:
    a.set_facecolor(FUNDO)
    for line in a.get_lines():
        line.set_color(CIANO)
    for t in a.texts:
        if t.get_text().strip().isdigit():
            t.set_color(TEXTO)
plt.show()

assert np.allclose(p_pl, [0.5, 0.0, 0.0, 0.5])
print("✅ PRÁTICA 1 — PennyLane: 50% para 00 e 50% para 11")
""")

md(r"""
---
# Prática 2 — Cirq
### A linha de qubits e a medição

Cirq organiza o circuito em linhas. Vamos criar o mesmo Bell, medir 2000 vezes e
comparar as frequências com a previsão de PennyLane.
""")

code(r"""
q0, q1 = cirq.LineQubit.range(2)
circuito = cirq.Circuit(
    cirq.H(q0),
    cirq.CNOT(q0, q1),
    cirq.measure(q0, q1, key="m"),
)
print(circuito)

resultado = cirq.Simulator().run(circuito, repetitions=2000)
medidas = resultado.measurements["m"]
contagens = {}
for a, b in medidas:
    chave = f"{int(a)}{int(b)}"
    contagens[chave] = contagens.get(chave, 0) + 1
print("Contagens:", contagens)

assert contagens.get("01", 0) == 0
assert contagens.get("10", 0) == 0
assert contagens.get("00", 0) + contagens.get("11", 0) == 2000
print("✅ PRÁTICA 2 — Cirq: só 00 e 11 aparecem")
""")

md(r"""
---
# Prática 3 — Qiskit
### Estado, circuito e esfera de Bloch

Qiskit oferece `Statevector` para inspecionar amplitudes e `draw("mpl")` para o
desenho. Vamos ver o estado de Bell e a esfera de Bloch de um único qubit.
""")

code(r"""
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

estado = Statevector(qc)
p_qiskit = np.asarray(estado.probabilities())
print("Amplitudes:", np.round(estado.data, 3))
print("Probabilidades:", np.round(p_qiskit, 3))
print("Amostras:", estado.sample_counts(2000, qargs=[0, 1]))

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
plt.show()

from qiskit.visualization import plot_bloch_multivector
qc1 = QuantumCircuit(1)
qc1.h(0)
figb = plot_bloch_multivector(Statevector(qc1))
figb.patch.set_facecolor(FUNDO)
for axb in figb.axes:
    axb.set_facecolor(FUNDO)
    axb.set_title("")
    for pane in (axb.xaxis.pane, axb.yaxis.pane, axb.zaxis.pane):
        pane.set_facecolor((0, 0, 0, 0))
        pane.set_edgecolor("#22304A")
    axb.tick_params(colors=TEXTO)
    for t in axb.texts:
        t.set_color(TEXTO)
    for line in axb.get_lines():
        line.set_color(CIANO)
plt.show()

assert np.allclose(p_qiskit, [0.5, 0.0, 0.0, 0.5])
print("✅ PRÁTICA 3 — Qiskit: estado e esfera de Bloch")
""")

md(r"""
---
# Prática 4 — Três linguagens, uma tabela

As três bibliotecas concordam? Vamos calcular as probabilidades e as frequências
lado a lado. Atenção à convenção de ordem dos qubits.
""")

code(r"""
# PennyLane: exato
p_pl = np.asarray(bell_pl())

# Cirq: frequências
p_cirq = np.zeros(4)
for a, b in medidas:
    p_cirq[2 * int(a) + int(b)] += 1
p_cirq /= p_cirq.sum()

# Qiskit: frequências
p_qk = np.zeros(4)
for chave, valor in estado.sample_counts(2000, qargs=[0, 1]).items():
    p_qk[int(str(chave), 2)] = valor
p_qk /= p_qk.sum()

rotulos = ["|00⟩", "|01⟩", "|10⟩", "|11⟩"]
print(f"{'estado':>6} | {'PennyLane':>10} | {'Cirq':>8} | {'Qiskit':>8}")
for i, r in enumerate(rotulos):
    print(f"{r:>6} | {p_pl[i]:10.3f} | {p_cirq[i]:8.3f} | {p_qk[i]:8.3f}")

assert abs(p_pl.sum() - 1) < 1e-9
assert abs(p_cirq.sum() - 1) < 1e-9
assert abs(p_qk.sum() - 1) < 1e-9
print("✅ PRÁTICA 4 — as três bibliotecas concordam dentro da flutuação")
""")

md(r"""
---
# Prática 5 — Onda piloto em duas fendas

Este é um **modelo didático**: um campo de velocidade estilizado guia trajetórias
para as franjas claras. Não é uma integração numérica da equação de Bohm.
""")

code(r"""
def vy(y, x):
    lam = 0.20
    return -0.92 * np.sin(2 * np.pi * y / lam) * np.exp(-((x - 0.55) / 0.42) ** 2)

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.set_xlim(0, 1)
ax.set_ylim(-0.52, 0.52)
ax.axvline(0.18, color="#94A3B8", lw=6)
for s, cor in [(-1, AMBAR), (1, CIANO)]:
    for off in np.linspace(-0.045, 0.045, 9):
        y = s * 0.10 + off
        xs, ys = [0.20], [y]
        for x in np.linspace(0.20, 0.98, 600)[1:]:
            y = y + (0.78 / 600) * vy(y, x)
            if abs(y) > 0.50:
                break
            xs.append(x)
            ys.append(y)
        ax.plot(xs, ys, color=cor, lw=0.9, alpha=0.8)
ax.set_title("Trajetórias guiadas por um campo de fase", color=TEXTO, fontsize=14, loc="left")
ax.set_xlabel("posição x", color=SUAVE)
ax.set_ylabel("posição y", color=SUAVE)
ax.text(0.02, 0.04, "modelo estilizado — não é uma solução da equação de Bohm",
        transform=ax.transAxes, color=SUAVE, fontsize=9)
plt.show()

assert 0.0 <= 0.20 <= 1.0
print("✅ PRÁTICA 5 — modelo de onda piloto executado")
""")

md(r"""
---
# Prática 6 — Holograma e ordem implicada

A transformada de Fourier distribui a informação. Vamos manter apenas 1,1% dos
coeficientes e reconstruir uma versão borrada do todo. É uma **analogia** da
ordem implicada, não uma holografia física.
""")

code(r"""
from PIL import Image, ImageDraw, ImageFont
from matplotlib.font_manager import findfont, FontProperties

tam = 256
img = Image.new("L", (tam, tam), 0)
draw = ImageDraw.Draw(img)
fonte_path = findfont(FontProperties(family="DejaVu Sans"))
fonte = ImageFont.truetype(fonte_path, int(tam * 0.74))
bbox = draw.textbbox((0, 0), "B", font=fonte)
w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
draw.text(((tam - w) / 2 - bbox[0], (tam - h) / 2 - bbox[1]), "B", fill=255, font=fonte)
letra = np.asarray(img, dtype=float) / 255.0

F = np.fft.fftshift(np.fft.fft2(letra))
yy, xx = np.mgrid[0:tam, 0:tam]
mask = ((xx - 128) ** 2 + (yy - 128) ** 2) < (0.06 * tam) ** 2
rec = np.abs(np.fft.ifft2(np.fft.ifftshift(F * mask)))

fig, axs = plt.subplots(1, 3, figsize=(11, 3.6))
for a in axs:
    a.axis("off")
axs[0].imshow(letra, cmap="gray")
axs[0].set_title("original", color=TEXTO)
axs[1].imshow(np.log1p(np.abs(F)), cmap="magma")
axs[1].set_title("espectro", color=TEXTO)
axs[2].imshow(rec, cmap="gray")
axs[2].set_title(f"reconstrução {mask.mean():.1%}", color=TEXTO)
plt.show()

assert rec.shape == (tam, tam)
assert mask.mean() < 0.05
print("✅ PRÁTICA 6 — o todo em 1,1% dos coeficientes")
""")

md(r"""
---
# Prática 7 — Diálogo como experimento

A roda de diálogo não usa código; usa presença. Esta célula apenas imprime o
roteiro e os tempos. O “dado” é qualitativo: o que muda na pergunta e nas
suposições.
""")

code(r"""
def roteiro_dialogo(pergunta: str):
    blocos = [
        ("Roda inicial", 2, "uma palavra por pessoa"),
        ("Pergunta", 1, pergunta),
        ("Rodada 1", 4, "uma fala por pessoa, sem interrupção"),
        ("Silêncio", 1, "escreva uma suposição"),
        ("Rodada 2", 5, "responda ao que ouviu, não à pessoa"),
        ("Fechamento", 2, "o que eu levo desta conversa?"),
    ]
    print("ROTEIRO — 15 min")
    for nome, minutos, instrucao in blocos:
        print(f"[{minutos:2d} min] {nome}: {instrucao}")
    print("\nPergunta central:", pergunta)

roteiro_dialogo("O que acontece entre duas medições?")
print("✅ PRÁTICA 7 — roteiro de diálogo pronto")
""")

md(r"""
---
# Prática 8 — Projeto final

Complete o cartão abaixo. Ele precisa ter **pergunta, suposição, experimento,
evidência e limite**. Sem o limite, o projeto não é aprovado.
""")

code(r"""
projeto = {
    "pergunta": "Medir na base X muda a correlação do estado de Bell?",
    "suposicao": "A correlação perfeita depende da base escolhida.",
    "experimento": "Circuito de Bell em Qiskit, medido em Z e em X.",
    "evidencia": "Matriz de correlações nas duas bases.",
    "limite": "O experimento não testa a interpretação de Bohm; testa a previsão quântica.",
}

for campo, valor in projeto.items():
    print(f"{campo.upper()}: {valor}")

assert all(isinstance(v, str) and len(v) >= 15 for v in projeto.values())
print("✅ PRÁTICA 8 — cartão de projeto completo")
""")

md(r"""
---
## 🧑‍🏫 Para o professor

- As práticas 1–4 podem ser feitas em duplas; as práticas 5–6, em grupos.
- A prática 7 exige tempo protegido e um observador.
- A prática 8 é o esqueleto do projeto; a rubrica está no livro, cap. 14.
- Se a rede falhar, use as figuras já geradas no livro e faça as práticas 5–7
  desplugadas.

### Limites

- O modelo de onda piloto é **estilizado**; não é uma solução numérica.
- O holograma é uma **analogia**; não é uma teoria física.
- Bohm é uma **interpretação**; não é consenso.
- As três bibliotecas são **simuladores**; não há hardware quântico real aqui.

### Referências

BOHM, D. *Wholeness and the Implicate Order*. London: Routledge, 1980.
BOHM, D. *On Dialogue*. London: Routledge, 1996.
NIELSEN, M. A.; CHUANG, I. L. *Quantum Computation and Quantum Information*.
Cambridge: Cambridge University Press, 2000.
PENNYLANE, CIRQ, QISKIT: documentação oficial.
""")


def construir() -> None:
    nb = nbf.v4.new_notebook()
    nb["cells"] = [
        nbf.v4.new_markdown_cell(t) if k == "md" else nbf.v4.new_code_cell(t)
        for k, t in CELULAS
    ]
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10"},
        "colab": {"provenance": [], "toc_visible": True},
    }
    nb["nbformat"] = 4
    nb["nbformat_minor"] = 5
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, str(SAIDA))
    print(f"Notebook: {SAIDA}")
    print(f"Células: {len(nb['cells'])} "
          f"({sum(c['cell_type']=='markdown' for c in nb['cells'])} markdown, "
          f"{sum(c['cell_type']=='code' for c in nb['cells'])} código)")


if __name__ == "__main__":
    construir()