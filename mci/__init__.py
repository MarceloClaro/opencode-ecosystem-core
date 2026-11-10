# -*- coding: utf-8 -*-
"""
Metacognitive Interconnect (MCI)
================================
Camada de interconexão metacognitiva do OpenCode Ecosystem Core.

Componentes:
- MetaBus: Global Workspace (pub/sub + persistência)
- MetacognitiveMemory: memória episódica/semântica + confidence ledger
- Blackboard: coordenação por quadro negro com Agent Cards (A2A)
- ReflexionEngine: auto-reflexão pós-execução (Reflexion, Shinn et al. 2023)
- R1148: EMA, N-of-1/SCED, grafo de claims, trust warrant e contrato de runtime
"""

from .metabus import metabus, MetaBus, MetacognitiveMemory
from .blackboard import blackboard, Blackboard, AgentCard, BlackboardTask
from .reflexion import reflexion_engine, ReflexionEngine
from .metacognitive_evaluator import (
    MetacognitiveTrace,
    MetacognitiveEvaluator,
    MetacognitiveBenchmarkSuite,
    classify_metacognitive_tier,
    run_metacognitive_superhuman_suite,
)
from .orchestration import run_scientific_cycle
from .pipeline import run_scientific_governance_pipeline
from .ema import (
    build_schedule,
    record_responses,
    validate_psychometrics,
    paired_transfer_test,
    ema_report,
)
from .n_of_1 import (
    generate_sequence,
    lock_preregistration,
    verify_lock,
    nap,
    pem,
    tau_u,
    run_n_of_1,
)
from .claims_graph import ClaimsGraph, FormalLinkError
from .trust_warrant import (
    brier_score,
    expected_calibration_error,
    coordination_score,
    epistemic_warrant,
    trust_report,
)
from .runtime_contract import (
    ACTION_CLASSES,
    CircuitBreaker,
    RuntimeContract,
)

__all__ = [
    "metabus", "MetaBus", "MetacognitiveMemory",
    "blackboard", "Blackboard", "AgentCard", "BlackboardTask",
    "reflexion_engine", "ReflexionEngine",
    "MetacognitiveTrace", "MetacognitiveEvaluator", "MetacognitiveBenchmarkSuite",
    "classify_metacognitive_tier", "run_metacognitive_superhuman_suite",
    "run_scientific_cycle", "run_scientific_governance_pipeline",
    "build_schedule", "record_responses", "validate_psychometrics",
    "paired_transfer_test", "ema_report",
    "generate_sequence", "lock_preregistration", "verify_lock",
    "nap", "pem", "tau_u", "run_n_of_1",
    "ClaimsGraph", "FormalLinkError",
    "brier_score", "expected_calibration_error", "coordination_score",
    "epistemic_warrant", "trust_report",
    "ACTION_CLASSES", "CircuitBreaker", "RuntimeContract",
]

__version__ = "1.0.0"
