#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validação de RC: baseline vs twirlado (R1123).

Circuito Clifford de 2 qubits, TVD contra a distribuição ideal e bootstrap
aninhado. Não executa hardware por si só.
"""
from __future__ import annotations

import math

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from .randomized_compiling import pauli_frame_pass


def base_circuit() -> QuantumCircuit:
    """Circuito Clifford de 2 qubits usado na validação."""
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.h(1)
    circuit.cz(0, 1)
    circuit.h(0)
    circuit.measure([0, 1], [0, 1])
    return circuit


def _statevector(circuit: QuantumCircuit) -> Statevector:
    clean = circuit.remove_final_measurements(inplace=False)
    return Statevector.from_instruction(clean)


def ideal_probabilities(circuit: QuantumCircuit) -> dict[str, float]:
    """Distribuição ideal nos 4 resultados de 2 qubits."""
    probabilities = _statevector(circuit).probabilities_dict()
    return {
        f"{index:02b}": float(probabilities.get(f"{index:02b}", 0.0))
        for index in range(4)
    }


def _bits(key: str, num_qubits: int) -> str:
    text = str(key).lower()
    if text.startswith("0x"):
        text = text[2:]
    text = text.replace(" ", "")
    return text.zfill(num_qubits)[-num_qubits:]


def probabilities(counts: dict, num_qubits: int = 2) -> dict[str, float]:
    total = sum(int(value) for value in counts.values())
    if total <= 0:
        raise ValueError("counts vazios")
    output = {f"{index:02b}": 0 for index in range(2**num_qubits)}
    for key, value in counts.items():
        output[_bits(key, num_qubits)] += int(value)
    return {key: value / total for key, value in output.items()}


def tvd(counts: dict, ideal: dict[str, float], num_qubits: int = 2) -> float:
    observed = probabilities(counts, num_qubits)
    keys = set(observed) | set(ideal)
    return 0.5 * sum(
        abs(observed.get(key, 0.0) - float(ideal.get(key, 0.0)))
        for key in keys
    )


def rc_validation_plan(seeds: tuple[int, ...] | list[int]) -> dict:
    """Quatro baseline idênticos e quatro twirls distintos."""
    seeds = tuple(int(seed) for seed in seeds)
    base = base_circuit()
    baseline = [base.copy() for _ in seeds]
    twirled = []
    records = []
    for seed in seeds:
        result = pauli_frame_pass(base, seed=seed)
        twirled.append(result["circuit"])
        records.append(
            {
                "seed": seed,
                "n_twirls": result["n_twirls"],
                "twirls": result["twirls"],
            }
        )
    return {
        "baseline": baseline,
        "twirled": twirled,
        "seeds": list(seeds),
        "twirls": records,
        "ideal": ideal_probabilities(base),
    }


def _resample_mean_tvd(
    count_list: list[dict],
    ideal: dict[str, float],
    rng: np.random.Generator,
    num_qubits: int = 2,
) -> float:
    means = []
    keys = list(ideal)
    for counts in count_list:
        probs = probabilities(counts, num_qubits)
        total = sum(int(value) for value in counts.values())
        sampled = rng.multinomial(total, [probs[key] for key in keys])
        p_obs = sampled / total
        means.append(
            0.5 * sum(abs(p_obs[i] - ideal[key]) for i, key in enumerate(keys))
        )
    indices = rng.integers(0, len(means), size=len(means))
    return float(np.mean([means[index] for index in indices]))


def bootstrap_tvd_difference(
    baseline_counts: list[dict],
    twirled_counts: list[dict],
    ideal: dict[str, float],
    *,
    n_bootstrap: int = 2000,
    seed: int = 42,
) -> dict:
    """Bootstrap aninhado: shots dentro do job e jobs dentro do braço."""
    rng = np.random.default_rng(int(seed))
    differences = []
    for _ in range(int(n_bootstrap)):
        baseline = _resample_mean_tvd(baseline_counts, ideal, rng)
        twirled = _resample_mean_tvd(twirled_counts, ideal, rng)
        differences.append(twirled - baseline)
    array = np.asarray(differences, dtype=float)
    return {
        "schema_version": 1,
        "n_bootstrap": int(n_bootstrap),
        "mean_difference": float(np.mean(array)),
        "low": float(np.quantile(array, 0.025)),
        "high": float(np.quantile(array, 0.975)),
        "std": float(np.std(array, ddof=1)),
        "baseline_mean_tvd": float(
            np.mean([tvd(counts, ideal) for counts in baseline_counts])
        ),
        "twirled_mean_tvd": float(
            np.mean([tvd(counts, ideal) for counts in twirled_counts])
        ),
        "limits": (
            "Bootstrap de TVD com jobs finitos; não captura drift sistemático "
            "fora dos dois conjuntos. Diferença negativa favorece o twirl."
        ),
    }


def decision(summary: dict) -> dict:
    if summary["high"] < 0:
        verdict = "twirled melhor"
        reason = "IC 95% inteiro abaixo de zero"
    elif summary["low"] > 0:
        verdict = "twirled pior"
        reason = "IC 95% inteiro acima de zero"
    else:
        verdict = "sem efeito detectável"
        reason = "IC 95% inclui zero"
    return {
        "verdict": verdict,
        "reason": reason,
        "difference": summary["mean_difference"],
        "ci": [summary["low"], summary["high"]],
    }
