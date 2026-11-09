#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Probabilistic error cancellation — planejador 1q (R1114)."""
from __future__ import annotations

import math


def depolarizing_quasiprobabilities(p: float) -> dict:
    """Quasi-probabilidades do inverso do canal depolarizante 1q.

    O canal é ``(1-p) rho + p/3 (X rho X + Y rho Y + Z rho Z)``.
    A inversão usa ``q_I = 1 + p/lambda`` e ``q_P = -p/(3 lambda)``,
    com ``lambda = 1 - 4p/3``. ``gamma`` é o overhead de amostragem.
    """
    p = float(p)
    if not 0.0 <= p < 0.75:
        raise ValueError("p deve estar em [0, 0.75)")
    lam = 1.0 - 4.0 * p / 3.0
    q = -p / (3.0 * lam)
    q_i = 1.0 + p / lam
    gamma = q_i + 3.0 * abs(q)
    return {
        "I": q_i,
        "X": q,
        "Y": q,
        "Z": q,
        "lambda": lam,
        "gamma": gamma,
    }


def pec_plan(circuit, profile, *, target_relative_error: float = 0.01) -> dict:
    """Planeja PEC para portas 1q; 2q é marcado como não implementado."""
    if not 0.0 < target_relative_error < 1.0:
        raise ValueError("target_relative_error deve estar em (0, 1)")
    gates = []
    gamma_total = 1.0
    warnings = []
    for instruction in circuit.data:
        name = instruction.operation.name
        if name in {"measure", "barrier", "reset", "delay"}:
            continue
        if len(instruction.qubits) != 1:
            warnings.append(
                f"PEC 2q não implementado; porta {name!r} ignorada no overhead"
            )
            continue
        if name == "rz":
            continue
        q = circuit.find_bit(instruction.qubits[0]).index
        error = profile.oneq_error_for(name, q)
        if error <= 0:
            continue
        quasi = depolarizing_quasiprobabilities(error)
        gamma_total *= quasi["gamma"]
        gates.append(
            {
                "gate": name,
                "qubit": q,
                "error": error,
                "q_I": quasi["I"],
                "q_X": quasi["X"],
                "q_Y": quasi["Y"],
                "q_Z": quasi["Z"],
                "gamma": quasi["gamma"],
            }
        )
    samples = (gamma_total / target_relative_error) ** 2
    return {
        "schema_version": 1,
        "gates_1q": gates,
        "gamma_total": gamma_total,
        "target_relative_error": target_relative_error,
        "samples_required": samples,
        "warnings": sorted(set(warnings)),
        "limits": (
            "Planejador PEC para canal depolarizante 1q; 2q não implementado. "
            "O sampling é uma estimativa, não uma execução em hardware. "
            "PEC não é QEC."
        ),
    }
