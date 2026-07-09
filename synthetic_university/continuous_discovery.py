# -*- coding: utf-8 -*-
"""
Continuous Discovery Loop — R95
================================
Watcher/daemon que periodicamente gera, enriquece e reavalia teses,
mantendo um histórico acumulado de descobertas.

Uso:
    from synthetic_university.continuous_discovery import ContinuousDiscoveryLoop

    loop = ContinuousDiscoveryLoop(output_dir="academic/discovery", interval_hours=24)
    result = loop.run_cycle()
    summary = loop.get_summary()
    loop.export_all()

SPEC-935-R95.
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ============================================================
# Dados internos de fallback (sem dependência externa)
# ============================================================

FALLBACK_TITLES = [
    "Quantum Ethics: A Framework for Moral AI Systems",
    "Deep Learning for Tropical Disease Diagnosis",
    "Algorithmic Fairness in Criminal Justice",
    "Neural Correlates of Consciousness",
    "Blockchain for Scientific Reproducibility",
    "Federated Learning for Privacy-Preserving Healthcare",
    "Reinforcement Learning for Climate Policy Optimization",
    "Causal Inference in Epidemiological Modeling",
    "Natural Language Processing for Indigenous Language Preservation",
    "Topological Data Analysis in Neuroscience",
    "Swarm Intelligence for Disaster Response Coordination",
    "Generative AI for Drug Discovery Pipelines",
    "Digital Twins for Personalized Medicine",
    "Quantum Machine Learning for High-Energy Physics",
    "Synthetic Biology for Carbon Capture",
]

FALLBACK_CONCEPTS_POOL = [
    ["quantum", "ethics", "AI", "morality"],
    ["deep learning", "diagnosis", "tropics", "disease"],
    ["fairness", "algorithms", "criminal", "justice"],
    ["consciousness", "neural", "correlates", "brain"],
    ["blockchain", "reproducibility", "science", "open data"],
    ["federated", "privacy", "healthcare", "learning"],
    ["reinforcement", "climate", "policy", "optimization"],
    ["causal", "inference", "epidemiology", "modeling"],
    ["NLP", "indigenous", "language", "preservation"],
    ["topological", "data", "analysis", "neuroscience"],
    ["swarm", "disaster", "response", "coordination"],
    ["generative", "drug", "discovery", "pipeline"],
    ["digital twin", "personalized", "medicine", "simulation"],
    ["quantum ML", "high-energy", "physics", "particle"],
    ["synthetic biology", "carbon", "capture", "climate"],
]


# ============================================================
# Classe principal
# ============================================================

class ContinuousDiscoveryLoop:
    """Loop de descoberta contínua para a Universidade Sintética.

    Attributes:
        output_dir: Diretório para exportação dos relatórios.
        interval_hours: Intervalo sugerido entre ciclos (não implementa scheduling).
        lang: Idioma (en/pt).
        cycle_history: Lista de resultados de ciclos executados.
    """

    def __init__(
        self,
        output_dir: str = "academic/discovery",
        interval_hours: float = 24,
        lang: str = "en",
    ):
        self.output_dir = output_dir
        self.interval_hours = interval_hours
        self.lang = lang
        self.cycle_history: List[Dict[str, Any]] = []

    # --------------------------------------------------------
    # Geração interna de teses (fallback)
    # --------------------------------------------------------

    def _generate_theses(self, n: int = 4) -> List[Dict[str, Any]]:
        """Gera N teses a partir de dados de fallback."""
        import random
        rng = random.Random(time.time())
        indices = rng.sample(range(len(FALLBACK_TITLES)), min(n, len(FALLBACK_TITLES)))
        theses = []
        for i, idx in enumerate(indices):
            theses.append({
                "thesis_id": f"thesis_{int(time.time())}_{i}",
                "title": FALLBACK_TITLES[idx],
                "concepts": FALLBACK_CONCEPTS_POOL[idx % len(FALLBACK_CONCEPTS_POOL)],
                "composite_score": round(rng.uniform(0.3, 0.9), 2),
            })
        return theses

    def _enrich_thesis(self, thesis: Dict[str, Any]) -> Dict[str, Any]:
        """Enriquece uma tese com dados simulados (fallback)."""
        import random
        rng = random.Random(time.time())
        concepts = thesis.get("concepts", ["concept"])
        enriched = []
        for c in concepts[:3]:
            enriched.append({
                "concept": c,
                "results": [
                    {"title": f"Paper about {c}", "year": rng.randint(2018, 2025)},
                ],
            })
        thesis["concepts_enriched"] = enriched
        thesis["enrichment_count"] = len(enriched)
        return thesis

    def _analyze_novelty(self, thesis: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa novidade de forma simulada."""
        import random
        rng = random.Random(time.time() + hash(thesis.get("thesis_id", "")))
        originality = rng.uniform(20, 85)
        non_triviality = rng.uniform(15, 80)
        impact = rng.uniform(10, 75)
        thesis["novelty_score"] = round(
            originality * 0.35 + non_triviality * 0.35 + impact * 0.30, 1
        )
        thesis["novelty_components"] = {
            "originality": round(originality, 1),
            "non_triviality": round(non_triviality, 1),
            "impact": round(impact, 1),
        }
        return thesis

    # --------------------------------------------------------
    # Ciclo principal
    # --------------------------------------------------------

    def run_cycle(self) -> Dict[str, Any]:
        """Executa um ciclo completo de descoberta contínua.

        Etapas:
            1. Gera 3-5 teses
            2. Enriquece cada tese
            3. Reavalia novidade de cada tese
            4. Calcula métricas agregadas

        Returns:
            Dict com metadados do ciclo e lista de teses.
        """
        import random
        rng = random.Random(time.time())
        start = time.time()

        # Etapa 1: gerar teses
        n_theses = rng.randint(3, 5)
        theses = self._generate_theses(n_theses)

        # Etapas 2 e 3: enriquecer e avaliar novidade
        for t in theses:
            self._enrich_thesis(t)
            self._analyze_novelty(t)

        # Etapa 4: métricas
        novelty_scores = [t.get("novelty_score", 0) for t in theses]
        enrichment_counts = [t.get("enrichment_count", 0) for t in theses]

        cycle_result = {
            "timestamp": start,
            "duration_seconds": round(time.time() - start, 3),
            "theses_count": len(theses),
            "avg_novelty": round(
                sum(novelty_scores) / max(1, len(novelty_scores)), 1
            ),
            "avg_enrichment": round(
                sum(enrichment_counts) / max(1, len(enrichment_counts)), 1
            ),
            "theses": theses,
            "status": "ok",
        }

        self.cycle_history.append(cycle_result)
        logger.info(
            f"Ciclo {len(self.cycle_history)} concluído: "
            f"{len(theses)} teses, "
            f"novidade média {cycle_result['avg_novelty']:.1f}"
        )

        return cycle_result

    # --------------------------------------------------------
    # Sumário e consultas
    # --------------------------------------------------------

    def get_summary(self) -> Dict[str, Any]:
        """Retorna sumário consolidado de todos os ciclos.

        Returns:
            Dict com total_cycles, avg_novelty, avg_enrichment,
            top_theses, latest_cycle.
        """
        if not self.cycle_history:
            return {
                "total_cycles": 0,
                "avg_novelty": 0.0,
                "avg_enrichment": 0.0,
                "top_theses": [],
                "latest_cycle": None,
            }

        all_novelties = []
        all_enrichments = []
        all_theses = []

        for cycle in self.cycle_history:
            for t in cycle.get("theses", []):
                all_novelties.append(t.get("novelty_score", 0))
                all_enrichments.append(t.get("enrichment_count", 0))
                all_theses.append(t)

        # Top 5 teses por novelty_score
        all_theses.sort(
            key=lambda t: t.get("novelty_score", 0), reverse=True
        )
        top_theses = all_theses[:5]

        return {
            "total_cycles": len(self.cycle_history),
            "avg_novelty": round(
                sum(all_novelties) / max(1, len(all_novelties)), 1
            ),
            "avg_enrichment": round(
                sum(all_enrichments) / max(1, len(all_enrichments)), 1
            ),
            "top_theses": [
                {
                    "thesis_id": t.get("thesis_id", ""),
                    "title": t.get("title", ""),
                    "novelty_score": t.get("novelty_score", 0),
                }
                for t in top_theses
            ],
            "latest_cycle": self.cycle_history[-1]["timestamp"]
            if self.cycle_history
            else None,
        }

    # --------------------------------------------------------
    # Exportação
    # --------------------------------------------------------

    def export_report(self, cycle_index: int = -1) -> str:
        """Exporta relatório de um ciclo específico para JSON.

        Args:
            cycle_index: Índice do ciclo (default -1 = último).

        Returns:
            Caminho do arquivo exportado.
        """
        if not self.cycle_history:
            raise ValueError("Nenhum ciclo para exportar")

        cycle = self.cycle_history[cycle_index]
        os.makedirs(self.output_dir, exist_ok=True)
        path = os.path.join(
            self.output_dir, f"cycle_{len(self.cycle_history)}_{int(cycle['timestamp'])}.json"
        )
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cycle, f, indent=2, ensure_ascii=False)
        logger.info(f"Relatório exportado: {path}")
        return path

    def export_all(self) -> str:
        """Exporta relatório consolidado de todos os ciclos.

        Returns:
            Caminho do arquivo exportado.
        """
        os.makedirs(self.output_dir, exist_ok=True)
        data = {
            "total_cycles": len(self.cycle_history),
            "summary": self.get_summary(),
            "cycles": self.cycle_history,
        }
        path = os.path.join(self.output_dir, "all_cycles.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Relatório consolidado exportado: {path}")
        return path
