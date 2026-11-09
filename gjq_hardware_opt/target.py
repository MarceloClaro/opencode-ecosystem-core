#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construção de um Target do Qiskit a partir de um perfil declarado (R1109)."""
from __future__ import annotations

from qiskit.circuit import Measure, Parameter
from qiskit.circuit.library import (
    CXGate,
    CZGate,
    ECRGate,
    HGate,
    IGate,
    RXGate,
    RYGate,
    RZGate,
    SXGate,
    UGate,
    XGate,
)
from qiskit.transpiler import Target
from qiskit.transpiler.target import InstructionProperties

from .profile import HardwareProfile


def _gate_for(name: str):
    if name == "rz":
        return RZGate(Parameter("theta"))
    if name == "rx":
        return RXGate(Parameter("theta"))
    if name == "ry":
        return RYGate(Parameter("theta"))
    if name == "h":
        return HGate()
    if name == "u":
        return UGate(Parameter("theta"), Parameter("phi"), Parameter("lam"))
    if name == "sx":
        return SXGate()
    if name == "x":
        return XGate()
    if name == "id":
        return IGate()
    if name == "cx":
        return CXGate()
    if name == "cz":
        return CZGate()
    if name == "ecr":
        return ECRGate()
    raise ValueError(
        f"porta sem construção conhecida no perfil: {name!r}; "
        "use rz, u, sx, x, id, cx, cz ou ecr"
    )


def build_target_from_profile(profile: HardwareProfile) -> Target:
    """Reconstrói um Target com erros e durações do perfil.

    O Target preserva os índices físicos do backend. A largura é a do perfil,
    mesmo que o circuito use poucos qubits; a compactação é feita depois da
    transpilação.
    """
    target = Target(
        num_qubits=profile.num_qubits,
        description=f"{profile.name} ({profile.profile_kind})",
    )
    operational = list(profile.operational_qubits) or list(range(profile.num_qubits))
    for gate in profile.oneq_gates:
        properties = {}
        for q in operational:
            error = 0.0 if gate == "rz" else profile.oneq_error_for(gate, q)
            duration = profile.oneq_duration.get(gate, {}).get(q, 0.0)
            properties[(q,)] = InstructionProperties(duration=duration, error=error)
        if properties:
            target.add_instruction(_gate_for(gate), properties)

    for gate in profile.twoq_gates:
        properties = {}
        for edge in profile.coupling_map:
            a, b = edge
            error = profile.twoq_error_for(gate, a, b)
            duration = profile.twoq_duration.get(gate, {}).get(edge, 0.0)
            properties[(a, b)] = InstructionProperties(duration=duration, error=error)
        if properties:
            target.add_instruction(_gate_for(gate), properties)

    measure_props = {
        (q,): InstructionProperties(
            duration=profile.readout_duration.get(q, 0.0),
            error=profile.readout_error[q],
        )
        for q in operational
    }
    target.add_instruction(Measure(), measure_props)
    return target


def target_gate_names(target: Target) -> list[str]:
    return [str(name) for name in target.operation_names]
