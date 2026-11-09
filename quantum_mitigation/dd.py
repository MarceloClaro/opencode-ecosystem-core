#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dynamical decoupling circuit-level (R1114)."""
from __future__ import annotations

import math

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

DD_SEQUENCES = {
    "xy4": ("rx", "ry", "rx", "ry"),
    "cpmg": ("rx", "rx"),
    "echo": ("rx", "rx"),
}


def _without_measurements(circuit: QuantumCircuit) -> QuantumCircuit:
    return circuit.remove_final_measurements(inplace=False)


def insert_dd(
    circuit: QuantumCircuit,
    qubits: list[int],
    sequence: str = "xy4",
) -> QuantumCircuit:
    """Insere um bloco de DD no fim do circuito (planejamento)."""
    if sequence not in DD_SEQUENCES:
        raise ValueError(f"sequência inválida: {sequence!r}")
    out = _without_measurements(circuit)
    for q in qubits:
        for gate in DD_SEQUENCES[sequence]:
            if gate == "rx":
                out.rx(math.pi, q)
            elif gate == "ry":
                out.ry(math.pi, q)
    return out


def verify_identity(
    circuit: QuantumCircuit,
    qubits: list[int],
    sequence: str = "xy4",
) -> float:
    """Fidelidade entre o estado original e o estado com bloco de DD."""
    base = _without_measurements(circuit)
    with_dd = insert_dd(circuit, qubits, sequence)
    left = Statevector.from_instruction(base)
    right = Statevector.from_instruction(with_dd)
    return float(abs(np.vdot(left.data, right.data)) ** 2)


def dd_plan(
    circuit: QuantumCircuit,
    qubits: list[int],
    sequence: str = "xy4",
) -> dict:
    if not qubits:
        raise ValueError("informe ao menos um qubit para DD")
    base = _without_measurements(circuit)
    with_dd = insert_dd(circuit, qubits, sequence)
    fidelity = verify_identity(circuit, qubits, sequence)
    return {
        "schema_version": 1,
        "sequence": sequence,
        "qubits": list(qubits),
        "gates": list(DD_SEQUENCES[sequence]),
        "base_depth": base.depth(),
        "dd_depth": with_dd.depth(),
        "base_size": base.size(),
        "dd_size": with_dd.size(),
        "identity_fidelity": fidelity,
        "identity_ok": fidelity >= 1.0 - 1e-9,
        "limits": (
            "DD circuit-level inserido no fim do circuito para planejamento; "
            "não é schedule pulse-level nem prova de redução de erro em hardware."
        ),
    }


def pulse_dd_plan(
    *,
    t1_us: float,
    t2_us: float,
    idle_time_us: float,
    sequence: str = "cpmg",
    min_spacing_us: float = 0.1,
) -> dict:
    """Plano de DD pulse-level a partir de T1/T2 e janela ociosa.

    Não executa pulsos; o runtime GJQ atual não expõe controle pulse-level.
    """
    if t1_us <= 0 or t2_us <= 0 or idle_time_us <= 0 or min_spacing_us <= 0:
        raise ValueError("T1, T2, idle_time e min_spacing devem ser > 0")
    if sequence not in DD_SEQUENCES:
        raise ValueError(f"sequência inválida: {sequence!r}")
    if sequence == "xy4":
        blocks = max(1, int(idle_time_us / (4.0 * min_spacing_us)))
        n_pulses = 4 * blocks
    else:
        n_pulses = max(1, int(idle_time_us / min_spacing_us))
    timings = [
        (index + 0.5) * idle_time_us / n_pulses
        for index in range(n_pulses)
    ]
    return {
        "schema_version": 1,
        "sequence": sequence,
        "t1_us": float(t1_us),
        "t2_us": float(t2_us),
        "idle_time_us": float(idle_time_us),
        "min_spacing_us": float(min_spacing_us),
        "n_pulses": n_pulses,
        "timings_us": timings,
        "idle_over_t2": idle_time_us / t2_us,
        "decoder": None,
        "limits": (
            "Plano de timing pulse-level; não executa pulsos e não prevê "
            "ganho de coerência. O runtime GJQ atual não expõe controle de "
            "pulso para implementar este plano em hardware."
        ),
    }
