#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Métricas de circuito e verificação de equivalência distribucional."""
from __future__ import annotations

import time
from typing import Iterable

from qiskit import transpile
from qiskit.quantum_info import Statevector


def _ops(qc) -> dict[str, int]:
    return {str(k): int(v) for k, v in qc.count_ops().items()}


def circuit_metrics(qc) -> dict:
    """Métricas que não dependem de backend."""
    ops = _ops(qc)
    num_1q = 0
    num_2q = 0
    for instr in qc.data:
        nome = instr.operation.name
        if nome in {"measure", "barrier", "reset"}:
            continue
        if instr.operation.num_qubits == 1:
            num_1q += 1
        elif instr.operation.num_qubits == 2:
            num_2q += 1
    return {
        "num_qubits": int(qc.num_qubits),
        "num_clbits": int(qc.num_clbits),
        "size": int(qc.size()),
        "depth": int(qc.depth()),
        "num_1q": num_1q,
        "num_2q": num_2q,
        "num_measure": int(ops.get("measure", 0)),
        "ops": ops,
    }


def _measure_map(qc) -> list[tuple[int, int]]:
    saida = []
    for instr in qc.data:
        if instr.operation.name == "measure":
            q = qc.find_bit(instr.qubits[0]).index
            c = qc.find_bit(instr.clbits[0]).index
            saida.append((q, c))
    return saida


def dist_ideal(qc) -> dict[str, float]:
    """Distribuição ideal nos bits clássicos medidos.

    Remove as medidas, calcula o statevector e marginaliza para os bits
    clássicos. Se não houver medida, devolve a distribuição de todos os qubits.
    """
    mapa = _measure_map(qc)
    limpo = qc.remove_final_measurements(inplace=False)
    probs = Statevector(limpo).probabilities_dict()
    if not mapa:
        return {str(k): float(v) for k, v in probs.items()}
    n, m = qc.num_qubits, qc.num_clbits
    dist: dict[str, float] = {}
    for estado, prob in probs.items():
        bits = ["0"] * m
        for q, c in mapa:
            bits[m - 1 - c] = estado[n - 1 - q]
        chave = "".join(bits)
        dist[chave] = dist.get(chave, 0.0) + float(prob)
    return dist


def tvd(a: dict[str, float], b: dict[str, float]) -> float:
    return 0.5 * sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in set(a) | set(b))


def transpile_measured(
    qc,
    optimization_level: int,
    seed: int,
    basis_gates: Iterable[str] = ("u", "cx"),
    coupling_map=None,
):
    """Transpila e mede o tempo de transpilação."""
    kwargs = {
        "basis_gates": list(basis_gates),
        "optimization_level": int(optimization_level),
        "seed_transpiler": int(seed),
    }
    if coupling_map is not None:
        kwargs["coupling_map"] = coupling_map
    inicio = time.perf_counter()
    saida = transpile(qc, **kwargs)
    return saida, time.perf_counter() - inicio
