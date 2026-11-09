#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Passe de Pauli-frame para randomized compiling (R1119).

Implementa o twirl de Pauli em portas Clifford:

    P' · G · P = G,   P' = G P G†

Cada porta Clifford recebe um Pauli aleatório P antes e o conjugado P' depois.
O circuito é logicamente idêntico ao original (a menos de fase global), mas o
ruído entre portas é twirlado. Não executa hardware e não declara RC validado.
"""
from __future__ import annotations

from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Clifford, Pauli

CLIFFORD_GATES = frozenset(
    {
        "id",
        "h",
        "x",
        "y",
        "z",
        "s",
        "sdg",
        "sx",
        "sxdg",
        "cx",
        "cy",
        "cz",
        "swap",
        "rx",
        "ry",
        "rz",
    }
)


def random_pauli(num_qubits: int, rng: np.random.Generator) -> Pauli:
    """Sorteia um Pauli uniforme em {I,X,Y,Z}^n."""
    if num_qubits < 1:
        raise ValueError("num_qubits deve ser >= 1")
    label = "".join(rng.choice(list("IXYZ"), size=num_qubits))
    return Pauli(label)


def conjugate_pauli(clifford: Clifford, pauli: Pauli) -> Pauli:
    """Retorna G P G† como Pauli, usando a matriz simplética do Clifford."""
    if clifford.num_qubits != pauli.num_qubits:
        raise ValueError("Clifford e Pauli com números de qubits diferentes")
    num_qubits = clifford.num_qubits
    x_map = np.asarray(clifford.x, dtype=bool)
    z_map = np.asarray(clifford.z, dtype=bool)
    x_in = np.asarray(pauli.x, dtype=bool)
    z_in = np.asarray(pauli.z, dtype=bool)
    x_out = np.zeros(num_qubits, dtype=bool)
    z_out = np.zeros(num_qubits, dtype=bool)
    for index in range(num_qubits):
        if x_in[index]:
            x_out ^= x_map[index]
            z_out ^= z_map[index]
        if z_in[index]:
            x_out ^= x_map[num_qubits + index]
            z_out ^= z_map[num_qubits + index]
    return Pauli((z_out, x_out))


def _gate_clifford(operation: Any) -> Clifford:
    if operation.name not in CLIFFORD_GATES:
        raise ValueError(
            f"porta não suportada pelo passe de Pauli-frame: {operation.name}"
        )
    try:
        return Clifford(operation)
    except Exception as exc:  # QiskitError para ângulos não-Clifford
        raise ValueError(
            f"porta {operation.name} não é Clifford para este ângulo: {exc}"
        ) from exc


def pauli_frame_pass(
    circuit: QuantumCircuit,
    *,
    seed: int | None = None,
    rng: np.random.Generator | None = None,
    strict: bool = True,
) -> dict:
    """Aplica o twirl de Pauli a cada porta Clifford do circuito.

    Retorna o circuito twirlado, a lista de twirls e as portas ignoradas.
    Medições e barreiras são preservadas.
    """
    if rng is None:
        rng = np.random.default_rng(seed)
    if circuit.num_clbits and not circuit.cregs:
        raise ValueError("circuito com clbits sem registradores clássicos")

    new = QuantumCircuit(*circuit.qregs, *circuit.cregs)
    twirls: list[dict] = []
    skipped: list[str] = []
    for instruction in circuit.data:
        operation = instruction.operation
        qubits = [
            new.qubits[circuit.find_bit(qubit).index]
            for qubit in instruction.qubits
        ]
        if operation.name in ("measure", "barrier"):
            clbits = [
                new.clbits[circuit.find_bit(clbit).index]
                for clbit in instruction.clbits
            ]
            new.append(operation, qubits, clbits)
            continue
        try:
            clifford = _gate_clifford(operation)
        except ValueError:
            if strict:
                raise
            skipped.append(operation.name)
            new.append(operation, qubits)
            continue
        pauli = random_pauli(len(qubits), rng)
        conjugated = conjugate_pauli(clifford, pauli)
        new.append(pauli.to_instruction(), qubits)
        new.append(operation, qubits)
        new.append(conjugated.to_instruction(), qubits)
        twirls.append(
            {
                "gate": operation.name,
                "qubits": [circuit.find_bit(qubit).index for qubit in instruction.qubits],
                "pauli": str(pauli),
                "conjugated": str(conjugated),
            }
        )
    return {
        "schema_version": 1,
        "circuit": new,
        "n_twirls": len(twirls),
        "twirls": twirls,
        "skipped": skipped,
        "strict": bool(strict),
        "limits": (
            "Passe de Pauli-frame para portas Clifford. Não é RC completo de "
            "2 qubits com decodificador em tempo real; não executa hardware."
        ),
    }


def verify_equivalence(
    original: QuantumCircuit,
    twirled: QuantumCircuit,
    *,
    atol: float = 1e-8,
) -> dict:
    """Verifica igualdade up to fase global via traço de operadores."""
    from qiskit.quantum_info import Operator

    clean_original = original.remove_final_measurements(inplace=False)
    clean_twirled = twirled.remove_final_measurements(inplace=False)
    if clean_original.num_qubits != clean_twirled.num_qubits:
        raise ValueError("circuitos com números de qubits diferentes")
    u1 = Operator(clean_original).data
    u2 = Operator(clean_twirled).data
    overlap = np.trace(u1.conj().T @ u2) / u1.shape[0]
    return {
        "equivalent_up_to_phase": bool(abs(abs(overlap) - 1.0) <= atol),
        "overlap": {
            "real": float(np.real(overlap)),
            "imag": float(np.imag(overlap)),
            "abs": float(abs(overlap)),
        },
        "atol": atol,
    }
