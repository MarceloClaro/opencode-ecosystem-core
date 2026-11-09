#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SPAM, crosstalk, drift e incerteza (R1114)."""
from __future__ import annotations

import math
from statistics import mean, pstdev

import numpy as np
from qiskit import QuantumCircuit, qasm2
from scipy.optimize import least_squares
from scipy.stats import norm


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


def spam_separation_plan(
    qubits: list[int],
    ks: tuple[int, ...] = (1, 3, 5),
) -> dict[str, str]:
    """Circuitos de pulsos pi repetidos para separar preparação de leitura."""
    output = {}
    for q in qubits:
        for k in ks:
            circuit = QuantumCircuit(max(qubits) + 1, 1)
            for _ in range(int(k)):
                circuit.rx(math.pi, q)
            circuit.measure(q, 0)
            output[f"q{q}_k{int(k)}"] = qasm2.dumps(circuit)
    return output


def _spam_p1(k: int, e: float, r0: float, r1: float) -> float:
    p0 = (1.0 + (1.0 - 2.0 * e) ** int(k)) / 2.0
    return (1.0 - r1) + p0 * (r0 - (1.0 - r1))


def fit_spam_separation(counts_by_k: dict) -> dict:
    """Ajusta e (erro por pulso), r0 e r1 a partir de k=1,3,5."""
    items = []
    for key, counts in counts_by_k.items():
        k = int(key)
        total = sum(int(v) for v in counts.values())
        if total <= 0:
            raise ValueError(f"counts vazios para k={k}")
        items.append((k, int(counts.get("1", 0)) / total))
    items.sort()
    if len(items) < 3:
        raise ValueError("SPAM separation exige ao menos três valores de k")
    def residuals(x):
        e, r0, r1 = x
        return [
            _spam_p1(k, e, r0, r1) - observed
            for k, observed in items
        ]
    result = least_squares(
        residuals,
        x0=[0.01, 0.02, 0.03],
        bounds=([0.0, 0.0, 0.0], [0.5, 0.5, 0.5]),
    )
    e, r0, r1 = [float(v) for v in result.x]
    residual_norm = float(result.cost)
    at_bound = (
        min(abs(e - 0.5), abs(r0 - 0.5), abs(r1 - 0.5)) < 1e-6
        or min(abs(e), abs(r0), abs(r1)) < 1e-6
    )
    identified = (
        not at_bound
        and 0.001 < e < 0.499
        and 0.001 < r0 < 0.499
        and 0.001 < r1 < 0.499
        and residual_norm < 1e-4
    )
    return {
        "schema_version": 1,
        "identified": identified,
        "reason": (
            "ajuste identificável"
            if identified
            else "ajuste no limite ou resíduo alto; e/r0/r1 não são físicos"
        ),
        "prep_error_per_pi": e,
        "readout_p1_given_prep0": r0,
        "readout_p0_given_prep1": r1,
        "ks": [k for k, _ in items],
        "observed_p1": {str(k): p1 for k, p1 in items},
        "predicted_p1": {
            str(k): _spam_p1(k, e, r0, r1) for k, _ in items
        },
        "residual_norm": residual_norm,
        "limits": (
            "Modelo de pulsos pi independentes com erro e e leitura r0/r1; "
            "não separa crosstalk, drift ou erro correlacionado. |1> usa "
            "rx(pi), então a preparação do |1> está no modelo."
        ),
    }


def preregister_ci(
    p: float,
    half_width: float,
    *,
    confidence: float = 0.95,
) -> dict:
    """Calcula n para meia-largura Wilson pré-registrada."""
    if not 0.0 < p < 1.0:
        raise ValueError("p deve estar em (0, 1)")
    if not 0.0 < half_width < 1.0:
        raise ValueError("half_width deve estar em (0, 1)")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence deve estar em (0, 1)")
    z = float(norm.ppf((1.0 + confidence) / 2.0))
    estimate = max(1, int((z * z * p * (1.0 - p)) / (half_width**2)))
    n = max(1, int(estimate * 0.5))
    for candidate in range(n, n + 2_000_000):
        interval = wilson_interval(
            round(p * candidate), candidate, z=z
        )
        observed_half = (interval["high"] - interval["low"]) / 2.0
        if observed_half <= half_width:
            return {
                "schema_version": 1,
                "p": p,
                "half_width": half_width,
                "confidence": confidence,
                "z": z,
                "n": candidate,
                "expected_interval": interval,
                "observed_half_width": observed_half,
                "limits": "Cálculo pré-registrado; não garante poder estatístico.",
            }
    raise ValueError("não foi possível atingir a meia-largura")
