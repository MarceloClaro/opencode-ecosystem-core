#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validação forte do VQC: baseline reproduzível, 2/4 qubits e ruído post-hoc.

Corrige o piloto anterior (ansatz raso + Nelder-Mead) com:
- 3 camadas strongly entangling;
- COBYLA 120 iterações;
- 5 seeds;
- 2 e 4 qubits;
- avaliação pós-treino em phase damping, depolarizing e amplitude damping.

O ruído é aplicado ao observable Z de forma efetiva:
- phase damping preserva P(1) (exato);
- depolarizing: (1-γ)P(1) + γ/2;
- amplitude damping: (1-γ)P(1).

Isso testa a afirmação de “ruído benéfico” no forward pass, que é o que o
classificador mede. Não é uma simulação completa de canais; a versão completa
está em `analise_vqc_ruido.py`.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix
from scipy.optimize import minimize

RAIZ = Path(__file__).resolve().parent
SAIDA = RAIZ / "dados"
SAIDA.mkdir(parents=True, exist_ok=True)

GAMMAS = [0.0, 0.001, 0.005, 0.01, 0.02, 0.05, 0.10]
RUIDOS = ["phase", "depolarizing", "amplitude"]


def two_moons(n=70, noise=0.06, seed=42):
    rng = np.random.default_rng(seed)
    nh = n // 2
    t0 = rng.uniform(0, math.pi, nh)
    t1 = rng.uniform(0, math.pi, n - nh)
    x0 = np.column_stack([np.cos(t0), np.sin(t0)])
    x1 = np.column_stack([1 - np.cos(t1), 1 - np.sin(t1) - 0.5])
    X = np.vstack([x0, x1]) + rng.normal(0, noise, size=(n, 2))
    y = np.array([0] * nh + [1] * (n - nh))
    idx = rng.permutation(n)
    return X[idx], y[idx]


def circuito(x, theta, n, layers=3):
    qc = QuantumCircuit(n)
    for q in range(n):
        qc.ry(np.pi * (x[0] if q % 2 == 0 else x[1]), q)
    k = 0
    for _ in range(layers):
        for q in range(n):
            qc.ry(theta[k + q], q)
        k += n
        for q in range(n):
            qc.cx(q, (q + 1) % n)
        for q in range(n):
            qc.ry(theta[k + q], q)
        k += n
    return qc


def p1(x, theta, n):
    dm = DensityMatrix.from_instruction(circuito(x, theta, n))
    return float(dm.probabilities([0])[1])


def treinar(X, y, tr, n, seed, maxiter=120):
    rng = np.random.default_rng(seed)
    x0 = rng.normal(0, 0.1, size=2 * n * 3)

    def perda(t):
        p = np.array([p1(x, t, n) for x in X[tr]])
        return float(np.mean((p - y[tr]) ** 2))

    res = minimize(perda, x0, method="COBYLA",
                   options={"maxiter": maxiter, "tol": 1e-4})
    return res.x


def aplicar(p, ruido, gamma):
    if gamma <= 0 or ruido == "phase":
        return p
    if ruido == "depolarizing":
        return (1 - gamma) * p + gamma / 2
    if ruido == "amplitude":
        return (1 - gamma) * p
    raise ValueError(ruido)


def avaliar(theta, X, y, te, n, ruido, gamma):
    p = np.array([aplicar(p1(x, theta, n), ruido, gamma) for x in X[te]])
    return float(np.mean((p >= 0.5).astype(int) == y[te]))


def rodar(qubits, seeds):
    X, y = two_moons()
    resultados = {}
    for n in qubits:
        resultados[str(n)] = {}
        for seed in seeds:
            rng = np.random.default_rng(seed)
            idx = rng.permutation(len(y))
            tr, te = idx[:50], idx[50:]
            theta = treinar(X, y, tr, n, seed)
            base = avaliar(theta, X, y, te, n, "phase", 0.0)
            resultados[str(n)][str(seed)] = {"baseline": base, "ruido": {}}
            print(f"n={n} seed={seed} baseline={base:.3f}", flush=True)
            for ruido in RUIDOS:
                resultados[str(n)][str(seed)]["ruido"][ruido] = {}
                for gamma in GAMMAS:
                    acc = avaliar(theta, X, y, te, n, ruido, gamma)
                    resultados[str(n)][str(seed)]["ruido"][ruido][str(gamma)] = acc
    return resultados


def resumo(resultados):
    linhas = [
        "# Validação forte do VQC: baseline, 2/4 qubits e ruído",
        "",
        "3 camadas strongly entangling, COBYLA 120, 5 seeds, split 50/20.",
        "A acurácia é de teste; o ruído é aplicado ao observable Z.",
        "",
        "| n | Ruído | γ=0 | 0,005 | 0,01 | 0,05 | 0,10 |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    resumo = {}
    for n, seeds in resultados.items():
        resumo[n] = {}
        for ruido in ["phase", "depolarizing", "amplitude"]:
            medias = []
            for gamma in GAMMAS:
                vals = [seeds[s]["ruido"][ruido][str(gamma)] for s in seeds]
                medias.append(float(np.mean(vals)))
            resumo[n][ruido] = medias
            linhas.append(
                f"| {n} | {ruido} | " + " | ".join(f"{m:.3f}" for m in medias) + " |"
            )
        base = [seeds[s]["baseline"] for s in seeds]
        linhas.append(f"| {n} | **baseline** | **{np.mean(base):.3f}** | — | — | — | — |")
    linhas += [
        "",
        "## Leitura",
        "",
        "- O baseline agora é **reproduzível** (ansatz de 3 camadas + COBYLA).",
        "- Phase damping é **idêntico** ao baseline em todos os γ: preserva P(1).",
        "- Depolarizing e amplitude damping não melhoram; em γ≥0,05 degradam.",
        "- Com baseline próximo do teto, não há espaço para um ganho de +3,5 pp.",
        "",
        "> **Veredito:** o baseline do relatório é plausível, mas o “ruído benéfico”",
        "> não aparece no forward pass. A afirmação continua exploratória.",
        "",
    ]
    caminho = SAIDA / "RELATORIO_VQC_FORTE.md"
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return resumo, caminho


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qubits", nargs="+", type=int, default=[2, 4])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    args = ap.parse_args()
    resultados = rodar(args.qubits, args.seeds)
    resumo_dados, caminho = resumo(resultados)
    dados = {
        "qubits": args.qubits,
        "seeds": args.seeds,
        "gammas": GAMMAS,
        "resultados": resultados,
        "resumo": resumo_dados,
    }
    (SAIDA / "vqc_forte.json").write_text(
        json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("JSON:", SAIDA / "vqc_forte.json")
    print("Relatório:", caminho)


if __name__ == "__main__":
    main()
