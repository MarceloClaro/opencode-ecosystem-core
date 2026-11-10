"""R1133 — desenho pareado e randomizado para comparação de layouts.

O erro anterior comparou pares físicos diferentes sem randomização. Este
módulo não executa hardware: calcula n, randomiza a ordem dos braços e recusa
comparações confundidas. Também distingue comparação de compiladores no mesmo
par (within-pair) de comparação de layouts (randomized pairs).
"""
from __future__ import annotations

import math

import numpy as np
from scipy.stats import norm

LIMITS = (
    "Planejamento estatístico offline. n é aproximação normal para diferenças "
    "pareadas; não incorpora drift, caudas ou dependência temporal. A decisão "
    "final exige dados e revisão humana; nenhum hardware é executado."
)


def paired_sample_size(
    effect: float,
    sigma: float,
    *,
    alpha: float = 0.05,
    power: float = 0.8,
) -> dict:
    if effect <= 0 or sigma <= 0:
        raise ValueError("effect e sigma devem ser positivos")
    if not 0 < alpha < 1 or not 0 < power < 1:
        raise ValueError("alpha e power devem estar em (0,1)")
    z_alpha = float(norm.ppf(1 - alpha / 2))
    z_power = float(norm.ppf(power))
    n = math.ceil(((z_alpha + z_power) * sigma / effect) ** 2)
    return {
        "n_pairs": int(n),
        "effect": float(effect),
        "sigma": float(sigma),
        "alpha": float(alpha),
        "power": float(power),
        "z_alpha": z_alpha,
        "z_power": z_power,
        "formula": "n = ceil(((z_{1-alpha/2}+z_power)*sigma/effect)^2)",
        "limits": LIMITS,
    }


def randomized_assignment(n_pairs: int, *, seed: int = 0) -> list[str]:
    """Atribuição balanceada AB/BA por par, determinística por seed."""
    if isinstance(n_pairs, bool) or not isinstance(n_pairs, int) or n_pairs < 1:
        raise ValueError("n_pairs deve ser inteiro >= 1")
    half = n_pairs // 2
    labels = ["AB"] * half + ["BA"] * (n_pairs - half)
    rng = np.random.default_rng(int(seed))
    rng.shuffle(labels)
    return labels


def confound_audit(
    baseline_qubits,
    optimized_qubits,
    *,
    randomized: bool,
) -> dict:
    baseline = tuple(int(item) for item in baseline_qubits)
    optimized = tuple(int(item) for item in optimized_qubits)
    if baseline == optimized:
        return {
            "allowed": True,
            "design": "within_pair",
            "reason": "mesmo par físico; isola compilador/estratégia",
        }
    if randomized:
        return {
            "allowed": True,
            "design": "layout_randomized",
            "reason": "pares físicos diferentes, mas atribuição randomizada e pareada",
        }
    return {
        "allowed": False,
        "design": "confounded",
        "reason": "pares físicos diferentes sem randomização; não isola layout de qualidade do qubit",
    }


def build_preregistration(
    *,
    n_pairs: int,
    circuits_per_pair: int = 4,
    effect: float = 0.01,
    sigma: float = 0.02,
    seed: int = 1133,
    baseline_qubits=(0, 1),
    optimized_qubits=(106, 107),
    randomized: bool = True,
) -> dict:
    if circuits_per_pair < 1:
        raise ValueError("circuits_per_pair deve ser >= 1")
    sample = paired_sample_size(effect, sigma)
    confound = confound_audit(
        baseline_qubits, optimized_qubits, randomized=randomized
    )
    enough = n_pairs >= sample["n_pairs"]
    return {
        "schema_version": 1,
        "protocol": "r1133-layout-paired-preregistration",
        "n_pairs": int(n_pairs),
        "n_required": sample["n_pairs"],
        "enough_pairs": bool(enough),
        "circuits_per_pair": int(circuits_per_pair),
        "effect": float(effect),
        "sigma": float(sigma),
        "alpha": sample["alpha"],
        "power": sample["power"],
        "seed": int(seed),
        "randomized": bool(randomized),
        "assignment": randomized_assignment(n_pairs, seed=seed),
        "baseline_qubits": list(baseline_qubits),
        "optimized_qubits": list(optimized_qubits),
        "confound": confound,
        "primary_metric": "diferença pareada de TVD mitigada",
        "covariate": "r1 do par",
        "decision_rule": (
            "comparar somente se enough_pairs e confound.allowed; "
            "reportar IC pareado e efeito mínimo de 0,01"
        ),
        "hardware_submission_allowed": False,
        "limits": LIMITS,
    }
