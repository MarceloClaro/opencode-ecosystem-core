#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SPAM, crosstalk, drift e incerteza (R1114)."""
from __future__ import annotations

import math
from statistics import mean, pstdev

import numpy as np
from qiskit import QuantumCircuit, qasm2


def fit_spam(counts0: dict[str, int], counts1: dict[str, int]) -> dict:
    total0 = sum(int(v) for v in counts0.values())
    total1 = sum(int(v) for v in counts1.values())
    if total0 <= 0 or total1 <= 0:
        raise ValueError("counts vazios")
    p1_given_0 = int(counts0.get("1", 0)) / total0
    p0_given_1 = int(counts1.get("0", 0)) / total1
    return {
        "schema_version": 1,
        "p1_given_prep0": p1_given_0,
        "p0_given_prep1": p0_given_1,
        "readout_error_symmetric": 0.5 * (p1_given_0 + p0_given_1),
        "counts0_total": total0,
        "counts1_total": total1,
        "note": (
            "|1> é preparado com rx(pi); p0_given_prep1 inclui preparação do "
            "|1> e leitura. A separação completa exige experimento adicional."
        ),
    }


def spam_circuits(qubits: list[int]) -> dict[str, str]:
    output = {}
    for state in ("0", "1"):
        width = max(qubits) + 1
        circuit = QuantumCircuit(width, 1)
        if state == "1":
            for q in qubits:
                circuit.rx(math.pi, q)
        for q in qubits:
            circuit.measure(q, 0)
        output[state] = qasm2.dumps(circuit)
    return output


def crosstalk_metric(isolated_error: float, simultaneous_error: float) -> dict:
    isolated = float(isolated_error)
    simultaneous = float(simultaneous_error)
    if isolated < 0 or simultaneous < 0:
        raise ValueError("erros devem ser >= 0")
    ratio = simultaneous / isolated if isolated > 0 else None
    return {
        "schema_version": 1,
        "isolated_error": isolated,
        "simultaneous_error": simultaneous,
        "excess": simultaneous - isolated,
        "relative": (simultaneous - isolated) / isolated if isolated > 0 else None,
        "ratio": ratio,
        "limits": (
            "Métrica descritiva; não identifica mecanismo nem prova crosstalk "
            "em hardware."
        ),
    }


def drift_detection(
    values: list[float],
    timestamps: list[str] | None = None,
) -> dict:
    data = np.asarray(values, dtype=float)
    if data.size < 2:
        raise ValueError("drift exige ao menos dois valores")
    x = np.arange(data.size, dtype=float)
    slope = float(np.polyfit(x, data, 1)[0])
    mean_value = float(np.mean(data))
    centered = data - mean_value
    cusum = np.cumsum(centered)
    return {
        "schema_version": 1,
        "n": int(data.size),
        "mean": mean_value,
        "std": float(np.std(data, ddof=1)),
        "slope_per_step": slope,
        "relative_drift": (
            float((data[-1] - data[0]) / mean_value) if mean_value != 0 else None
        ),
        "cusum_max_abs": float(np.max(np.abs(cusum))),
        "timestamps": timestamps or [],
        "limits": (
            "Tendência e CUSUM descritivos; não corrigem calibração nem provam "
            "deriva física."
        ),
    }


def wilson_interval(successes: int, trials: int, z: float = 1.96) -> dict:
    if trials <= 0:
        raise ValueError("trials deve ser > 0")
    p = successes / trials
    denominator = 1.0 + z**2 / trials
    center = (p + z**2 / (2.0 * trials)) / denominator
    margin = (
        z
        * math.sqrt(p * (1.0 - p) / trials + z**2 / (4.0 * trials**2))
        / denominator
    )
    return {
        "p": p,
        "low": max(0.0, center - margin),
        "high": min(1.0, center + margin),
        "z": z,
        "trials": trials,
    }


def bootstrap_ci(
    values: list[float],
    *,
    n_bootstrap: int = 2000,
    confidence: float = 0.95,
    seed: int = 42,
) -> dict:
    data = np.asarray(values, dtype=float)
    if data.size < 2:
        raise ValueError("bootstrap exige ao menos dois valores")
    rng = np.random.default_rng(int(seed))
    samples = rng.choice(data, size=(int(n_bootstrap), data.size), replace=True)
    means = samples.mean(axis=1)
    alpha = (1.0 - confidence) / 2.0
    return {
        "mean": float(np.mean(data)),
        "low": float(np.quantile(means, alpha)),
        "high": float(np.quantile(means, 1.0 - alpha)),
        "confidence": confidence,
        "n_bootstrap": int(n_bootstrap),
        "n": int(data.size),
    }


def uncertainty_report(values: list[float]) -> dict:
    data = [float(v) for v in values]
    if not data:
        raise ValueError("values vazio")
    return {
        "schema_version": 1,
        "n": len(data),
        "mean": mean(data),
        "std": pstdev(data) if len(data) > 1 else 0.0,
        "min": min(data),
        "max": max(data),
        "bootstrap": bootstrap_ci(data) if len(data) > 1 else None,
        "limits": (
            "Dispersão entre repetições; não é prova estatística universal. "
            "Três repetições não estimam caudas extremas."
        ),
    }
