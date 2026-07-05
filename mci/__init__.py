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

__all__ = [
    "metabus", "MetaBus", "MetacognitiveMemory",
    "blackboard", "Blackboard", "AgentCard", "BlackboardTask",
    "reflexion_engine", "ReflexionEngine",
]

__version__ = "1.0.0"
