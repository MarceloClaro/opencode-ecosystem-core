#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os circuitos OpenQASM 2.0 usados no livro e no editor da Tiangong.

Os arquivos ficam em ``circuitos_qasm/`` e podem ser colados no editor
``https://tiangongqs.com/cloud/circuit`` (modo QASM). O script valida cada
arquivo com ``qiskit.qasm2.loads`` antes de gravar o README.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit, qasm2

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "circuitos_qasm"


def bell() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def ghz4() -> QuantumCircuit:
    qc = QuantumCircuit(4, 4)
    qc.h(0)
    for alvo in (1, 2, 3):
        qc.cx(0, alvo)
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    return qc


def chsh(a1: int, angulo: float) -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    if a1:
        qc.h(0)
    qc.ry(angulo, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def vqc(x: tuple[int, int], theta: list[float]) -> QuantumCircuit:
    qc = QuantumCircuit(2, 1)
    qc.ry(np.pi * x[0], 0)
    qc.ry(np.pi * x[1], 1)
    qc.ry(theta[0], 0)
    qc.ry(theta[1], 1)
    qc.cx(0, 1)
    qc.ry(theta[2], 0)
    qc.ry(theta[3], 1)
    qc.measure(0, 0)
    return qc


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    theta = [1.5708, 1.5708, -1.5708, 2.819]

    circuitos = {
        "bell.qasm": bell(),
        "ghz4.qasm": ghz4(),
    }
    for nome, a1, angulo in [
        ("e00", 0, -np.pi / 4),
        ("e01", 0, np.pi / 4),
        ("e10", 1, -np.pi / 4),
        ("e11", 1, np.pi / 4),
    ]:
        circuitos[f"chsh_{nome}.qasm"] = chsh(a1, float(angulo))
    for x in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        circuitos[f"vqc_xor_{x[0]}{x[1]}.qasm"] = vqc(x, theta)

    for nome, qc in circuitos.items():
        texto = qasm2.dumps(qc)
        # valida antes de gravar
        qasm2.loads(texto)
        (SAIDA / nome).write_text(texto, encoding="utf-8")
        print(f"  ✓ {nome} ({qc.num_qubits} qubits, depth {qc.depth()})")

    readme = """# Circuitos OpenQASM 2.0

Estes arquivos são os circuitos usados no livro. Eles podem ser colados no
editor de circuitos da Tiangong:

1. Abra <https://tiangongqs.com/cloud/circuit>.
2. Entre na sua conta.
3. Escolha o editor **QASM** (OpenQASM 2.0).
4. Cole o conteúdo de um arquivo desta pasta.
5. Selecione o backend (`Guoji08`, `Baihua` ou um simulador).
6. Defina 1024 tiros e execute.
7. Compare os counts com a tabela da lauda correspondente.

| Arquivo | Experimento | O que esperar |
|---|---|---|
| `bell.qasm` | Bell | 00 e 11 dominam; 01 e 10 são ruído |
| `ghz4.qasm` | GHZ de 4 qubits | 0000 e 1111 dominam; ~21% fora no Guoji08 |
| `chsh_e00.qasm` | CHSH E00 | correlação positiva |
| `chsh_e01.qasm` | CHSH E01 | correlação positiva |
| `chsh_e10.qasm` | CHSH E10 | correlação positiva |
| `chsh_e11.qasm` | CHSH E11 | correlação negativa |
| `vqc_xor_00.qasm` | VQC XOR 00 | P(1) baixo |
| `vqc_xor_01.qasm` | VQC XOR 01 | P(1) alto |
| `vqc_xor_10.qasm` | VQC XOR 10 | P(1) alto |
| `vqc_xor_11.qasm` | VQC XOR 11 | P(1) baixo |

> **Limite:** o editor pode exigir login, fila e backend disponível. O arquivo
> QASM é compatível com OpenQASM 2.0; isso não é uma garantia de execução
> imediata nem de resultado idêntico. A calibração muda.
"""
    (SAIDA / "README.md").write_text(readme, encoding="utf-8")
    print(f"Pronto: {SAIDA}")


if __name__ == "__main__":
    main()