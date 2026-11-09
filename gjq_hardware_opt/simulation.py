#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simulação de plano GJQ antes do hardware (R1112).

O simulador remapeia os qubits físicos usados para 0..k-1, monta um modelo
depolarizante por porta e leitura a partir do perfil e compara a distribuição
ruidosa com a ideal. Não é previsão de hardware.
"""
from __future__ import annotations

import math
from typing import Any

from qiskit import QuantumCircuit, qasm2
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

from quantum_efficiency.metrics import dist_ideal, tvd

from .profile import HardwareProfile


def _remap(circuit: QuantumCircuit, used_physical: list[int]) -> tuple[QuantumCircuit, dict[int, int]]:
    local = {int(phys): index for index, phys in enumerate(used_physical)}
    compact = QuantumCircuit(len(used_physical), circuit.num_clbits)
    for instruction in circuit.data:
        qargs = [
            compact.qubits[local[circuit.find_bit(q).index]]
            for q in instruction.qubits
        ]
        cargs = [
            compact.clbits[circuit.find_bit(c).index]
            for c in instruction.clbits
        ]
        compact.append(instruction.operation, qargs, cargs)
    return compact, local


def _noise_model(circuit: QuantumCircuit, local: dict[int, int], profile: HardwareProfile) -> NoiseModel:
    model = NoiseModel()
    reverse = {local_index: physical for physical, local_index in local.items()}
    seen: set[tuple[str, tuple[int, ...]]] = set()
    for instruction in circuit.data:
        name = instruction.operation.name
        if name in {"barrier", "delay"}:
            continue
        local_indices = [circuit.find_bit(q).index for q in instruction.qubits]
        physical = [reverse[index] for index in local_indices]
        qubits = [local[q] for q in physical]
        key = (name, tuple(qubits))
        if key in seen:
            continue
        seen.add(key)
        if name == "measure":
            error = profile.readout_error.get(physical[0], profile.default_readout_error)
            p1_given_0 = error
            p0_given_1 = error
            readout = ReadoutError(
                [[1.0 - p1_given_0, p0_given_1], [p1_given_0, 1.0 - p0_given_1]]
            )
            model.add_readout_error(readout, qubits)
        elif len(qubits) == 1:
            if name == "rz":
                continue
            error = profile.oneq_error_for(name, physical[0])
            if error > 0:
                model.add_quantum_error(
                    depolarizing_error(error, 1), [name], qubits
                )
        elif len(qubits) == 2:
            error = profile.twoq_error_for(name, physical[0], physical[1])
            if error > 0:
                model.add_quantum_error(
                    depolarizing_error(error, 2), [name], qubits
                )
    return model


def simulate_case(
    qasm_text: str,
    used_physical: list[int],
    profile: HardwareProfile,
    shots: int,
    *,
    seed: int = 42,
) -> dict[str, Any]:
    circuit = qasm2.loads(qasm_text)
    used = sorted(int(q) for q in used_physical)
    compact, local = _remap(circuit, used)
    model = _noise_model(compact, local, profile)
    simulator = AerSimulator(noise_model=model, seed_simulator=int(seed))
    counts = simulator.run(compact, shots=int(shots)).result().get_counts()
    total = sum(int(v) for v in counts.values())
    if total <= 0:
        raise RuntimeError("simulação sem counts")
    noisy = {str(k): int(v) / total for k, v in counts.items()}
    ideal = {str(k): float(v) for k, v in dist_ideal(compact).items()}
    return {
        "used_physical": used,
        "local_map": {str(k): v for k, v in local.items()},
        "counts": {str(k): int(v) for k, v in counts.items()},
        "noisy_probabilities": noisy,
        "ideal_probabilities": ideal,
        "tvd_noisy_vs_ideal": tvd(noisy, ideal),
        "shots": int(shots),
        "total": total,
        "noise_model": {
            "kind": "depolarizing_per_gate_and_readout",
            "source": "perfil do backend",
        },
    }


def simulate_plan(
    plan: dict[str, Any],
    profile: HardwareProfile,
    *,
    shots: int,
    seed: int = 42,
) -> dict[str, Any]:
    baseline = simulate_case(
        plan["baseline"]["qasm2"],
        plan["baseline"]["used_physical"],
        profile,
        shots,
        seed=seed,
    )
    optimized = simulate_case(
        plan["optimized"]["qasm2"],
        plan["optimized"]["used_physical"],
        profile,
        shots,
        seed=seed,
    )
    ideal_equivalence = tvd(
        baseline["ideal_probabilities"], optimized["ideal_probabilities"]
    )
    gate_ok = (
        baseline["total"] == int(shots)
        and optimized["total"] == int(shots)
        and math.isfinite(ideal_equivalence)
        and ideal_equivalence <= 1e-9
    )
    winner = (
        "baseline"
        if baseline["tvd_noisy_vs_ideal"] <= optimized["tvd_noisy_vs_ideal"]
        else "optimized"
    )
    return {
        "schema_version": 1,
        "baseline": baseline,
        "optimized": optimized,
        "ideal_equivalence_tvd": ideal_equivalence,
        "gate_ok": gate_ok,
        "simulated_winner": winner,
        "limits": (
            "Simulação com modelo depolarizante derivado do perfil; não é "
            "execução física e não prevê fidelidade de hardware."
        ),
    }
