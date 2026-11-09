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
