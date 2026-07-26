# -*- coding: utf-8 -*-
"""
Pacote reasoning — Motores de Raciocínio + Módulo Quântico
==========================================================
SPEC-917: 11 motores de raciocínio (lógico, simbólico, relacional,
crítico, bayesiano, causal, temporal, fuzzy, cadeia de pensamento,
analógico e contrafactual) + simulador quântico statevector.
"""

from reasoning.engines import (
    MultiReasoningEngine,
    ReasoningResult,
    Z3Engine,
    SymPyEngine,
    KanrenEngine,
    CriticalEngine,
    BayesianEngine,
    CausalEngine,
    TemporalEngine,
    FuzzyReasoningEngine,
    ChainOfThoughtEngine,
    AnalogicalEngine,
    CounterfactualEngine,
    QuantumReasoningEngine,
    multi_reasoning,
)
from reasoning.cache import ReasoningCache, reasoning_cache
from reasoning.visualizer import ReasoningVisualizer, reasoning_visualizer
from reasoning.parallel import ParallelReasoning
from reasoning.evaluator import ReasoningEvaluator, reasoning_evaluator
from reasoning.quantum import (
    QuantumSimulator,
    bell_state,
    ghz_state,
    uniform_superposition,
    run_experiment_suite,
    DEFAULT_SEEDS,
)
from reasoning.fallacies import FallacyDetector, FallacyMatch, fallacy_detector
from reasoning.arche_rlt import (
    PeirceType,
    RLTNode,
    ReasoningMapper,
    RLTBuilder,
    RLTValidator,
    RLTVisualizer,
    ArcheRLT,
    arche_rlt,
)

__all__ = [
    "MultiReasoningEngine", "ReasoningResult", "Z3Engine", "SymPyEngine",
    "KanrenEngine", "CriticalEngine", "BayesianEngine", "CausalEngine",
    "TemporalEngine", "FuzzyReasoningEngine", "ChainOfThoughtEngine",
    "AnalogicalEngine", "CounterfactualEngine", "QuantumReasoningEngine",
    "multi_reasoning",
    "ReasoningCache", "reasoning_cache",
    "ReasoningVisualizer", "reasoning_visualizer",
    "ParallelReasoning", "ReasoningEvaluator", "reasoning_evaluator",
    "QuantumSimulator", "bell_state", "ghz_state", "uniform_superposition",
    "run_experiment_suite", "DEFAULT_SEEDS",
    "FallacyDetector", "FallacyMatch", "fallacy_detector",
    "PeirceType", "RLTNode", "ReasoningMapper", "RLTBuilder",
    "RLTValidator", "RLTVisualizer", "ArcheRLT", "arche_rlt",
]
