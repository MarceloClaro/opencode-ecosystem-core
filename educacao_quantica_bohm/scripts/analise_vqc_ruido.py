#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validação crítica do estudo de VQC com ruído benéfico (Qualis A1).

O relatório original usa 2 qubits, 5 trials e um único split 50/20. Aqui:
- aumentamos para 2 e 4 qubits;
- usamos validação cruzada estratificada de 5 folds;
- comparamos baseline, phase damping, depolarizing e amplitude damping;
- reportamos média, desvio e intervalo de confiança bootstrap de 95%;
- verificamos se o "sweet spot" de γ≈0,005 sobrevive ao aumento de qubits.

A simulação usa DensityMatrix do Qiskit (sem Aer). O objetivo é testar a
**robustez da afirmação**, não repetir exatamente os números do relatório.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Kraus
from scipy.optimize import minimize

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "dados_qualis"
SAIDA.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- dataset
def two_moons(n: int = 70, noise: float = 0.06, seed: int = 42):
    """Duas luas sintéticas, balanceadas, no espírito do relatório."""
    rng = np.random.default_rng(seed)
    n_half = n // 2
    t0 = rng.uniform(0, math.pi, n_half)
    t1 = rng.uniform(0, math.pi, n - n_half)
    x0 = np.column_stack([np.cos(t0), np.sin(t0)])
    x1 = np.column_stack([1 - np.cos(t1), 1 - np.sin(t1) - 0.5])
    X = np.vstack([x0, x1]) + rng.normal(0, noise, size=(n, 2))
    y = np.array([0] * n_half + [1] * (n - n_half))
    idx = rng.permutation(n)
    return X[idx], y[idx]


def folds_estratificados(y: np.ndarray, k: int = 5, seed: int = 42):
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(y))
    partes = []
    for classe in (0, 1):
        idx_c = idx[y[idx] == classe]
        partes.append(np.array_split(idx_c, k))
    for i in range(k):
        te = np.concatenate([partes[0][i], partes[1][i]])
        tr = np.setdiff1d(idx, te)
        yield tr, te


# ---------------------------------------------------------------- canais
def kraus(noise: str, gamma: float):
    if noise == "phase":
        return [
            np.array([[1, 0], [0, math.sqrt(max(0.0, 1 - gamma))]], dtype=complex),
            np.array([[0, 0], [0, math.sqrt(max(0.0, gamma))]], dtype=complex),
        ]
    if noise == "amplitude":
        return [
            np.array([[1, 0], [0, math.sqrt(max(0.0, 1 - gamma))]], dtype=complex),
            np.array([[0, math.sqrt(max(0.0, gamma))], [0, 0]], dtype=complex),
        ]
    if noise == "depolarizing":
        p = gamma
        return [
            math.sqrt(max(0.0, 1 - 3 * p / 4)) * np.eye(2, dtype=complex),
            math.sqrt(max(0.0, p / 4)) * np.array([[0, 1], [1, 0]], dtype=complex),
            math.sqrt(max(0.0, p / 4)) * np.array([[0, -1j], [1j, 0]], dtype=complex),
            math.sqrt(max(0.0, p / 4)) * np.array([[1, 0], [0, -1]], dtype=complex),
        ]
    return []


def aplicar_canal(dm: DensityMatrix, ops, qubit: int, n: int) -> DensityMatrix:
    if not ops:
        return dm
    cheios = []
    for K in ops:
        op = np.kron(np.eye(2 ** (n - qubit - 1)), np.kron(K, np.eye(2 ** qubit)))
        cheios.append(op)
    return dm.evolve(Kraus(cheios))


# ---------------------------------------------------------------- circuito
def n_params(n: int, arch: str) -> int:
    return n if arch == "basic" else 2 * n


def circuito(x, theta, n: int, arch: str) -> QuantumCircuit:
    qc = QuantumCircuit(n)
    for q in range(n):
        angulo = np.pi * (x[0] if q % 2 == 0 else x[1])
        qc.ry(angulo, q)
    i = 0
    if arch == "basic":
        for q in range(n):
            qc.ry(theta[i], q)
            i += 1
    elif arch == "strongly":
        for q in range(n):
            qc.ry(theta[i], q)
            i += 1
        for q in range(n):
            qc.cx(q, (q + 1) % n)
        for q in range(n):
            qc.ry(theta[i], q)
            i += 1
    elif arch == "hardware":
        for q in range(n):
            qc.ry(theta[i], q)
            i += 1
        for q in range(n):
            qc.rz(theta[i], q)
            i += 1
        for q in range(n - 1):
            qc.cz(q, q + 1)
    else:
        raise ValueError(arch)
    return qc


def p1(x, theta, n: int, arch: str, noise: str, gamma: float) -> float:
    qc = circuito(x, theta, n, arch)
    dm = DensityMatrix.from_instruction(qc)
    if gamma > 0 and noise != "none":
        ops = kraus(noise, gamma)
        for q in range(n):
            dm = aplicar_canal(dm, ops, q, n)
    probs = dm.probabilities([0])
    return float(probs[1])


