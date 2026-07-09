# -*- coding: utf-8 -*-
"""
Role-Based Agents — R101
========================
Implementa os 4 papeis do framework EvoSci (ACL 2026):

  - MentorAgent: Define direcao estrategica, constroi clusters de problemas,
    avalia fitness geral do ecossistema.
  - PrimeResearcherAgent: Lidera pesquisa colaborativa, decompoe tarefas,
    coordena assistentes.
  - ReviewerAgent: Avalia ideias com scores dimensionais (novidade,
    viabilidade, excitacao cientifica, overall).
  - EvolutionManagerAgent: Destila memorias persistentes de ideacao e
    experimentacao (EvoScientist, arXiv 2026).

SPEC-935-R101.
"""

from __future__ import annotations

import json
import logging
import random
import statistics
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================
# Dataclasses compartilhadas
# ============================================================

@dataclass
class ProblemCluster:
    """Cluster de problemas interdisciplinares."""
    id: str = field(default_factory=lambda: f"pc-{uuid.uuid4().hex[:8]}")
    title: str = ""
    domains: List[str] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    description: str = ""
    embedding: List[float] = field(default_factory=list)
    feasibility: float = 0.5       # 0.0 a 1.0
    novelty_potential: float = 0.5  # 0.0 a 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "domains": self.domains,
            "concepts": self.concepts,
            "description": self.description,
            "feasibility": self.feasibility,
            "novelty_potential": self.novelty_potential,
        }


@dataclass
class ResearchIdea:
    """Ideia de pesquisa gerada por um agente."""
    id: str = field(default_factory=lambda: f"ri-{uuid.uuid4().hex[:8]}")
    title: str = ""
    hypothesis: str = ""
    methodology: str = ""
    expected_impact: str = ""
    domains: List[str] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    scores: Dict[str, float] = field(default_factory=dict)
    rationale: str = ""
    cluster_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "hypothesis": self.hypothesis,
            "methodology": self.methodology,
            "expected_impact": self.expected_impact,
            "domains": self.domains,
            "concepts": self.concepts,
            "scores": dict(self.scores),
            "rationale": self.rationale,
            "cluster_id": self.cluster_id,
        }


@dataclass
class TaskDecomposition:
    """Decomposicao de tarefas para um cluster."""
    id: str = field(default_factory=lambda: f"td-{uuid.uuid4().hex[:8]}")
    cluster_id: str = ""
    tasks: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "cluster_id": self.cluster_id,
            "tasks": self.tasks,
        }


# Planilha de dominios interdisciplinares
INTERDISCIPLINARY_DOMAINS = [
    ("Quantum Machine Learning", ["quantum", "machine learning", "physics"]),
    ("Bio-Inspired AI", ["neuroscience", "biology", "computation"]),
    ("Climate Informatics", ["climate science", "data science", "policy"]),
    ("Neuro-Symbolic Systems", ["neuroscience", "logic", "AI"]),
    ("Synthetic Biology Computing", ["biology", "computation", "genetics"]),
    ("Ethical AI Governance", ["ethics", "law", "AI"]),
    ("Digital Twins for Healthcare", ["healthcare", "simulation", "AI"]),
    ("Swarm Robotics Ecology", ["robotics", "ecology", "swarm"]),
    ("Computational Social Science", ["sociology", "computation", "networks"]),
    ("Quantum Chemistry Simulation", ["quantum", "chemistry", "simulation"]),
]


# ============================================================
# MentorAgent
# ============================================================

