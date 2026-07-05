# -*- coding: utf-8 -*-
"""
Pacote reasoning — Motores de Raciocínio + Módulo Quântico
==========================================================
4 motores (Z3, SymPy, Kanren, Critical) com fallbacks stdlib e
simulador quântico statevector (2 a 100 qubits, 5 seeds padrão).
"""

from reasoning.engines import (
    MultiReasoningEngine,
    ReasoningResult,
    Z3Engine,
    SymPyEngine,
    KanrenEngine,
    CriticalEngine,
    multi_reasoning,
)
from reasoning.quantum import (
    QuantumSimulator,
    bell_state,
    ghz_state,
    uniform_superposition,
    run_experiment_suite,
    DEFAULT_SEEDS,
)

__all__ = [
    "MultiReasoningEngine", "ReasoningResult", "Z3Engine", "SymPyEngine",
    "KanrenEngine", "CriticalEngine", "multi_reasoning",
    "QuantumSimulator", "bell_state", "ghz_state", "uniform_superposition",
    "run_experiment_suite", "DEFAULT_SEEDS",
]