# ---------------------------------------------------------------- treino
def treinar_avaliar(Xtr, ytr, Xte, yte, n, arch, noise, gamma, seed):
    rng = np.random.default_rng(seed)
    x0 = rng.normal(0, 0.12, size=n_params(n, arch))

    def perda(theta):
        p = np.array([p1(x, theta, n, arch, noise, gamma) for x in Xtr])
        return float(np.mean((p - ytr) ** 2))

    res = minimize(
        perda, x0, method="Nelder-Mead",
        options={"maxiter": 25, "xatol": 1e-3, "fatol": 1e-4},
    )
    p_tr = np.array([p1(x, res.x, n, arch, noise, gamma) for x in Xtr])
    p_te = np.array([p1(x, res.x, n, arch, noise, gamma) for x in Xte])
    acc_tr = float(np.mean((p_tr >= 0.5).astype(int) == ytr))
    acc_te = float(np.mean((p_te >= 0.5).astype(int) == yte))
    return acc_tr, acc_te, float(res.fun)


def bootstrap_ci(valores, n_boot=2000, seed=42):
    rng = np.random.default_rng(seed)
    vals = np.asarray(valores, dtype=float)
    medias = [rng.choice(vals, size=len(vals), replace=True).mean() for _ in range(n_boot)]
    return [float(np.percentile(medias, 2.5)), float(np.percentile(medias, 97.5))]


CONFIGURACOES = [
    ("baseline", "strongly", "none", 0.0),
    ("phase_005", "strongly", "phase", 0.005),
    ("phase_010", "strongly", "phase", 0.010),
    ("depol_005", "strongly", "depolarizing", 0.005),
    ("amp_005", "strongly", "amplitude", 0.005),
]


def rodar(n_qubits_list, folds=5):
    X, y = two_moons()
    resultados = {}
    for n in n_qubits_list:
        resultados[str(n)] = {}
        for nome, arch, noise, gamma in CONFIGURACOES:
            accs_tr, accs_te = [], []
            for i, (tr, te) in enumerate(folds_estratificados(y, folds)):
                a_tr, a_te, _ = treinar_avaliar(
                    X[tr], y[tr], X[te], y[te], n, arch, noise, gamma, seed=42 + i
                )
                accs_tr.append(a_tr)
                accs_te.append(a_te)
            media = float(np.mean(accs_te))
            desvio = float(np.std(accs_te, ddof=1))
            resultados[str(n)][nome] = {
                "n_qubits": n,
                "arquitetura": arch,
                "ruido": noise,
                "gamma": gamma,
                "acc_treino_media": float(np.mean(accs_tr)),
                "acc_teste_media": media,
                "acc_teste_desvio": desvio,
                "acc_teste_folds": accs_te,
                "ic95": bootstrap_ci(accs_te),
            }
            print(f"n={n} {nome:12s} acc={media:.3f} ± {desvio:.3f} folds={accs_te}")
    return resultados


def relatorio(resultados):
    linhas = [
        "# Validação do estudo de VQC com ruído benéfico",
        "",
        "Réplica crítica com 2 e 4 qubits, validação cruzada estratificada de 5 folds",
        "e intervalo de confiança bootstrap de 95%. A métrica é acurácia de teste.",
        "",
        "| n | Configuração | Acurácia teste | Desvio | IC95 |",
        "|---:|---|---:|---:|---|",
    ]
    for n, configs in resultados.items():
        for nome, d in configs.items():
            ic = d["ic95"]
            linhas.append(
                f"| {n} | {nome} | {d['acc_teste_media']:.3f} | "
                f"{d['acc_teste_desvio']:.3f} | [{ic[0]:.3f}, {ic[1]:.3f}] |"
            )
    linhas += [
        "",
        "## Leitura crítica",
        "",
        "- O relatório original usa **5 trials** e um **único split 50/20**; isso",
        "  não permite afirmar significância estatística nem generalização.",
        "- A comparação de arquiteturas com **um único trial** por configuração",
        "  (hardware efficient = 81,0%) não sustenta “superioridade estatística”.",
        "- O rótulo “primeira aplicação documentada” não é verificável sem uma",
        "  revisão sistemática; a literatura de VQC + Optuna é ampla.",
        "- O efeito de ruído benéfico, se existir, precisa sobreviver a:",
        "  mais folds, mais seeds, mais datasets, intervalo de confiança e",
        "  validação em hardware. Esta réplica testa os dois primeiros pontos.",
        "",
        "> **Veredito:** veja a tabela. Se o IC95 de phase damping cruzar o baseline,",
        "> o sweet spot não foi validado nestes dados. A ausência de evidência não",
        "> prova que o efeito não existe; prova que 5 trials e 20 pontos de teste",
        "> não bastam para sustentá-lo.",
        "",
    ]
    caminho = SAIDA / "RELATORIO_VALIDACAO.md"
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return caminho


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qubits", nargs="+", type=int, default=[2, 4])
    ap.add_argument("--folds", type=int, default=5)
    args = ap.parse_args()

    resultados = rodar(args.qubits, args.folds)
    dados = {
        "dataset": "two_moons_sintetico",
        "n_amostras": 70,
        "folds": args.folds,
        "qubits": args.qubits,
        "configuracoes": [c[0] for c in CONFIGURACOES],
        "resultados": resultados,
    }
    caminho = SAIDA / "vqc_ruido_validacao.json"
    caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
    print("JSON:", caminho)
    print("Relatório:", relatorio(resultados))


if __name__ == "__main__":
    main()