class MentorAgent:
    """Define direcao estrategica e constroi clusters de problemas.

    Inspirado no Mentor Agent do EvoSci (Xiong et al., ACL 2026).
    """

    def __init__(
        self,
        knowledge_graph: Optional[Dict[str, Any]] = None,
        creativity: float = 0.3,
    ):
        self.knowledge_graph = knowledge_graph or {}
        self.creativity = creativity
        self.clusters: List[ProblemCluster] = []
        self.feedback_history: List[Dict[str, Any]] = []

    def construct_problem_space(
        self,
        seed_domains: Optional[List[str]] = None,
        num_clusters: int = 3,
    ) -> List[ProblemCluster]:
        """Constroi clusters de problemas interdisciplinares.

        Se knowledge_graph existir, extrai conceitos dele; caso contrario,
        usa dominios pre-definidos.
        """
        self.clusters = []
        domains = seed_domains or [d[0] for d in INTERDISCIPLINARY_DOMAINS]

        # Embaralhar e selecionar dominios
        selected = random.sample(
            domains,
            min(num_clusters, len(domains)),
        )

        for domain_name in selected:
            # Encontrar conceitos associados
            concepts = []
            for d_name, d_concepts in INTERDISCIPLINARY_DOMAINS:
                if d_name == domain_name:
                    concepts = d_concepts
                    break

            # Se temos grafo, enriquecer com conceitos do grafo
            if self.knowledge_graph:
                graph_concepts = self.knowledge_graph.get("concepts", [])
                if graph_concepts:
                    extra = random.sample(
                        graph_concepts,
                        min(2, len(graph_concepts)),
                    )
                    concepts = list(set(concepts + extra))

            cluster = ProblemCluster(
                title=domain_name,
                domains=[domain_name],
                concepts=concepts,
                description=f"Cluster interdisciplinar em {domain_name} "
                           f"com conceitos: {', '.join(concepts)}",
                feasibility=random.uniform(0.3, 0.9),
                novelty_potential=random.uniform(0.4, 0.95),
                embedding=[random.random() for _ in range(16)],
            )
            self.clusters.append(cluster)

        return self.clusters

    def select_cluster(
        self,
        feedback: Optional[Dict[str, Any]] = None,
    ) -> Optional[ProblemCluster]:
        """Seleciona o melhor cluster com base em feedback ou heuristica."""
        if not self.clusters:
            return None

        if feedback:
            self.feedback_history.append(feedback)

        # Pontuacao composta
        def score(c: ProblemCluster) -> float:
            f = c.feasibility
            n = c.novelty_potential
            # Peso maior para novidade com pequena penalidade por baixa viabilidade
            return 0.6 * n + 0.4 * f

        self.clusters.sort(key=score, reverse=True)
        return self.clusters[0]

    def evaluate_fitness(
        self,
        ideas: List[ResearchIdea],
    ) -> Dict[str, float]:
        """Avalia fitness geral do ecossistema de ideias."""
        if not ideas:
            return {"avg_novelty": 0.0, "avg_feasibility": 0.0, "overall": 0.0}

        avg_novelty = statistics.mean(
            [i.scores.get("novelty", 0) for i in ideas]
        )
        avg_feasibility = statistics.mean(
            [i.scores.get("feasibility", 0) for i in ideas]
        )
        avg_excitement = statistics.mean(
            [i.scores.get("excitement", 0) for i in ideas]
        )
        overall = 0.4 * avg_novelty + 0.3 * avg_feasibility + 0.3 * avg_excitement

        return {
            "avg_novelty": round(avg_novelty, 2),
            "avg_feasibility": round(avg_feasibility, 2),
            "avg_excitement": round(avg_excitement, 2),
            "overall": round(overall, 2),
        }

    def reset(self) -> None:
        """Limpa estado interno."""
        self.clusters = []
        self.feedback_history = []


# ============================================================
# PrimeResearcherAgent
# ============================================================

class PrimeResearcherAgent:
    """Lidera pesquisa colaborativa e decompoe tarefas.

    Inspirado no Prime Researcher do EvoSci (ACL 2026) e no
    Researcher Agent do EvoScientist (arXiv 2026).
    """

    def __init__(
        self,
        ideation_memory: Optional[Any] = None,
        experimentation_memory: Optional[Any] = None,
    ):
        self.ideation_memory = ideation_memory
        self.experimentation_memory = experimentation_memory

    def decompose_tasks(self, cluster: ProblemCluster) -> TaskDecomposition:
        """Decompoe um cluster em tarefas estruturadas."""
        tasks = [
            {
                "id": "background",
                "description": f"Investigacao de background em {cluster.title}",
                "domain": cluster.domains[0] if cluster.domains else "",
                "expected_output": "Sumario de literatura",
            },
            {
                "id": "problem_analysis",
                "description": f"Analise do problema: {cluster.description}",
                "domain": cluster.domains[0] if cluster.domains else "",
                "expected_output": "Analise estruturada",
            },
            {
                "id": "idea_generation",
                "description": "Geracao de hipoteses e metodologias",
                "domain": cluster.domains[0] if cluster.domains else "",
                "expected_output": "3+ ideias de pesquisa",
            },
            {
                "id": "refinement",
                "description": "Refinamento iterativo das ideias",
                "domain": cluster.domains[0] if cluster.domains else "",
                "expected_output": "Ideias refinadas com scores",
            },
        ]

        return TaskDecomposition(
            cluster_id=cluster.id,
            tasks=tasks,
        )

    def generate_ideas(
        self,
        cluster: ProblemCluster,
        num_ideas: int = 3,
    ) -> List[ResearchIdea]:
        """Gera ideias de pesquisa para um cluster."""
        ideas = []

        for i in range(num_ideas):
            # Amostrar conceitos do cluster
            concepts_sample = random.sample(
                cluster.concepts,
                min(3, len(cluster.concepts)),
            ) if cluster.concepts else ["general"]

            # Se temos memoria de ideacao, enriquecer
            memory_inspiration = ""
            if self.ideation_memory:
                successful = self.ideation_memory.get_successful_directions(
                    top_k=1
                )
                if successful:
                    memory_inspiration = successful[0].get("idea", "")

            idea = ResearchIdea(
                title=f"{cluster.title} — Approach {i + 1}",
                hypothesis=f"Hypothesis {i + 1}: Explorando "
                          f"{' e '.join(concepts_sample)} "
                          f"em {cluster.title}",
                methodology=f"Metodologia {i + 1}: Abordagem "
                           f"{['experimental', 'computacional', 'teorica'][i % 3]}",
                expected_impact=f"Impacto esperado: Avanco em "
                               f"{cluster.title}",
                domains=cluster.domains,
                concepts=list(set(cluster.concepts + concepts_sample)),
                cluster_id=cluster.id,
            )
            ideas.append(idea)

        return ideas

    def refine_ideas(
        self,
        ideas: List[ResearchIdea],
        feedback: List[Dict[str, Any]],
    ) -> List[ResearchIdea]:
        """Refina ideias com base em feedback."""
        refined = []
        for idea, fb in zip(ideas, feedback):
            # Aplicar feedback como melhoria textual
            suggestion = fb.get("suggestion", "")
            if suggestion:
                idea.hypothesis += f" [Refined: {suggestion}]"
            refined.append(idea)
        return refined


