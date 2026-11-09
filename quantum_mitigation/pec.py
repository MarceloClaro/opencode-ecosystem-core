#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PEC por inversão de canal Pauli (1q e 2q) — R1115.

A representação Pauli-Lindblad fornece taxas de erro por operador de Pauli.
Aqui invertemos o canal de Pauli resultante e calculamos as quasi-probabilidades
e o overhead de amostragem. Para um perfil que só traz um erro escalar,
assumimos depolarização uniforme e declaramos essa hipótese.
"""
from __future__ import annotations

from itertools import product

PAULIS = ("I", "X", "Y", "Z")
_MAP = {"I": (0, 0), "X": (1, 0), "Z": (0, 1), "Y": (1, 1)}


def pauli_labels(n_qubits: int) -> list[str]:
    if n_qubits < 1:
        raise ValueError("n_qubits deve ser >= 1")
    return ["".join(parts) for parts in product(PAULIS, repeat=n_qubits)]


def _symplectic(a: str, b: str) -> int:
    total = 0
    for ca, cb in zip(a, b):
        xa, za = _MAP[ca]
        xb, zb = _MAP[cb]
        total += xa * zb + za * xb
    return total % 2


def uniform_depolarizing_rates(p: float, n_qubits: int = 1) -> dict[str, float]:
    labels = pauli_labels(n_qubits)
    identity = "I" * n_qubits
    count = len(labels) - 1
    return {
        label: float(p) / count
        for label in labels
        if label != identity
    }


def pauli_channel_inverse(
    error_rates: dict[str, float],
    n_qubits: int = 1,
) -> dict:
    """Inverte um canal de Pauli e devolve quasi-probabilidades e γ.

    ``error_rates`` mapeia rótulos Pauli não-identidade para probabilidades.
    A identidade recebe ``1 - soma``.
    """
    labels = pauli_labels(n_qubits)
    identity = "I" * n_qubits
    rate = {
        label: float(error_rates.get(label, 0.0))
        for label in labels
        if label != identity
    }
    total = sum(rate.values())
    if total >= 1.0:
        raise ValueError("a soma das taxas de erro deve ser < 1")
    rate[identity] = 1.0 - total
    lam = {
        q: sum(
            rate[p] * ((-1) ** _symplectic(p, q))
            for p in labels
        )
        for q in labels
    }
    if any(abs(value) < 1e-12 for value in lam.values()):
        raise ValueError("canal não inversível: lambda nulo")
    q = {
        p: sum(
            ((-1) ** _symplectic(p, target)) / lam[target]
            for target in labels
        ) / len(labels)
        for p in labels
    }
    gamma = sum(abs(value) for value in q.values())
    return {
        "n_qubits": n_qubits,
        "labels": labels,
        "p": rate,
        "lambda": lam,
        "q": q,
        "gamma": gamma,
    }


def depolarizing_quasiprobabilities(p: float) -> dict:
    """Compatibilidade 1q: retorna coeficientes I/X/Y/Z e gamma."""
    result = pauli_channel_inverse(
        uniform_depolarizing_rates(p, 1), 1
    )
    return {
        "I": result["q"]["I"],
        "X": result["q"]["X"],
        "Y": result["q"]["Y"],
        "Z": result["q"]["Z"],
        "gamma": result["gamma"],
    }


def pec_plan(circuit, profile, *, target_relative_error: float = 0.01) -> dict:
    """Planeja PEC para portas 1q e 2q via inversão de canal Pauli."""
    if not 0.0 < target_relative_error < 1.0:
        raise ValueError("target_relative_error deve estar em (0, 1)")
    gates = []
    gamma_total = 1.0
    warnings = []
    for instruction in circuit.data:
        name = instruction.operation.name
        if name in {"measure", "barrier", "reset", "delay"}:
            continue
        qubits = [
            circuit.find_bit(q).index for q in instruction.qubits
        ]
        if len(qubits) == 1:
            if name == "rz":
                continue
            error = profile.oneq_error_for(name, qubits[0])
            n_qubits = 1
        elif len(qubits) == 2:
            error = profile.twoq_error_for(name, qubits[0], qubits[1])
            n_qubits = 2
        else:
            warnings.append(
                f"porta {name!r} com {len(qubits)} qubits ignorada no PEC"
            )
            continue
        if error <= 0:
            continue
        inverse = pauli_channel_inverse(
            uniform_depolarizing_rates(error, n_qubits), n_qubits
        )
        gamma_total *= inverse["gamma"]
        gates.append(
            {
                "gate": name,
                "qubits": qubits,
                "n_qubits": n_qubits,
                "error": error,
                "gamma": inverse["gamma"],
                "q_I": inverse["q"]["I" * n_qubits],
                "non_identity_quasi": {
                    label: value
                    for label, value in inverse["q"].items()
                    if label != "I" * n_qubits
                },
            }
        )
    samples = (gamma_total / target_relative_error) ** 2
    return {
        "schema_version": 1,
        "gates": gates,
        "gamma_total": gamma_total,
        "target_relative_error": target_relative_error,
        "samples_required": samples,
        "warnings": sorted(set(warnings)),
        "limits": (
            "Inversão de canal Pauli; o perfil fornece um erro escalar, então "
            "as taxas por Pauli são uniformes (depolarização). Um modelo "
            "Pauli-Lindblad completo exige taxas caracterizadas por operador. "
            "PEC não é QEC; 2q está incluído no planejamento, não executado."
        ),
    }
