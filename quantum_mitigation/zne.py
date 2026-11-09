#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zero-noise extrapolation (ZNE) para circuitos pequenos (R1114)."""
from __future__ import annotations

import math

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

from quantum_efficiency.metrics import dist_ideal, tvd


def _unitary_circuit(circuit: QuantumCircuit) -> QuantumCircuit:
    """Remove medidas/barreiras para permitir folding unitário."""
    out = QuantumCircuit(circuit.num_qubits)
    for instruction in circuit.data:
        if instruction.operation.name in {"measure", "barrier"}:
            continue
        qargs = [
            out.qubits[circuit.find_bit(q).index]
            for q in instruction.qubits
        ]
        out.append(instruction.operation, qargs)
    return out


def fold_circuit(circuit: QuantumCircuit, scale: int) -> QuantumCircuit:
    """Folding global U -> U (U† U)^k, com escala ímpar >= 1."""
    scale = int(scale)
    if scale < 1 or scale % 2 == 0:
        raise ValueError("scale deve ser inteiro ímpar >= 1")
    base = _unitary_circuit(circuit)
    k = (scale - 1) // 2
    folded = base.copy()
    if k:
        inverse = base.inverse()
        for _ in range(k):
            folded.compose(inverse, inplace=True)
            folded.compose(base, inplace=True)
    if circuit.num_clbits:
        folded.add_register(ClassicalRegister(circuit.num_clbits))
        for instruction in circuit.data:
            if instruction.operation.name != "measure":
                continue
            q = circuit.find_bit(instruction.qubits[0]).index
            c = circuit.find_bit(instruction.clbits[0]).index
            folded.measure(q, c)
    return folded


def noise_model_from_profile(profile, circuit: QuantumCircuit) -> NoiseModel:
    used = sorted(
        {
            circuit.find_bit(q).index
            for instruction in circuit.data
            for q in instruction.qubits
        }
    )
    used_set = set(used)
    model = NoiseModel()
    for gate, by_qubit in profile.oneq_error.items():
        if gate == "rz":
            continue
        for q in used:
            error = by_qubit.get(q, profile.default_error)
            if error > 0:
                model.add_quantum_error(depolarizing_error(error, 1), [gate], [q])
    for gate, by_edge in profile.twoq_error.items():
        for (a, b), error in by_edge.items():
            if a in used_set and b in used_set and error > 0:
                model.add_quantum_error(
                    depolarizing_error(error, 2), [gate], [a, b]
                )
    for q in used:
        error = profile.readout_error.get(q, profile.default_readout_error)
        model.add_readout_error(
            ReadoutError([[1.0 - error, error], [error, 1.0 - error]]),
            [q],
        )
    return model


def extrapolate(
    scales: list[int],
    values: list[float],
    method: str = "linear",
) -> dict:
    x = np.asarray(scales, dtype=float)
    y = np.asarray(values, dtype=float)
    if len(x) < 2:
        raise ValueError("ZNE exige ao menos duas escalas")
    if method == "linear":
        coefficients = np.polyfit(x, y, 1)
        result = float(coefficients[1])
    elif method == "quadratic":
        if len(x) < 3:
            raise ValueError("extrapolação quadrática exige três escalas")
        coefficients = np.polyfit(x, y, 2)
        result = float(coefficients[2])
    elif method == "exponential":
        coefficients = np.polyfit(x, np.log(np.maximum(y, 1e-12)), 1)
        result = float(math.exp(coefficients[1]))
    else:
        raise ValueError("method deve ser linear, quadratic ou exponential")
    return {
        "method": method,
        "extrapolated": result,
        "coefficients": [float(c) for c in coefficients],
    }


def run_zne(
    circuit: QuantumCircuit,
    profile,
    *,
    scales: tuple[int, ...] = (1, 3, 5),
    shots: int = 2048,
    seed: int = 42,
    method: str = "linear",
) -> dict:
    base = _unitary_circuit(circuit)
    model = noise_model_from_profile(profile, base)
    simulator = AerSimulator(noise_model=model, seed_simulator=int(seed))
    rows = []
    for scale in scales:
        folded = fold_circuit(circuit, scale)
        counts = simulator.run(folded, shots=int(shots)).result().get_counts()
        total = sum(int(v) for v in counts.values())
        probabilities = {str(k): int(v) / total for k, v in counts.items()}
        ideal = dist_ideal(folded)
        rows.append(
            {
                "scale": int(scale),
                "tvd": tvd(probabilities, ideal),
                "counts": {str(k): int(v) for k, v in counts.items()},
                "depth": folded.depth(),
            }
        )
    extrapolation = extrapolate(
        [row["scale"] for row in rows],
        [row["tvd"] for row in rows],
        method=method,
    )
    return {
        "schema_version": 1,
        "scales": rows,
        "extrapolation": extrapolation,
        "shots": int(shots),
        "seed": int(seed),
        "limits": (
            "ZNE com folding global e modelo depolarizante; extrapola TVD, "
            "não fidelidade de estado. Não é QEC."
        ),
    }
