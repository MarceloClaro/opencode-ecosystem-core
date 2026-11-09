#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Calibração Rabi da preparação de |1> (R1118).

Mede p1(θ) para vários ângulos e ajusta

    p1(θ) = r0 + A·sin²((θ+ε)/2)

para separar erro de leitura (r0, r1) de desvio coerente (ε). Não executa
hardware e não declara melhora sem validação.
"""
from __future__ import annotations

import math

import numpy as np
from qiskit import QuantumCircuit, qasm2

DEFAULT_ANGLES = (
    math.pi / 4.0,
    math.pi / 2.0,
    3.0 * math.pi / 4.0,
    math.pi,
    5.0 * math.pi / 4.0,
    3.0 * math.pi / 2.0,
    7.0 * math.pi / 4.0,
    2.0 * math.pi,
)


def rabi_calibration_plan(
    qubit: int = 1,
    angles: tuple[float, ...] | list[float] | None = None,
    axes: tuple[str, ...] = ("x", "y"),
) -> dict[str, dict]:
    """Plano de 8 ângulos × 2 eixos (16 circuitos) para calibração Rabi."""
    if angles is None:
        angles = DEFAULT_ANGLES
    else:
        angles = tuple(float(angle) for angle in angles)
    plan: dict[str, dict] = {}
    for axis in axes:
        if axis not in ("x", "y"):
            raise ValueError(f"eixo inválido: {axis}")
        for index, theta in enumerate(angles):
            circuit = QuantumCircuit(max(qubit + 1, 1), 1)
            if axis == "x":
                circuit.rx(theta, qubit)
            else:
                circuit.ry(theta, qubit)
            circuit.measure(qubit, 0)
            key = f"q{qubit}_{axis}_{index}"
            plan[key] = {
                "qasm": qasm2.dumps(circuit),
                "axis": axis,
                "theta": float(theta),
                "index": index,
            }
    return plan


def _fit_axis(points: list[tuple[float, float, float]]) -> dict:
    theta = np.asarray([item[0] for item in points], dtype=float)
    observed = np.asarray([item[1] for item in points], dtype=float)
    sigma = np.asarray([max(item[2], 1e-9) for item in points], dtype=float)
    design = np.column_stack(
        [np.ones_like(theta), np.cos(theta), np.sin(theta)]
    )
    weights = 1.0 / (sigma**2)
    weighted_design = design * np.sqrt(weights)[:, None]
    weighted_observed = observed * np.sqrt(weights)
    beta, *_ = np.linalg.lstsq(weighted_design, weighted_observed, rcond=None)
    residual = observed - design @ beta
    dof = max(1, len(theta) - 3)
    chi2 = float(np.sum((residual / sigma) ** 2))
    covariance = np.linalg.inv(design.T @ (design * weights[:, None]))
    covariance *= max(1.0, chi2 / dof)

    c0, c1, c2 = (float(value) for value in beta)
    radius2 = c1 * c1 + c2 * c2
    contrast = 2.0 * math.sqrt(radius2)
    epsilon = math.atan2(c2, -c1) if radius2 > 1e-18 else 0.0
    r0 = c0 - contrast / 2.0
    r1 = 1.0 - r0 - contrast

    if radius2 > 1e-18:
        grad_contrast = np.array([0.0, 2.0 * c1 / contrast, 2.0 * c2 / contrast])
        grad_epsilon = np.array([0.0, c2 / radius2, -c1 / radius2])
    else:
        grad_contrast = np.zeros(3)
        grad_epsilon = np.zeros(3)
    var_contrast = float(grad_contrast @ covariance @ grad_contrast)
    var_epsilon = float(grad_epsilon @ covariance @ grad_epsilon)
    se_contrast = math.sqrt(max(0.0, var_contrast))
    se_epsilon = math.sqrt(max(0.0, var_epsilon))
    var_r0 = float(covariance[0, 0] + var_contrast / 4.0)
    se_r0 = math.sqrt(max(0.0, var_r0))

    theta_star = (math.pi - epsilon) % (2.0 * math.pi)
    gain = contrast * math.sin(epsilon / 2.0) ** 2
    grad_gain_contrast = math.sin(epsilon / 2.0) ** 2
    grad_gain_epsilon = contrast * math.sin(epsilon / 2.0) * math.cos(epsilon / 2.0)
    cov_contrast_epsilon = float(
        grad_contrast @ covariance @ grad_epsilon
    )
    var_gain = (
        grad_gain_contrast**2 * var_contrast
        + grad_gain_epsilon**2 * var_epsilon
        + 2.0 * grad_gain_contrast * grad_gain_epsilon * cov_contrast_epsilon
    )
    se_gain = math.sqrt(max(0.0, var_gain))

    identified = bool(
        contrast > 0.5
        and -0.5 <= r0 <= 0.5
        and -0.5 <= r1 <= 0.5
        and r0 + r1 < 1.0
        and chi2 / dof < 20.0
        and se_epsilon < 0.2
    )
    corrected = [
        (value - r0) / contrast if contrast > 1e-12 else None
        for value in observed
    ]
    return {
        "identified": identified,
        "n_points": len(points),
        "contrast": contrast,
        "contrast_se": se_contrast,
        "r0": r0,
        "r1": r1,
        "r0_se": se_r0,
        "epsilon": epsilon,
        "epsilon_se": se_epsilon,
        "theta_star": theta_star,
        "gain_vs_pi": gain,
        "gain_vs_pi_se": se_gain,
        "chi2": chi2,
        "dof": dof,
        "chi2_per_dof": chi2 / dof,
        "points": [
            {
                "theta": float(item[0]),
                "p1_observed": float(item[1]),
                "sigma": float(item[2]),
                "p1_corrected": (
                    None if corrected[index] is None else float(corrected[index])
                ),
            }
            for index, item in enumerate(points)
        ],
        "limits": (
            "Ajuste senoidal de 3 parâmetros. Decaimento/depuração podem reduzir "
            "o contraste e enviesar r1; não é GST e não separa todos os erros."
        ),
    }


def fit_rabi_calibration(
    plan: dict[str, dict],
    counts_by_key: dict[str, dict[str, int]],
) -> dict:
    """Ajusta r0, r1, contraste e desvio coerente por eixo."""
    axes: dict[str, list[tuple[float, float, float]]] = {}
    for key, item in plan.items():
        if key not in counts_by_key:
            raise ValueError(f"counts ausente para {key}")
        counts = counts_by_key[key]
        total = sum(int(value) for value in counts.values())
        if total <= 0:
            raise ValueError(f"counts vazios para {key}")
        ones = int(counts.get("1", 0))
        p1 = ones / total
        sigma = math.sqrt(max(p1 * (1.0 - p1), 1e-12) / total)
        axes.setdefault(item["axis"], []).append(
            (float(item["theta"]), p1, sigma)
        )

    fitted = {axis: _fit_axis(points) for axis, points in axes.items()}
    identified = {
        axis: item for axis, item in fitted.items() if item["identified"]
    }
    preferred = "none"
    if len(identified) == 1:
        preferred = next(iter(identified))
    elif len(identified) > 1:
        ordered = sorted(identified, key=lambda axis: abs(fitted[axis]["epsilon"]))
        first, second = ordered[0], ordered[1]
        difference = abs(
            fitted[first]["epsilon"] - fitted[second]["epsilon"]
        )
        combined_se = math.hypot(
            fitted[first]["epsilon_se"], fitted[second]["epsilon_se"]
        )
        if difference > 2.0 * combined_se:
            preferred = first

    if preferred != "none":
        chosen = fitted[preferred]
        theta_star = chosen["theta_star"]
        gain = chosen["gain_vs_pi"]
        gain_se = chosen["gain_vs_pi_se"]
    else:
        theta_star = None
        gain = 0.0
        gain_se = 0.0

    return {
        "schema_version": 1,
        "axes": fitted,
        "preferred_axis": preferred,
        "theta_star": theta_star,
        "gain_vs_pi": gain,
        "gain_vs_pi_se": gain_se,
        "identified": bool(identified),
        "limits": (
            "Calibração local de um qubit. Preferência de eixo só é declarada "
            "quando a diferença de |ε| supera 2 erros padrão combinados. "
            "Ganho estimado não é ganho validado."
        ),
    }
