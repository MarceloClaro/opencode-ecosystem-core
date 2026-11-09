#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mitigação de erro de leitura para o hardware GJQ (R1110).

Duas fontes de matriz de confusão:

1. calibração no hardware: prepara |00> e |11> (ou todos os estados da base)
   nos mesmos quitais físicos e mede;
2. perfil: usa ``readout_error`` de forma simétrica quando as propriedades
   assimétricas são sentinela (o Baihua reporta ``prob_meas*=1.0``).

A mitigação por inversão pode produzir massas negativas; elas são clipadas e
o vetor é renormalizado. O resultado é descritivo e não é fidelidade.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
from qiskit import QuantumCircuit

from .profile import HardwareProfile

MAX_MITIGATION_QUBITS = 6


@dataclass
class ReadoutModel:
    qubits: tuple[int, ...]
    matrix: list[list[float]]
    source: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "qubits": list(self.qubits),
            "matrix": [[float(x) for x in row] for row in self.matrix],
            "source": self.source,
            "size": len(self.qubits),
        }


def states_for(n: int) -> list[str]:
    return ["".join(bits) for bits in itertools.product("01", repeat=n)]


def _validate_readout(value: float, fallback: float) -> float:
    value = float(value)
    if not 0.0 <= value < 0.5:
        return float(fallback)
    return value


def readout_confusion_matrix(
    profile: HardwareProfile,
    qubits: Iterable[int],
) -> ReadoutModel:
    """Matriz de confusão a partir do perfil, com fallback simétrico.

    ``qubits`` está na ordem MSB -> LSB dos bits clássicos. Para o Bell em
    q106/q107 com ``measure q[106] -> c[0]`` e ``q[107] -> c[1]``, a ordem é
    ``(107, 106)``.
    """
    order = tuple(int(q) for q in qubits)
    if len(order) > MAX_MITIGATION_QUBITS:
        raise ValueError(
            f"mitigação limitada a {MAX_MITIGATION_QUBITS} qubits; recebido {len(order)}"
        )
    matrix = np.array([[1.0]])
    source = "profile_symmetric"
    for q in order:
        error = profile.readout_error.get(q, profile.default_readout_error)
        p1_given_0 = _validate_readout(
            getattr(profile, "readout_p1_given_0", {}).get(q, error), error
        )
        p0_given_1 = _validate_readout(
            getattr(profile, "readout_p0_given_1", {}).get(q, error), error
        )
        if p1_given_0 != error or p0_given_1 != error:
            source = "profile_asymmetric"
        single = np.array(
            [
                [1.0 - p1_given_0, p0_given_1],
                [p1_given_0, 1.0 - p0_given_1],
            ],
            dtype=float,
        )
        matrix = np.kron(matrix, single)
    return ReadoutModel(order, matrix.tolist(), source)


def confusion_from_calibration_counts(
    prepared_counts: dict[str, dict[str, int]],
    qubits: Iterable[int],
    *,
    require_full: bool = True,
) -> ReadoutModel:
    """Constrói a matriz a partir de counts de calibração.

    ``prepared_counts`` mapeia o bitstring preparado para os counts medidos.
    A ordem dos bits é MSB -> LSB, igual à ordem de ``qubits``.
    """
    order = tuple(int(q) for q in qubits)
    n = len(order)
    if n > MAX_MITIGATION_QUBITS:
        raise ValueError(
            f"mitigação limitada a {MAX_MITIGATION_QUBITS} qubits; recebido {n}"
        )
    all_states = states_for(n)
    size = len(all_states)
    matrix = np.zeros((size, size), dtype=float)
    for prepared, counts in prepared_counts.items():
        if prepared not in all_states:
            raise ValueError(f"estado preparado inválido: {prepared!r}")
        total = sum(int(v) for v in counts.values())
        if total <= 0:
            raise ValueError(f"counts vazios para o estado {prepared}")
        column = int(prepared, 2)
        for measured, count in counts.items():
            if measured not in all_states:
                raise ValueError(f"estado medido inválido: {measured!r}")
            matrix[int(measured, 2), column] += int(count) / total
    if require_full:
        missing = [
            state for state in all_states
            if state not in prepared_counts
        ]
        if missing:
            raise ValueError(f"calibração incompleta; faltam {missing}")
    return ReadoutModel(order, matrix.tolist(), "hardware_calibration")


def subspace_matrix_from_calibration(
    prepared_counts: dict[str, dict[str, int]],
    states: tuple[str, ...] = ("00", "11"),
) -> tuple[list[list[float]], dict[str, float]]:
    """Matriz 2x2 restrita a ``states`` e leakage por coluna.

    Para o Bell, preparar |00> e |11> e medir apenas a população nesses dois
    estados é suficiente para inverter a correlação. O leakage (01/10) é
    reportado separadamente e não entra na inversão.
    """
    if len(states) != 2:
        raise ValueError("a submatriz exige exatamente dois estados")
    matrix = np.zeros((2, 2), dtype=float)
    leakage: dict[str, float] = {}
    for column, prepared in enumerate(states):
        if prepared not in prepared_counts:
            raise ValueError(f"calibração ausente para {prepared}")
        counts = prepared_counts[prepared]
        total = sum(int(v) for v in counts.values())
        if total <= 0:
            raise ValueError(f"counts vazios para {prepared}")
        inside = sum(int(counts.get(state, 0)) for state in states)
        if inside <= 0:
            raise ValueError(f"calibração sem população em {states} para {prepared}")
        for row, state in enumerate(states):
            matrix[row, column] = int(counts.get(state, 0)) / inside
        leakage[prepared] = max(0.0, 1.0 - inside / total)
    return matrix.tolist(), leakage


