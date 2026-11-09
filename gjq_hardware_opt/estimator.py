#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Estimativa de sucesso por porta para um perfil de hardware (R1109).

O valor é um proxy: produto de ``(1 - erro)`` por operação e leitura. Ele não é
fidelidade de estado, não inclui crosstalk, leakage, deriva ou correlação.
"""
from __future__ import annotations

import math

from qiskit import QuantumCircuit

from .profile import HardwareProfile


def estimate_success(circuit: QuantumCircuit, profile: HardwareProfile) -> dict:
    log_success = 0.0
    operations = 0
    unknown: set[str] = set()
    per_gate: dict[str, int] = {}
    for instruction in circuit.data:
        name = instruction.operation.name
        if name in {"barrier", "delay"}:
            continue
        per_gate[name] = per_gate.get(name, 0) + 1
        if name == "measure":
            error = 0.0
            for qubit in instruction.qubits:
                q = circuit.find_bit(qubit).index
                error = 1.0 - (1.0 - error) * (1.0 - profile.readout_error.get(q, profile.default_readout_error))
        elif name == "reset":
            error = profile.default_error
            unknown.add(name)
        elif len(instruction.qubits) == 1:
            q = circuit.find_bit(instruction.qubits[0]).index
            error = 0.0 if name == "rz" else profile.oneq_error_for(name, q)
            if name not in profile.oneq_gates and name != "rz":
                unknown.add(name)
        elif len(instruction.qubits) == 2:
            a = circuit.find_bit(instruction.qubits[0]).index
            b = circuit.find_bit(instruction.qubits[1]).index
            error = profile.twoq_error_for(name, a, b)
            if name not in profile.twoq_gates:
                unknown.add(name)
        else:
            error = profile.default_error
            unknown.add(name)

        error = min(max(float(error), 0.0), 1.0)
        if error >= 1.0:
            log_success = -math.inf
        elif log_success != -math.inf:
            log_success += math.log1p(-error)
        operations += 1

    success = 0.0 if log_success == -math.inf else math.exp(log_success)
    return {
        "success_proxy": success,
        "error_budget_proxy": 1.0 - success,
        "log_success_proxy": log_success,
        "operations": operations,
        "per_gate": dict(sorted(per_gate.items())),
        "unknown_operations": sorted(unknown),
        "method": (
            "produto de (1 - erro) por porta e leitura; proxy independente, "
            "não é fidelidade de estado"
        ),
    }
