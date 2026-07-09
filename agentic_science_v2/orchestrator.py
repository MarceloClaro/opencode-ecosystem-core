# -*- coding: utf-8 -*-
"""
Agentic Science V2 — Orchestrator
==================================
Orquestrador central que integra todos os componentes do R101:

  - MentorAgent: constroi e seleciona clusters de problemas
  - PrimeResearcherAgent: gera e refina ideias
  - ReviewerAgent: avalia ideias com scores dimensionais
  - EvolutionManagerAgent: destila memorias persistentes
  - EvoEngine: ciclo darwiniano (selection, crossover, mutation, inheritance)
  - Environment (EurekAgent-style): permissions, artifacts, budget, HITL

Ciclo completo:
  1. Mentor constroi problem space
  2. PrimeResearcher gera ideias para cluster selecionado
  3. Reviewer avalia ideias
  4. EvolutionManager destila memorias
  5. EvoEngine evolui populacao
  6. Repete por N rodadas ou ate estagnacao

SPEC-935-R101.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agentic_science_v2.agents import (
    MentorAgent,
    PrimeResearcherAgent,
    ReviewerAgent,
    EvolutionManagerAgent,
    ProblemCluster,
    ResearchIdea,
)
from agentic_science_v2.evolutionary_engine import EvoEngine, EvolutionRound
from agentic_science_v2.environment import (
    PermissionsEngine,
    ArtifactEngine,
    BudgetEngine,
    HITLEngine,
    Artifact,
)

logger = logging.getLogger(__name__)


@dataclass
class CycleReport:
    """Relatorio completo de um ciclo de descoberta."""
    id: str = field(default_factory=lambda: f"cr-{uuid.uuid4().hex[:8]}")
    round_number: int = 0
    cluster: Optional[ProblemCluster] = None
    ideas: List[ResearchIdea] = field(default_factory=list)
    fitness: Dict[str, float] = field(default_factory=dict)
    evolution: Optional[EvolutionRound] = None
    memory_summary: Dict[str, Any] = field(default_factory=dict)
    duration_seconds: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "round": self.round_number,
            "cluster": self.cluster.to_dict() if self.cluster else None,
            "ideas": [i.to_dict() for i in self.ideas],
            "fitness": self.fitness,
            "evolution": self.evolution.to_dict() if self.evolution else None,
            "memory_summary": self.memory_summary,
            "duration": round(self.duration_seconds, 2),
        }


# ============================================================
# AgenticScienceV2
# ============================================================

class AgenticScienceV2:
    """Orquestrador principal do R101.

    Integra todos os subsistemas em um ciclo fechado de descoberta
    cientifica autonomia.
    """

    def __init__(
        self,
        knowledge_graph: Optional[Dict[str, Any]] = None,
        max_rounds: int = 5,
        ideas_per_round: int = 3,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7,
    ):
        # Sub-sistemas
        self.mentor = MentorAgent(knowledge_graph=knowledge_graph)
        self.researcher = PrimeResearcherAgent()
        self.reviewer = ReviewerAgent()
        self.evo_manager = EvolutionManagerAgent()
        self.evo_engine = EvoEngine(
            mutation_rate=mutation_rate,
            crossover_rate=crossover_rate,
        )

        # Ambiente (EurekAgent-style)
        self.permissions = PermissionsEngine()
        self.artifacts = ArtifactEngine()
        self.budgets = BudgetEngine()
        self.hitl = HITLEngine()

        # Config
        self.max_rounds = max_rounds
        self.ideas_per_round = ideas_per_round

        # Estado
        self.current_round = 0
        self.history: List[CycleReport] = []
        self.population: List[Dict[str, Any]] = []  # entidades evolutivas
        self.running = False

    def _entities_to_fitness(
        self,
        ideas: List[ResearchIdea],
    ) -> Dict[str, float]:
        """Converte ideias em dict fitness para o EvoEngine."""
        return {
            idea.id: idea.scores.get("overall", 0.5)
            for idea in ideas
        }

    def _ideas_to_entities(
        self,
        ideas: List[ResearchIdea],
    ) -> List[Dict[str, Any]]:
        """Converte ideias em entidades para o EvoEngine."""
        entities = []
        for idea in ideas:
            entity = {
                "id": idea.id,
                "concepts": idea.concepts,
                "domains": idea.domains,
                "traits": {
                    "hypothesis": idea.hypothesis,
                    "methodology": idea.methodology,
                },
            }
            entities.append(entity)
        return entities

    def run_cycle(
        self,
        seed_domains: Optional[List[str]] = None,
        num_clusters: int = 3,
    ) -> CycleReport:
        """Executa um ciclo completo de descoberta."""
        self.current_round += 1
        round_num = self.current_round
        start = time.time()

        self.hitl.log_event(
            "cycle_start",
            f"Iniciando ciclo {round_num}",
            {"max_rounds": self.max_rounds},
        )

        # 1. Mentor: construir espaco de problemas
        clusters = self.mentor.construct_problem_space(
            seed_domains=seed_domains,
            num_clusters=num_clusters,
        )
        cluster = self.mentor.select_cluster()
        self.hitl.log_event(
            "clusters_ready",
            f"Cluster selecionado: {cluster.title if cluster else 'N/A'}",
        )

        # 2. PrimeResearcher: gerar ideias
        ideas = self.researcher.generate_ideas(
            cluster,
            num_ideas=self.ideas_per_round,
        ) if cluster else []

        # 3. Reviewer: avaliar ideias
        ideas = self.reviewer.batch_review(ideas)
        self.hitl.log_event(
            "ideas_reviewed",
            f"{len(ideas)} ideias avaliadas",
        )

        # 4. EvolutionManager: destilar memorias
        self.evo_manager.distill_ideation(ideas)
        self.evo_manager.distill_experimentation([
            {"strategy": f"round_{round_num}", "success_rate": 0.8},
        ])

        # 5. EvoEngine: passo evolutivo
        entities = self._ideas_to_entities(ideas)
        fitness_scores = self._entities_to_fitness(ideas)
        new_population, evo_round = self.evo_engine.step(
            entities,
            fitness_scores,
            novelty_pool=["quantum", "ethical", "autonomous", "generative"],
        )
        self.population = new_population

        # 6. Ambiente: armazenar artefatos
        session_id = self.permissions.create_session()
        budget = self.budgets.create_budget(session_id, max_time=3600)

        for idea in ideas:
            artifact = Artifact(
                session_id=session_id,
                name=idea.title[:40],
                artifact_type="hypothesis",
                content=idea.hypothesis,
                score=idea.scores.get("overall", 0),
            )
            self.artifacts.store(artifact)

        # 7. Fitness geral (Mentor)
        fitness = self.mentor.evaluate_fitness(ideas)

        # 8. Relatorio
        duration = time.time() - start
        report = CycleReport(
            round_number=round_num,
            cluster=cluster,
            ideas=ideas,
            fitness=fitness,
            evolution=evo_round,
            memory_summary=self.evo_manager.summary(),
            duration_seconds=duration,
        )
        self.history.append(report)

        self.hitl.log_event(
            "cycle_complete",
            f"Ciclo {round_num} completo em {duration:.1f}s. "
            f"Fitness: {fitness.get('overall', 0)}",
        )

        return report

    def run_full(
        self,
        seed_domains: Optional[List[str]] = None,
    ) -> List[CycleReport]:
        """Executa ciclos completos ate max_rounds ou estagnacao."""
        self.running = True
        reports = []

        for r in range(self.max_rounds):
            if not self.running:
                break

            # Verificar estagnacao
            if self.evo_engine.is_stagnant(window=3, threshold=0.02):
                self.hitl.log_event(
                    "stagnation_detected",
                    "Evolucao estagnada — interrompendo",
                )
                break

            report = self.run_cycle(seed_domains=seed_domains)
            reports.append(report)

            # Verificar orcamento
            if self.budgets.all_exhausted():
                self.hitl.log_event(
                    "budget_exhausted",
                    "Orcamento esgotado — interrompendo",
                )
                break

        self.running = False
        return reports

    def stop(self) -> None:
        """Interrompe execucao."""
        self.running = False

    def summary(self) -> Dict[str, Any]:
        """Sumario completo do estado do orquestrador."""
        top_artifacts = self.artifacts.get_top_k(3)

        return {
            "rounds_completed": len(self.history),
            "max_rounds": self.max_rounds,
            "current_fitness": (
                self.history[-1].fitness if self.history else {}
            ),
            "evolution": self.evo_engine.summary(),
            "memory": self.evo_manager.summary(),
            "environment": {
                "permissions": self.permissions.status(),
                "artifacts": self.artifacts.summary(),
                "budgets": self.budgets.summary(),
                "hitl": self.hitl.summary(),
            },
            "top_artifacts": [a.to_dict() for a in top_artifacts],
            "is_stagnant": self.evo_engine.is_stagnant(),
            "is_running": self.running,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Exporta estado completo."""
        return {
            "config": {
                "max_rounds": self.max_rounds,
                "ideas_per_round": self.ideas_per_round,
            },
            "summary": self.summary(),
            "history": [r.to_dict() for r in self.history],
        }


# ============================================================
# Helper: run from CLI
# ============================================================

def run_agentic_science_v2(
    seed_domain: Optional[str] = None,
    max_rounds: int = 3,
) -> Dict[str, Any]:
    """Funcao helper para execucao do R101."""
    seed_domains = [seed_domain] if seed_domain else None
    asc = AgenticScienceV2(max_rounds=max_rounds)
    reports = asc.run_full(seed_domains=seed_domains)
    return asc.to_dict()