# ============================================================
# ReviewerAgent
# ============================================================

class ReviewerAgent:
    """Avalia ideias com scores dimensionais.

    Inspirado no Reviewer do EvoSci (ACL 2026): avalia novidade,
    viabilidade, eficacia esperada, excitacao cientifica e overall.
    """

    def __init__(self, strictness: float = 0.5):
        self.strictness = strictness  # 0.0 (facil) a 1.0 (rigoroso)
        self.review_history: List[Dict[str, Any]] = []

    def review(self, idea: ResearchIdea) -> ResearchIdea:
        """Avalia uma ideia e preenche scores."""

        # Heuristica baseada em comprimento e diversidade de conceitos
        num_concepts = len(idea.concepts) if idea.concepts else 1
        hypothesis_len = len(idea.hypothesis) if idea.hypothesis else 0

        novelty = min(1.0, (
            0.3 * (num_concepts / 5.0) +
            0.3 * random.uniform(0.4, 0.9) +
            0.4 * (1.0 - self.strictness * 0.3)
        ))

        feasibility = min(1.0, (
            0.5 * (1.0 - self.strictness * 0.4) +
            0.3 * min(1.0, hypothesis_len / 200.0) +
            0.2 * random.uniform(0.3, 0.8)
        ))

        excitement = min(1.0, (
            0.4 * novelty +
            0.3 * (num_concepts / 4.0) +
            0.3 * random.uniform(0.3, 0.9)
        ))

        effectiveness = min(1.0, (
            0.5 * feasibility +
            0.3 * novelty +
            0.2 * random.uniform(0.2, 0.8)
        ))

        overall = round(
            0.3 * novelty + 0.25 * feasibility +
            0.25 * excitement + 0.2 * effectiveness,
            2,
        )

        # Gerar rationale
        rationale = (
            f"Novelty {novelty:.2f}: {'alta' if novelty > 0.6 else 'moderada' if novelty > 0.3 else 'baixa'}. "
            f"Feasibility {feasibility:.2f}: {'viavel' if feasibility > 0.5 else 'desafiadora'}. "
            f"Excitement {excitement:.2f}: {'empolgante' if excitement > 0.6 else 'moderado'}."
        )

        idea.scores = {
            "novelty": round(novelty, 2),
            "feasibility": round(feasibility, 2),
            "excitement": round(excitement, 2),
            "effectiveness": round(effectiveness, 2),
            "overall": overall,
        }
        idea.rationale = rationale

        self.review_history.append({
            "idea_id": idea.id,
            "scores": dict(idea.scores),
            "timestamp": time.time(),
        })

        return idea

    def batch_review(
        self,
        ideas: List[ResearchIdea],
    ) -> List[ResearchIdea]:
        """Avalia multiplas ideias."""
        return [self.review(idea) for idea in ideas]

    def get_ranking(
        self,
        ideas: List[ResearchIdea],
    ) -> List[ResearchIdea]:
        """Retorna ideias ordenadas por score overall."""
        return sorted(
            ideas,
            key=lambda i: i.scores.get("overall", 0),
            reverse=True,
        )

    def get_suggestions(
        self,
        idea: ResearchIdea,
    ) -> str:
        """Gera sugestoes de melhoria."""
        suggestions = []
        scores = idea.scores

        if scores.get("novelty", 0) < 0.4:
            suggestions.append("Aumentar a novidade incorporando conceitos "
                               "de dominios distantes")
        if scores.get("feasibility", 0) < 0.4:
            suggestions.append("Detalhar a metodologia e recursos necessarios")
        if scores.get("excitement", 0) < 0.4:
            suggestions.append("Articular melhor o impacto potencial")

        return " | ".join(suggestions) if suggestions else "Idea bem equilibrada"