def _clip_and_normalize(values: np.ndarray) -> tuple[np.ndarray, float]:
    negative_mass = float(-np.sum(values[values < 0.0]))
    clipped = np.clip(values, 0.0, None)
    total = float(np.sum(clipped))
    if total <= 0.0:
        return np.zeros_like(clipped), negative_mass
    return clipped / total, negative_mass


def mitigate_probabilities(
    probabilities: dict[str, float],
    model: ReadoutModel,
) -> dict[str, Any]:
    """Inverte a matriz completa e devolve probabilidades mitigadas."""
    n = len(model.qubits)
    all_states = states_for(n)
    vector = np.array([float(probabilities.get(state, 0.0)) for state in all_states])
    matrix = np.array(model.matrix, dtype=float)
    condition = float(np.linalg.cond(matrix)) if matrix.size else math.inf
    if not math.isfinite(condition) or condition > 1e12:
        mitigated = np.linalg.pinv(matrix) @ vector
        method = "pseudoinverse"
    else:
        mitigated = np.linalg.solve(matrix, vector)
        method = "inverse"
    mitigated, negative_mass = _clip_and_normalize(mitigated)
    return {
        "method": method,
        "source": model.source,
        "qubits": list(model.qubits),
        "matrix": [[float(x) for x in row] for row in model.matrix],
        "condition_number": condition,
        "negative_mass_clipped": negative_mass,
        "probabilities": {
            state: float(mitigated[index])
            for index, state in enumerate(all_states)
        },
    }


def mitigate_subspace(
    probabilities: dict[str, float],
    matrix: list[list[float]],
    states: tuple[str, ...] = ("00", "11"),
) -> dict[str, Any]:
    """Inverte a submatriz 2x2 dos estados correlacionados."""
    vector = np.array([float(probabilities.get(state, 0.0)) for state in states])
    matrix_np = np.array(matrix, dtype=float)
    condition = float(np.linalg.cond(matrix_np))
    if not math.isfinite(condition) or condition > 1e12:
        mitigated = np.linalg.pinv(matrix_np) @ vector
        method = "pseudoinverse"
    else:
        mitigated = np.linalg.solve(matrix_np, vector)
        method = "inverse"
    mitigated, negative_mass = _clip_and_normalize(mitigated)
    leakage = max(0.0, 1.0 - float(np.sum(vector)))
    return {
        "method": method,
        "states": list(states),
        "matrix": [[float(x) for x in row] for row in matrix],
        "condition_number": condition,
        "negative_mass_clipped": negative_mass,
        "leakage_outside_subspace": leakage,
        "probabilities": {
            state: float(mitigated[index])
            for index, state in enumerate(states)
        },
    }


def measurement_order(circuit: QuantumCircuit) -> list[int]:
    """Qubits físicos na ordem MSB -> LSB dos bits clássicos medidos."""
    pairs = []
    for instruction in circuit.data:
        if instruction.operation.name != "measure":
            continue
        if not instruction.clbits:
            continue
        q = circuit.find_bit(instruction.qubits[0]).index
        c = circuit.find_bit(instruction.clbits[0]).index
        pairs.append((c, q))
    pairs.sort(key=lambda item: item[0], reverse=True)
    return [q for _, q in pairs]


def calibration_circuit(qubits_order: list[int], prepared: str) -> QuantumCircuit:
    """Prepara ``prepared`` e mede na ordem MSB -> LSB de ``qubits_order``."""
    n = len(qubits_order)
    if len(prepared) != n or set(prepared) - {"0", "1"}:
        raise ValueError("prepared deve ter o mesmo tamanho e conter apenas 0/1")
    width = max(qubits_order) + 1
    circuit = QuantumCircuit(width, n)
    for index, q in enumerate(qubits_order):
        if prepared[index] == "1":
            # rx(pi) pertence à base do Baihua; x pode não pertencer.
            circuit.rx(math.pi, q)
    for index, q in enumerate(qubits_order):
        circuit.measure(q, n - 1 - index)
    return circuit


def calibration_circuits(
    qubits_order: list[int],
    *,
    states: Iterable[str] | None = None,
) -> dict[str, QuantumCircuit]:
    selected = list(states) if states is not None else states_for(len(qubits_order))
    return {
        state: calibration_circuit(qubits_order, state)
        for state in selected
    }


def mitigate_counts_for_circuit(
    counts: dict[str, int],
    circuit: QuantumCircuit,
    profile: HardwareProfile,
    *,
    calibration: ReadoutModel | None = None,
) -> dict[str, Any]:
    """Mitiga counts de um circuito pequeno usando o perfil ou calibração."""
    order = measurement_order(circuit)
    if not order:
        raise ValueError("o circuito não tem medições")
    if len(order) > MAX_MITIGATION_QUBITS:
        raise ValueError(
            f"mitigação limitada a {MAX_MITIGATION_QUBITS} qubits; recebido {len(order)}"
        )
    total = sum(int(v) for v in counts.values())
    if total <= 0:
        raise ValueError("counts vazio")
    probabilities = {str(k): int(v) / total for k, v in counts.items()}
    model = calibration or readout_confusion_matrix(profile, order)
    result = mitigate_probabilities(probabilities, model)
    result["raw_probabilities"] = probabilities
    result["total"] = total
    return result


def ideal_bell_subspace() -> dict[str, float]:
    return {"00": 0.5, "11": 0.5}


def correlation(probabilities: dict[str, float]) -> float:
    return float(probabilities.get("00", 0.0) + probabilities.get("11", 0.0))


def tvd_vs_ideal(probabilities: dict[str, float]) -> float:
    ideal = ideal_bell_subspace()
    keys = set(probabilities) | set(ideal)
    return 0.5 * sum(
        abs(float(probabilities.get(k, 0.0)) - ideal.get(k, 0.0))
        for k in keys
    )
