#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Catálogo de experimentos práticos para os 100 conceitos.

Cada conceito aponta para um dos 18 circuitos-base. O mesmo circuito pode
servir a vários conceitos: o que muda é a leitura pedagógica. Todos os circuitos
têm uma versão simulada (statevector + amostragem) e podem ser enviados ao
backend pelo script `scripts/experimentos_100.py`.

Métrica universal: **sobreposição de distribuições** entre simulação e backend,
`sum_b min(p_sim[b], p_real[b])`. Ela mede o quanto as distribuições se parecem;
não é fidelidade de estado nem prova de emaranhamento.
"""
from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate

XOR = [(0, 0), (0, 1), (1, 0), (1, 1)]
THETA = [1.5708, 1.5708, -1.5708, 2.819]
CHSH = [
    ("E00", 0, -np.pi / 4),
    ("E01", 0, np.pi / 4),
    ("E10", 1, -np.pi / 4),
    ("E11", 1, np.pi / 4),
]


def _p(counts: dict, chave: str) -> float:
    total = sum(int(v) for v in counts.values())
    return int(counts.get(chave, 0)) / total if total else 0.0


def _soma(counts: dict, chaves: tuple[str, ...]) -> float:
    return sum(_p(counts, c) for c in chaves)


def qc_basis0() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    qc.measure(0, 0)
    return qc


def qc_basis1() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    qc.x(0)
    qc.measure(0, 0)
    return qc


def qc_superposicao() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def qc_fase() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.z(0)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def qc_bell() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def qc_ghz4() -> QuantumCircuit:
    qc = QuantumCircuit(4, 4)
    qc.h(0)
    for alvo in (1, 2, 3):
        qc.cx(0, alvo)
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    return qc


def qc_chsh(a1: int, angulo: float) -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    if a1:
        qc.h(0)
    qc.ry(angulo, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def qcs_chsh() -> list[QuantumCircuit]:
    return [qc_chsh(a1, float(ang)) for _, a1, ang in CHSH]


def qc_qrng() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def qc_amplitude() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    qc.ry(2 * np.pi / 3, 0)
    qc.measure(0, 0)
    return qc


def qc_vqc(x: tuple[int, int]) -> QuantumCircuit:
    qc = QuantumCircuit(2, 1)
    qc.ry(np.pi * x[0], 0)
    qc.ry(np.pi * x[1], 1)
    qc.ry(THETA[0], 0)
    qc.ry(THETA[1], 1)
    qc.cx(0, 1)
    qc.ry(THETA[2], 0)
    qc.ry(THETA[3], 1)
    qc.measure(0, 0)
    return qc


def qcs_vqc() -> list[QuantumCircuit]:
    return [qc_vqc(x) for x in XOR]


def qc_interferencia2() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.h(1)
    qc.cz(0, 1)
    qc.h(0)
    qc.measure([0, 1], [0, 1])
    return qc


def qc_qft3() -> QuantumCircuit:
    qc = QuantumCircuit(3, 3)
    qc.x(2)
    qc.append(QFTGate(3), range(3))
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc


def qc_tensor01() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.measure([0, 1], [0, 1])
    return qc


def qc_ruido_phase() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.x(0)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def qc_qasm_ghz4() -> QuantumCircuit:
    # mesmo GHZ, mas construído a partir de um texto OpenQASM 2.0 no script
    return qc_ghz4()


def qcs_bloch() -> list[QuantumCircuit]:
    z = QuantumCircuit(1, 1)
    z.h(0)
    z.measure(0, 0)
    x = QuantumCircuit(1, 1)
    x.h(0)
    x.h(0)
    x.measure(0, 0)
    return [z, x]


def qc_walk3() -> QuantumCircuit:
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.h(1)
    qc.h(2)
    qc.cz(0, 1)
    qc.cz(1, 2)
    qc.h(0)
    qc.h(1)
    qc.h(2)
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc


def qc_amostragem() -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    return qc


# ---------------------------------------------------------------- leituras

def leitura_p0(cs):
    return f"P(0) = {_p(cs[0], '0'):.3f} (ideal 1,000)"


def leitura_p1(cs):
    return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 1,000)"


def leitura_superposicao(cs):
    return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 0,500)"


def leitura_fase(cs):
    return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 1,000)"


def leitura_bell(cs):
    v = _soma(cs[0], ("00", "11"))
    return f"P(00)+P(11) = {v:.3f} (ideal 1,000)"


def leitura_ghz(cs):
    v = _soma(cs[0], ("0000", "1111"))
    return f"P(0000)+P(1111) = {v:.3f} (ideal 1,000)"


def leitura_chsh(cs):
    E = []
    for c in cs:
        E.append(_p(c, "00") + _p(c, "11") - _p(c, "01") - _p(c, "10"))
    S = E[0] + E[1] + E[2] - E[3]
    return f"S = {S:.3f} (ideal 2,828)"


def leitura_qrng(cs):
    v = abs(_p(cs[0], "0") - _p(cs[0], "1"))
    return f"|P(0)-P(1)| = {v:.3f} (ideal 0,000)"


def leitura_amplitude(cs):
    return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 0,750)"


def leitura_vqc(cs):
    acertos = 0
    for c, x in zip(cs, XOR):
        y = 1 if x[0] != x[1] else 0
        pred = 1 if _p(c, "1") >= 0.5 else 0
        acertos += int(pred == y)
    return f"Acurácia = {acertos}/4"


def leitura_interferencia2(cs):
    return f"P(00) = {_p(cs[0], '00'):.3f} (ideal 0,500)"


def leitura_qft3(cs):
    return f"P(000) = {_p(cs[0], '000'):.3f} (ideal 0,125)"


def leitura_tensor01(cs):
    return f"P(01) = {_p(cs[0], '01'):.3f} (ideal 1,000)"


def leitura_ruido(cs):
    return f"P(0) = {_p(cs[0], '0'):.3f} (ideal 1,000)"


def leitura_bloch(cs):
    pz, px = _p(cs[0], "0"), _p(cs[1], "0")
    return f"⟨Z⟩ = {2*pz-1:+.3f}, ⟨X⟩ = {2*px-1:+.3f} (ideal 0, +1)"


def leitura_walk3(cs):
    return f"P(000) = {_p(cs[0], '000'):.3f} (ideal 0,250)"


def leitura_amostragem(cs):
    return f"P(1) = {_p(cs[0], '1'):.3f} (ideal 0,500)"


EXPERIMENTOS = {
    "E01": {
        "nome": "Base |0⟩",
        "descricao": "Prepara |0⟩ e mede 1024 vezes.",
        "circuitos": lambda: [qc_basis0()],
        "leitura": leitura_p0,
    },
    "E02": {
        "nome": "Base |1⟩ e leitura",
        "descricao": "Prepara |1⟩ e mede; a discrepância é erro de leitura.",
        "circuitos": lambda: [qc_basis1()],
        "leitura": leitura_p1,
    },
    "E03": {
        "nome": "Superposição H|0⟩",
        "descricao": "H cria uma superposição; a medição produz 0 ou 1.",
        "circuitos": lambda: [qc_superposicao()],
        "leitura": leitura_superposicao,
    },
    "E04": {
        "nome": "Interferência H-Z-H",
        "descricao": "A fase Z inverte a interferência: o resultado vira |1⟩.",
        "circuitos": lambda: [qc_fase()],
        "leitura": leitura_fase,
    },
    "E05": {
        "nome": "Estado de Bell",
        "descricao": "H + CNOT criam uma correlação 00/11.",
        "circuitos": lambda: [qc_bell()],
        "leitura": leitura_bell,
    },
    "E06": {
        "nome": "GHZ de 4 qubits",
        "descricao": "Quatro qubits compartilham 0000/1111.",
        "circuitos": lambda: [qc_ghz4()],
        "leitura": leitura_ghz,
    },
    "E07": {
        "nome": "CHSH",
        "descricao": "Quatro configurações medem S.",
        "circuitos": qcs_chsh,
        "leitura": leitura_chsh,
    },
    "E08": {
        "nome": "Gerador quântico de números",
        "descricao": "H + medição produzem bits aproximadamente equilibrados.",
        "circuitos": lambda: [qc_qrng()],
        "leitura": leitura_qrng,
    },
    "E09": {
        "nome": "Codificação de amplitude",
        "descricao": "Ry(2π/3) prepara P(1)=0,75.",
        "circuitos": lambda: [qc_amplitude()],
        "leitura": leitura_amplitude,
    },
    "E10": {
        "nome": "Classificador XOR (VQC)",
        "descricao": "Quatro entradas, quatro medições, uma acurácia.",
        "circuitos": qcs_vqc,
        "leitura": leitura_vqc,
    },
    "E11": {
        "nome": "Interferência de dois qubits",
        "descricao": "H, CZ e H concentram a distribuição em 00/11.",
        "circuitos": lambda: [qc_interferencia2()],
        "leitura": leitura_interferencia2,
    },
    "E12": {
        "nome": "QFT de 3 qubits",
        "descricao": "A transformada de Fourier quântica uniformiza a saída.",
        "circuitos": lambda: [qc_qft3()],
        "leitura": leitura_qft3,
    },
    "E13": {
        "nome": "Produto tensorial |01⟩",
        "descricao": "X no qubit 1 prepara |01⟩.",
        "circuitos": lambda: [qc_tensor01()],
        "leitura": leitura_tensor01,
    },
    "E14": {
        "nome": "Ruído de fase",
        "descricao": "H-X-H deveria devolver P(0)=1; o backend perde coerência.",
        "circuitos": lambda: [qc_ruido_phase()],
        "leitura": leitura_ruido,
    },
    "E15": {
        "nome": "GHZ via QASM 2.0",
        "descricao": "O mesmo GHZ carregado de um texto OpenQASM 2.0.",
        "circuitos": lambda: [qc_qasm_ghz4()],
        "leitura": leitura_ghz,
    },
    "E16": {
        "nome": "Esfera de Bloch",
        "descricao": "Mede Z e X do estado H|0⟩.",
        "circuitos": qcs_bloch,
        "leitura": leitura_bloch,
    },
    "E17": {
        "nome": "Interferência de três qubits",
        "descricao": "Uma caminhada curta distribui amplitude em 000/010/101/111.",
        "circuitos": lambda: [qc_walk3()],
        "leitura": leitura_walk3,
    },
    "E18": {
        "nome": "Amostragem binomial",
        "descricao": "H + medição; o desvio de P(1) cai com o número de tiros.",
        "circuitos": lambda: [qc_amostragem()],
        "leitura": leitura_amostragem,
    },
}

# conceito -> experimento-base
MAPA = {
    # Parte 1
    "bit": "E01", "qubit": "E03", "amplitude": "E09", "probabilidade": "E18",
    "medicao": "E02", "base": "E16", "fase": "E04", "interferencia": "E04",
    "emaranhamento": "E05", "bell": "E07",
    # Parte 2
    "onda_piloto": "E03", "equacao_guia": "E04", "equilibrio_quantico": "E18",
    "nao_localidade": "E07", "colapso_efetivo": "E02", "ordem_implicada": "E11",
    "holomovimento": "E17", "dialogo": "E08", "suspensao": "E16",
    "totalidade": "E06",
    # Parte 3
    "porta_x": "E02", "porta_h": "E03", "porta_z": "E04", "cnot": "E05",
    "circuito": "E11", "bell_circuito": "E05", "ghz": "E06", "qasm": "E15",
    "transpilacao": "E15", "medicao_multipla": "E18",
    # Parte 4
    "pennylane": "E03", "cirq": "E03", "qiskit": "E03", "qnode": "E11",
    "cirq_circuit": "E05", "quantumcircuit": "E05", "statevector": "E16",
    "bloch": "E16", "amostragem": "E18", "gjq_client": "E15",
    # Parte 5
    "supercondutor": "E14", "qubit_fisico": "E02", "decoerencia": "E14",
    "t1_t2": "E14", "erro_leitura": "E02", "ruido": "E14",
    "ciquanta": "E15", "tiangong": "E15", "fila": "E08", "api_key": "E08",
    # Parte 6
    "ghz_real": "E06", "vqc_xor": "E10", "classificador": "E10",
    "encoding": "E09", "ansatz": "E11", "treino": "E10", "acuracia": "E10",
    "phase_damping": "E14", "depolarizing": "E14", "ruido_benefico": "E10",
    # Parte 7
    "vetor": "E16", "matriz": "E11", "produto_interno": "E16",
    "tensor": "E13", "densidade": "E05", "traco": "E05",
    "autovalor": "E16", "fourier": "E12", "holograma": "E17",
    "fourier_quantico": "E12",
    # Parte 8
    "nanoaula": "E18", "autodidatismo": "E10", "feedback": "E02",
    "checkpoint": "E16", "erro_produtivo": "E14", "roda": "E11",
    "projeto": "E11", "rubrica": "E10", "adaptacao": "E09",
    "acessibilidade": "E08",
    # Parte 9
    "acesso": "E08", "dupla_finalidade": "E07", "privacidade": "E08",
    "lgpd": "E08", "custo": "E18", "ambiente": "E14", "trabalho": "E11",
    "desinformacao": "E07", "consenso": "E06", "responsabilidade": "E02",
    # Parte 10
    "pergunta": "E03", "hipotese": "E07", "evidencia": "E16", "limite": "E14",
    "replicacao": "E06", "narrativa": "E17", "visualizacao": "E16",
    "apresentacao": "E15", "portfolio": "E10", "proximo_passo": "E10",
}


def circuitos(exp_id: str) -> list[QuantumCircuit]:
    return EXPERIMENTOS[exp_id]["circuitos"]()


def leitura(exp_id: str, counts: list[dict]) -> str:
    return EXPERIMENTOS[exp_id]["leitura"](counts)