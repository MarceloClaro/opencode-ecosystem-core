"""Compatibilidade: N-of-1 canônico em core_cognition.n_of_1 (R1150).

Este módulo não implementa uma segunda política. Ele reexporta o validador de
protocolo e o runner/SCED de `core_cognition.n_of_1`.

Não substitui participante, ética, consentimento ou supervisão clínica.
"""
from __future__ import annotations

from core_cognition.n_of_1 import (
    LIMITS,
    REQUIRED_PROTOCOL,
    SCED_LIMITS,
    generate_sequence,
    lag1_autocorrelation,
    lock_preregistration,
    nap,
    pem,
    permutation_test_nap,
    run_n_of_1,
    tau_u,
    verify_lock,
)

__all__ = [
    "LIMITS",
    "REQUIRED_PROTOCOL",
    "SCED_LIMITS",
    "generate_sequence",
    "lag1_autocorrelation",
    "lock_preregistration",
    "nap",
    "pem",
    "permutation_test_nap",
    "run_n_of_1",
    "tau_u",
    "verify_lock",
]
