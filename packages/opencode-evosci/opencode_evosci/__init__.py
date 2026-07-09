# -*- coding: utf-8 -*-
"""
opencode-evosci — Agentic Science V2 (R101)
============================================
Bio-inspired multi-agent evolutionary framework for scientific discovery.

Componentes:
  - MentorAgent: Gera hipoteses iniciais
  - PrimeResearcherAgent: Executa pesquisa aprofundada
  - ReviewerAgent: Avalia contribuicoes
  - EvolutionManagerAgent: Gerencia ciclo evolutivo
  - EvolutionaryEngine: Selecao, crossover, mutacao, heranca
  - OrchestratorAgent: Orquestra pipeline completo
"""

from .agents import MentorAgent, PrimeResearcherAgent, ReviewerAgent, EvolutionManagerAgent
from .evolutionary_engine import EvoEngine, EvolutionRound
from .environment import PermissionsEngine, Artifact, ArtifactEngine, Budget, BudgetEngine, HITLEngine
from .orchestrator import AgenticScienceV2

__all__ = [
    "MentorAgent", "PrimeResearcherAgent", "ReviewerAgent", "EvolutionManagerAgent",
    "EvolutionaryEngine",
    "Environment", "Artifact", "Budget",
    "OrchestratorAgent",
]
