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
    fit_spam_separation,
    preregister_ci,
    spam_circuits,
    spam_separation_plan,
    uncertainty_report,
    wilson_interval,
)
from .dd import DD_SEQUENCES, dd_plan, insert_dd, pulse_dd_plan, verify_identity
from .pec import (
    depolarizing_quasiprobabilities,
    pauli_channel_inverse,
    pec_plan,
    uniform_depolarizing_rates,
)
from .qec import (
    qec_plan,
    repetition_code_circuit,
    run_repetition_code,
    surface_code_plan,
)
from .zne import extrapolate, fold_circuit, run_zne, zne_applicability

__all__ = [
    "fold_circuit",
    "extrapolate",
    "run_zne",
    "zne_applicability",
    "insert_dd",
    "verify_identity",
    "dd_plan",
    "pulse_dd_plan",
    "DD_SEQUENCES",
    "depolarizing_quasiprobabilities",
    "pauli_channel_inverse",
    "uniform_depolarizing_rates",
    "pec_plan",
    "repetition_code_circuit",
    "run_repetition_code",
    "qec_plan",
    "surface_code_plan",
    "fit_spam",
    "fit_spam_separation",
    "preregister_ci",
    "spam_circuits",
    "spam_separation_plan",
    "crosstalk_metric",
    "drift_detection",
    "wilson_interval",
    "bootstrap_ci",
    "uncertainty_report",
]
