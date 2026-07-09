# -*- coding: utf-8 -*-
"""
evo-science skill — R101 Agentic Science V2
=====================================================================
Implementa comandos /evo-init, /evo-evolve, /evo-status, /evo-report.
Pode ser usado como skill independente ou registrado como MCP tool.
"""

import sys
import os
from typing import Any, Dict, List, Optional

# Tenta importar do core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

_HAS_CORE = False
try:
    from agentic_science_v2.orchestrator import OrchestratorAgent
    from agentic_science_v2.agents import MentorAgent
    _HAS_CORE = True
except ImportError:
    _HAS_CORE = False


class EvoScienceSkill:
    """Skill de ciclo evolutivo de descoberta cientifica."""

    def __init__(self):
        self._orchestrator = None
        self._population = []
        self._generation = 0
        self._topic = ""
        self._fitness_history = []
        self._initialized = False

    def evo_init(self, topic: str) -> Dict[str, Any]:
        """/evo-init: Inicializa ciclo evolutivo."""
        self._topic = topic
        self._generation = 0
        self._initialized = True

        if _HAS_CORE:
            mentor = MentorAgent()
            self._population = mentor.propose_hypotheses(topic, n=4)
        else:
            # Modo standalone: hipoteses simuladas
            self._population = [
                {"id": "H1", "hypothesis": f"Hypothesis A for {topic}", "fitness": 0.0},
                {"id": "H2", "hypothesis": f"Hypothesis B for {topic}", "fitness": 0.0},
                {"id": "H3", "hypothesis": f"Hypothesis C for {topic}", "fitness": 0.0},
                {"id": "H4", "hypothesis": f"Hypothesis D for {topic}", "fitness": 0.0},
            ]

        self._fitness_history.append(0.0)
        return {
            "status": "initialized",
            "topic": topic,
            "population_size": len(self._population),
            "population": self._population
        }

    def evo_evolve(self) -> Dict[str, Any]:
        """/evo-evolve: Executa rodada evolutiva."""
        if not self._initialized:
            return {"status": "error", "message": "Use /evo-init first"}

        self._generation += 1

        if _HAS_CORE:
            # Usar EvolutionaryEngine do core
            from agentic_science_v2.evolutionary_engine import EvolutionaryEngine
            engine = EvolutionaryEngine()
            self._population = engine.evolve(self._population)
            avg_fitness = sum(h.get("fitness", 0.0) for h in self._population) / len(self._population)
        else:
            # Simulacao standalone
            import random
            for h in self._population:
                h["fitness"] = min(1.0, h.get("fitness", 0.0) + random.uniform(0.05, 0.2))
            avg_fitness = sum(h["fitness"] for h in self._population) / len(self._population)
            # Crossover: troca partes entre hipoteses
            if len(self._population) >= 2:
                i, j = random.sample(range(len(self._population)), 2)
                child = {
                    "id": f"H{len(self._population) + 1}",
                    "hypothesis": f"Hybrid: {self._population[i]['hypothesis'][:20]} + {self._population[j]['hypothesis'][:20]}",
                    "fitness": (self._population[i]["fitness"] + self._population[j]["fitness"]) / 2
                }
                self._population.append(child)

        self._fitness_history.append(avg_fitness)
        return {
            "status": "evolved",
            "generation": self._generation,
            "population_size": len(self._population),
            "avg_fitness": round(avg_fitness, 4),
            "population": self._population
        }

    def evo_status(self) -> Dict[str, Any]:
        """/evo-status: Estado atual da populacao."""
        if not self._initialized:
            return {"status": "error", "message": "Not initialized"}
        best = max(self._population, key=lambda h: h.get("fitness", 0.0))
        avg_fit = sum(h.get("fitness", 0.0) for h in self._population) / len(self._population)
        return {
            "status": "running",
            "topic": self._topic,
            "generation": self._generation,
            "population_size": len(self._population),
            "avg_fitness": round(avg_fit, 4),
            "best_hypothesis": best.get("hypothesis", ""),
            "best_fitness": round(best.get("fitness", 0.0), 4),
            "fitness_history": self._fitness_history
        }

    def evo_report(self) -> Dict[str, Any]:
        """/evo-report: Relatorio de evolucao."""
        if not self._initialized:
            return {"status": "error", "message": "Not initialized"}
        return {
            "status": "report",
            "topic": self._topic,
            "total_generations": self._generation,
            "final_population": self._population,
            "fitness_trajectory": self._fitness_history,
            "convergence_reached": len(self._fitness_history) > 1 and
                abs(self._fitness_history[-1] - self._fitness_history[-2]) < 0.01
        }


# Instancia singleton para uso como modulo
_skill = EvoScienceSkill()

# API publica (mapeia 1:1 com comandos)
evo_init = _skill.evo_init
evo_evolve = _skill.evo_evolve
evo_status = _skill.evo_status
evo_report = _skill.evo_report
