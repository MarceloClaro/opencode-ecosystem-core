#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Benchmarks determinísticos para medir eficiência de circuitos."""
from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate


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


def qft4() -> QuantumCircuit:
    qc = QuantumCircuit(4, 4)
    qc.x(3)
    qc.append(QFTGate(4), range(4))
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    return qc


def vqe2() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.ry(0.3, 0)
    qc.ry(0.6, 1)
    qc.cx(0, 1)
    qc.ry(-0.4, 0)
    qc.ry(0.5, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def layered4() -> QuantumCircuit:
    qc = QuantumCircuit(4, 4)
    for camada in range(3):
        for q in range(4):
            qc.h(q)
            qc.rz(0.1 * (q + 1) * (camada + 1), q)
        for q in range(3):
            qc.cx(q, q + 1)
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    return qc


def redundant() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.x(0)
    qc.h(1)
    qc.h(1)
    qc.cx(0, 1)
    qc.cx(0, 1)
    qc.h(0)
    qc.measure([0, 1], [0, 1])
    return qc


def nonadjacent() -> QuantumCircuit:
    qc = QuantumCircuit(4, 4)
    qc.h(0)
    qc.cx(0, 3)
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    return qc


BENCHMARKS = [
    {"name": "bell", "circuit": bell(), "coupling_map": None},
    {"name": "ghz4", "circuit": ghz4(), "coupling_map": None},
    {"name": "qft4", "circuit": qft4(), "coupling_map": None},
    {"name": "vqe2", "circuit": vqe2(), "coupling_map": None},
    {"name": "layered4", "circuit": layered4(), "coupling_map": None},
    {"name": "redundant", "circuit": redundant(), "coupling_map": None},
    {"name": "nonadjacent", "circuit": nonadjacent(), "coupling_map": [[0, 1], [1, 2], [2, 3]]},
]
