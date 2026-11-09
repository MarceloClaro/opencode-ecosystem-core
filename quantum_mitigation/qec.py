#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Código de repetição de 3 qubits para bit-flip (R1114)."""
from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, pauli_error


def repetition_code_circuit() -> QuantumCircuit:
    """Codifica |0> em 3 qubits, extrai síndrome e mede dados + ancillas."""
    qc = QuantumCircuit(5, 5)
    qc.id(0)
    qc.id(1)
    qc.id(2)
    # s0 = z0 xor z1
    qc.cx(0, 3)
    qc.cx(1, 3)
    # s1 = z1 xor z2
    qc.cx(1, 4)
    qc.cx(2, 4)
    qc.measure(range(5), range(5))
    return qc


def _decode(key: str) -> tuple[int, int, int, int, int]:
    bits = key.zfill(5)
    d0 = int(bits[-1])
    d1 = int(bits[-2])
    d2 = int(bits[-3])
    s0 = int(bits[-4])
    s1 = int(bits[-5])
    return d0, d1, d2, s0, s1


def _correct(d0: int, d1: int, d2: int, s0: int, s1: int) -> int:
    if s0 == 1 and s1 == 0:
        d0 ^= 1
    elif s0 == 1 and s1 == 1:
        d1 ^= 1
    elif s0 == 0 and s1 == 1:
        d2 ^= 1
    return d0


def run_repetition_code(
    p: float,
    *,
    shots: int = 20000,
    seed: int = 42,
) -> dict:
    if not 0.0 <= p < 1.0:
        raise ValueError("p deve estar em [0, 1)")
    model = NoiseModel()
    error = pauli_error([("X", p), ("I", 1.0 - p)])
    for q in (0, 1, 2):
        model.add_quantum_error(error, ["id"], [q])
    simulator = AerSimulator(noise_model=model, seed_simulator=int(seed))
    counts = simulator.run(repetition_code_circuit(), shots=int(shots)).result().get_counts()
    logical_errors = 0
    total = 0
    for key, count in counts.items():
        d0, d1, d2, s0, s1 = _decode(key)
        logical = _correct(d0, d1, d2, s0, s1)
        logical_errors += int(count) * logical
        total += int(count)
    logical_error = logical_errors / total if total else None
    theory = 3.0 * p**2 - 2.0 * p**3
    return {
        "schema_version": 1,
        "code": "repetition_3_bitflip",
        "distance": 3,
        "physical_qubits": 3,
        "syndrome_qubits": 2,
        "p": float(p),
        "shots": int(shots),
        "logical_error_simulated": logical_error,
        "logical_error_theory": theory,
        "counts_total": total,
        "limits": (
            "Código de repetição de 3 qubits para bit-flip; não protege fase, "
            "não é código de superfície e não demonstra fault tolerance."
        ),
    }


def qec_plan(distance: int = 3, p: float = 0.01) -> dict:
    if distance != 3:
        raise ValueError("apenas distância 3 do código de repetição está implementada")
    theory = 3.0 * p**2 - 2.0 * p**3
    return {
        "schema_version": 1,
        "code": "repetition_3_bitflip",
        "distance": 3,
        "physical_qubits": 3,
        "syndrome_qubits": 2,
        "p": float(p),
        "logical_error_theory": theory,
        "limits": (
            "Plano para bit-flip; não protege fase. Não é superfície, não é "
            "fault-tolerant e não garante threshold."
        ),
    }


def surface_code_plan(
    distance: int = 3,
    rounds: int = 3,
    physical_error_rate: float = 0.001,
    threshold: float | None = None,
) -> dict:
    """Orçamento de qubits e interface de decodificador para código de superfície.

    Não simula o código de superfície. O threshold é um parâmetro declarado,
    não uma medida. A estimativa só é calculada se o operador fornecer um
    threshold explícito e p < threshold.
    """
    distance = int(distance)
    rounds = int(rounds)
    if distance < 3 or distance % 2 == 0:
        raise ValueError("distance deve ser ímpar >= 3")
    if rounds < 1:
        raise ValueError("rounds deve ser >= 1")
    if not 0.0 <= physical_error_rate < 1.0:
        raise ValueError("physical_error_rate deve estar em [0, 1)")
    data_qubits = distance * distance
    ancilla_qubits = data_qubits - 1
    total_qubits = data_qubits + ancilla_qubits
    syndrome_bits = ancilla_qubits * rounds
    estimate = None
    if threshold is not None:
        threshold = float(threshold)
        if not 0.0 < threshold < 1.0:
            raise ValueError("threshold deve estar em (0, 1)")
        if physical_error_rate < threshold:
            estimate = (physical_error_rate / threshold) ** ((distance + 1) // 2)
    return {
        "schema_version": 1,
        "code": "rotated_surface_code",
        "distance": distance,
        "rounds": rounds,
        "physical_error_rate": physical_error_rate,
        "threshold_declared": threshold,
        "logical_error_estimate": estimate,
        "qubit_budget": {
            "data": data_qubits,
            "ancilla": ancilla_qubits,
            "total": total_qubits,
            "syndrome_bits": syndrome_bits,
        },
        "decoder": {
            "name": "MWPM interface",
            "executed": False,
            "note": "interface de planejamento; nenhum decodificador foi executado",
        },
        "limits": (
            "Planejamento de orçamento e interface de decodificador; não é "
            "simulação do código de superfície, não prova threshold e não "
            "demonstra fault tolerance."
        ),
    }
