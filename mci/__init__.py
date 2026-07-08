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

__all__ = [
    "metabus", "MetaBus", "MetacognitiveMemory",
    "blackboard", "Blackboard", "AgentCard", "BlackboardTask",
    "reflexion_engine", "ReflexionEngine",
    "MetacognitiveTrace", "MetacognitiveEvaluator", "MetacognitiveBenchmarkSuite",
    "classify_metacognitive_tier", "run_metacognitive_superhuman_suite",
    "run_scientific_cycle", "run_scientific_governance_pipeline",
]

__version__ = "1.0.0"
