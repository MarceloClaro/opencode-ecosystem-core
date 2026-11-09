#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mitigação e correção de erro quântico (SPEC-935-R1114).

Módulos:

- ``zne``: zero-noise extrapolation;
- ``dd``: dynamical decoupling circuit-level;
- ``pec``: probabilistic error cancellation (canal depolarizante 1q);
- ``qec``: código de repetição de 3 qubits para bit-flip;
- ``characterization``: SPAM, crosstalk, drift e incerteza.
"""
from .characterization import (
    bootstrap_ci,
    crosstalk_metric,
    drift_detection,
    fit_spam,
    spam_circuits,
    uncertainty_report,
    wilson_interval,
)
from .dd import DD_SEQUENCES, dd_plan, insert_dd, verify_identity
from .pec import depolarizing_quasiprobabilities, pec_plan
from .qec import qec_plan, repetition_code_circuit, run_repetition_code
from .zne import extrapolate, fold_circuit, run_zne

__all__ = [
    "fold_circuit",
    "extrapolate",
    "run_zne",
    "insert_dd",
    "verify_identity",
    "dd_plan",
    "DD_SEQUENCES",
    "depolarizing_quasiprobabilities",
    "pec_plan",
    "repetition_code_circuit",
    "run_repetition_code",
    "qec_plan",
    "fit_spam",
    "spam_circuits",
    "crosstalk_metric",
    "drift_detection",
    "wilson_interval",
    "bootstrap_ci",
    "uncertainty_report",
]
