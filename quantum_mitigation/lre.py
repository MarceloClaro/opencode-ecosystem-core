"""R1132 — Layerwise Richardson extrapolation (LRE) para ZNE.

Em vez de assumir uma única escala global monotônica, a LRE amplifica cada
camada independentemente e combina as configurações por interpolação de
Lagrange multivariada. É um planejador offline; não executa hardware.

Fonte: Russo & Mari, Phys. Rev. A 110, 062420 (2024),
DOI 10.1103/PhysRevA.110.062420.
"""
from __future__ import annotations

import itertools

import numpy as np

SCALES = (1.0, 2.0, 3.0)
LIMITS = (
    "LRE planejada para ruído aditivo por camada; não executa hardware. "
    "A interpolação é exata para o modelo multilinear nas escalas; ruído "
    "não linear, drift e interações entre camadas exigem mais escalas e "
    "validação. Não substitui ZNE global nem QEC."
)


def lagrange_coefficients(scales=SCALES, target: float = 0.0) -> np.ndarray:
    """Coeficientes 1D de Lagrange para o alvo (por padrão, ruído zero)."""
    points = np.asarray(scales, dtype=float)
    if points.ndim != 1 or len(points) < 2 or len(set(points.tolist())) != len(points):
        raise ValueError("escalas devem ser distintas e em número >= 2")
    coefficients = np.zeros_like(points)
    for i, point in enumerate(points):
        basis = 1.0
        for j, other in enumerate(points):
            if i != j:
                basis *= (target - other) / (point - other)
        coefficients[i] = basis
    if not np.isclose(coefficients.sum(), 1.0):
        raise ValueError("coeficientes de Lagrange não somam 1")
    return coefficients


def lre_design(layers: int, scales=SCALES, target: float = 0.0) -> dict:
    """Grade completa com coeficientes multiplicativos por configuração."""
    if isinstance(layers, bool) or not isinstance(layers, int) or layers < 1:
        raise ValueError("layers deve ser inteiro >= 1")
    scales = tuple(float(value) for value in scales)
    base = lagrange_coefficients(scales, target)
    configurations = list(itertools.product(scales, repeat=layers))
    coefficients = []
    for configuration in configurations:
        coefficient = 1.0
        for value in configuration:
            coefficient *= base[scales.index(value)]
        coefficients.append(float(coefficient))
    return {
        "layers": layers,
        "scales": list(scales),
        "target": float(target),
        "configurations": [list(item) for item in configurations],
        "coefficients": coefficients,
        "n_configurations": len(configurations),
        "sum_coefficients": float(sum(coefficients)),
    }


def global_design(layers: int, scales=SCALES, target: float = 0.0) -> dict:
    """Escalonamento global: todas as camadas na mesma escala."""
    if isinstance(layers, bool) or not isinstance(layers, int) or layers < 1:
        raise ValueError("layers deve ser inteiro >= 1")
    scales = tuple(float(value) for value in scales)
    coefficients = lagrange_coefficients(scales, target)
    return {
        "layers": layers,
        "scales": list(scales),
        "target": float(target),
        "configurations": [[value] * layers for value in scales],
        "coefficients": [float(value) for value in coefficients],
        "n_configurations": len(scales),
        "sum_coefficients": 1.0,
    }


def estimate(values, design: dict) -> float:
    values = np.asarray(values, dtype=float)
    coefficients = np.asarray(design["coefficients"], dtype=float)
    if values.shape != coefficients.shape:
        raise ValueError("valores e coeficientes com formas diferentes")
    return float(values @ coefficients)


def multilinear_model(
    configuration,
    *,
    offset: float = 0.9,
    slopes=(0.02, 0.03, 0.05),
) -> float:
    """Modelo de teste: E(x)=offset + soma_i slope_i x_i; x=0 é zero-ruído."""
    configuration = np.asarray(configuration, dtype=float)
    slopes = np.asarray(slopes[: len(configuration)], dtype=float)
    if len(slopes) != len(configuration):
        raise ValueError("slopes devem cobrir as camadas")
    return float(offset + np.sum(slopes * configuration))


def synthetic_audit(layers: int = 3) -> dict:
    """Mostra que a LRE recupera o valor zero-ruído no modelo multilinear."""
    design = lre_design(layers)
    values = [multilinear_model(configuration) for configuration in design["configurations"]]
    estimate_lre = estimate(values, design)
    global_plan = global_design(layers)
    global_values = [
        multilinear_model(configuration) for configuration in global_plan["configurations"]
    ]
    estimate_global = estimate(global_values, global_plan)
    truth = multilinear_model([0.0] * layers)
    return {
        "schema_version": 1,
        "layers": layers,
        "truth_zero_noise": truth,
        "lre_estimate": estimate_lre,
        "lre_error": abs(estimate_lre - truth),
        "global_estimate": estimate_global,
        "global_error": abs(estimate_global - truth),
        "lre_configurations": design["n_configurations"],
        "global_configurations": global_plan["n_configurations"],
        "limits": LIMITS,
        "hardware_executed": False,
    }