# ============================================================
# EvolutionManagerAgent
# ============================================================

class EvolutionManagerAgent:
    """Destila memorias persistentes para melhoria continua.

    Inspirado no Evolution Manager Agent do EvoScientist (arXiv 2026).
    Mantem:
      - IdeationMemory: direcoes promissoras + falhas
      - ExperimentationMemory: estrategias efetivas
    """

    def __init__(self):
        self.ideation_memory: Dict[str, Any] = {
            "successful_directions": [],
            "failed_directions": [],
            "top_ideas": [],
        }
        self.experimentation_memory: Dict[str, Any] = {
            "effective_strategies": [],
            "code_patterns": [],
        }

    def distill_ideation(
        self,
        ideas: List[ResearchIdea],
        top_k: int = 3,
    ) -> None:
        """Destila ideias de alta qualidade para memoria."""
        ranked = sorted(
            ideas,
            key=lambda i: i.scores.get("overall", 0),
            reverse=True,
        )

        # Registrar top ideias
        for idea in ranked[:top_k]:
            entry = {
                "idea_id": idea.id,
                "title": idea.title,
                "concepts": idea.concepts,
                "scores": dict(idea.scores),
                "timestamp": time.time(),
            }
            # Evitar duplicatas
            if not any(
                e["idea_id"] == idea.id
                for e in self.ideation_memory["top_ideas"]
            ):
                self.ideation_memory["top_ideas"].append(entry)

        # Registrar direcoes bem-sucedidas
        for idea in ranked[:top_k]:
            direction = {
                "idea": idea.hypothesis,
                "domains": idea.domains,
                "avg_score": statistics.mean(
                    list(idea.scores.values())
                ) if idea.scores else 0,
            }
            self.ideation_memory["successful_directions"].append(direction)

        # Registrar direcoes mal-sucedidas (baixo score)
        for idea in ranked[-2:]:
            direction = {
                "idea": idea.hypothesis,
                "reason": "low_score",
                "avg_score": statistics.mean(
                    list(idea.scores.values())
                ) if idea.scores else 0,
            }
            self.ideation_memory["failed_directions"].append(direction)

    def distill_experimentation(
        self,
        strategies: List[Dict[str, Any]],
    ) -> None:
        """Destila estrategias de experimentacao efetivas."""
        for strategy in strategies:
            if strategy.get("success_rate", 0) >= 0.5:
                self.experimentation_memory["effective_strategies"].append(
                    strategy
                )

    def get_successful_directions(self, top_k: int = 3) -> List[Dict[str, Any]]:
        """Recupera direcoes bem-sucedidas."""
        return self.ideation_memory["successful_directions"][:top_k]

    def get_failed_directions(self, top_k: int = 3) -> List[Dict[str, Any]]:
        """Recupera direcoes que falharam."""
        return self.ideation_memory["failed_directions"][:top_k]

    def get_best_strategies(self, top_k: int = 3) -> List[Dict[str, Any]]:
        """Recupera estrategias efetivas."""
        return self.experimentation_memory["effective_strategies"][:top_k]

    def summary(self) -> Dict[str, Any]:
        """Sumario do estado da memoria."""
        return {
            "ideation": {
                "successful": len(
                    self.ideation_memory["successful_directions"]
                ),
                "failed": len(self.ideation_memory["failed_directions"]),
                "top_ideas": len(self.ideation_memory["top_ideas"]),
            },
            "experimentation": {
                "effective_strategies": len(
                    self.experimentation_memory["effective_strategies"]
                ),
            },
        }

    def reset(self) -> None:
        """Limpa memorias."""
        self.ideation_memory = {
            "successful_directions": [],
            "failed_directions": [],
            "top_ideas": [],
        }
        self.experimentation_memory = {
            "effective_strategies": [],
            "code_patterns": [],
        }
