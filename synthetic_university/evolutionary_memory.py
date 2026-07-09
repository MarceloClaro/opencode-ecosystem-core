# -*- coding: utf-8 -*-
"""
Evolutionary Memory Substrate — R97
====================================
Substrato de memoria persistente evolutiva para o ecossistema.

Fornece 4 componentes integrados:
  - IdeationMemory: direcoes promissoras/falhas
  - ExperimentationMemory: estrategias reutilizaveis
  - HeartbeatReflection: reflexao periodica
  - StagnationDetector: deteccao de estagnacao

Uso:
    from synthetic_university.evolutionary_memory import (
        EvolutionaryMemorySubstrate,
    )

    mem = EvolutionaryMemorySubstrate()
    mem.ideation.record_idea("Quantum Ethics", "success", 85)
    mem.experimentation.record_strategy("chunking", ["nlp"], 90)
    mem.stagnation.record_novelty_score(0, 72.5)
    mem.save("/tmp/memory.json")

SPEC-935-R97.
"""

from __future__ import annotations

import json
import logging
import os
import statistics
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================
# Utilitarios
# ============================================================

def _text_similarity(a: str, b: str) -> float:
    """Similaridade simples baseada em overlap de palavras (0.0 a 1.0)."""
    if not a or not b:
        return 0.0
    a_words = set(a.lower().split())
    b_words = set(b.lower().split())
    if not a_words or not b_words:
        return 0.0
    intersection = a_words & b_words
    union = a_words | b_words
    return len(intersection) / max(1, len(union))


def _compute_trend(values: List[float]) -> str:
    """Computa tendencia de uma serie: 'improving', 'stable' ou 'declining'."""
    if len(values) < 3:
        return "stable"
    # Regressao linear simples
    n = len(values)
    xs = list(range(n))
    mean_x = sum(xs) / n
    mean_y = sum(values) / n
    num = sum((xs[i] - mean_x) * (values[i] - mean_y) for i in range(n))
    den = sum((xs[i] - mean_x) ** 2 for i in range(n))
    if den == 0:
        return "stable"
    slope = num / den
    if slope > 0.5:
        return "improving"
    elif slope < -0.5:
        return "declining"
    return "stable"


# ============================================================
# C1 — IdeationMemory
# ============================================================

class IdeationMemory:
    """Memoria de direcoes de pesquisa exploradas.

    Attributes:
        _ideas: Lista de dicionarios de ideias registradas.
    """

    def __init__(self):
        self._ideas: List[Dict[str, Any]] = []

    def record_idea(
        self,
        direction: str,
        outcome: str,
        score: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Registra uma direcao de pesquisa explorada.

        Args:
            direction: Titulo ou descricao da direcao.
            outcome: 'success' ou 'failure'.
            score: Score de 0 a 100.
            metadata: Dict opcional com dados extras (conceitos, etc).

        Returns:
            idea_id gerado.
        """
        idea_id = str(uuid.uuid4())[:8]
        idea = {
            "idea_id": idea_id,
            "direction": direction,
            "outcome": outcome,
            "score": max(0.0, min(100.0, float(score))),
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        self._ideas.append(idea)
        logger.debug("Ideation: registered '%s' (score=%.1f, outcome=%s)",
                     direction[:50], score, outcome)
        return idea_id

    def get_promising_directions(
        self, top_k: int = 5, min_score: float = 60
    ) -> List[Dict[str, Any]]:
        """Retorna direcoes promissoras (score >= min_score), ordenadas.

        Args:
            top_k: Maximo de resultados.
            min_score: Score minimo (inclusivo).

        Returns:
            Lista de ideias com score >= min_score, ordenadas descending.
        """
        candidates = [i for i in self._ideas if i["score"] >= min_score]
        candidates.sort(key=lambda i: i["score"], reverse=True)
        return candidates[:top_k]

    def get_failed_directions(
        self, max_score: float = 40
    ) -> List[Dict[str, Any]]:
        """Retorna direcoes que falharam (score <= max_score).

        Args:
            max_score: Score maximo (inclusivo) para considerar falha.

        Returns:
            Lista de ideias com score <= max_score.
        """
        return [i for i in self._ideas if i["score"] <= max_score]

    def is_already_explored(
        self, direction: str, threshold: float = 0.7
    ) -> bool:
        """Verifica se direcao similar ja foi explorada.

        Args:
            direction: Titulo/direcao a verificar.
            threshold: Similaridade minima (0.0 a 1.0).

        Returns:
            True se alguma ideia existente tem similaridade >= threshold.
        """
        for idea in self._ideas:
            sim = _text_similarity(direction, idea["direction"])
            if sim >= threshold:
                return True
        return False

    def get_direction_stats(self, idea_id: str) -> Dict[str, Any]:
        """Retorna estatisticas de uma direcao especifica.

        Args:
            idea_id: ID da ideia.

        Returns:
            Dict com n_attempts, avg_score, best_score, trend,
            ou dict vazio se nao encontrada.
        """
        ideas = [i for i in self._ideas if i["idea_id"] == idea_id]
        if not ideas:
            return {}

        scores = [i["score"] for i in ideas]
        return {
            "n_attempts": len(ideas),
            "avg_score": round(statistics.mean(scores), 1),
            "best_score": max(scores),
            "trend": _compute_trend(scores),
        }

    def get_exploration_summary(self) -> Dict[str, Any]:
        """Retorna sumario de exploracao.

        Returns:
            Dict com total_ideas, success_rate, avg_score, diversity.
        """
        if not self._ideas:
            return {
                "total_ideas": 0,
                "success_rate": 0.0,
                "avg_score": 0.0,
                "diversity": 0,
            }

        scores = [i["score"] for i in self._ideas]
        successes = sum(1 for i in self._ideas if i["outcome"] == "success")
        # Diversidade: conceitos unicos em metadados
        all_concepts = set()
        for i in self._ideas:
            concepts = i.get("metadata", {}).get("concepts", [])
            all_concepts.update(concepts)

        return {
            "total_ideas": len(self._ideas),
            "success_rate": round(successes / len(self._ideas), 2),
            "avg_score": round(statistics.mean(scores), 1),
            "diversity": len(all_concepts),
        }


# ============================================================
# C2 — ExperimentationMemory
# ============================================================

class ExperimentationMemory:
    """Memoria de estrategias de ideacao que funcionaram.

    Attributes:
        _strategies: Dict[str, Dict] — mapeia strategy_id -> dados.
    """

    def __init__(self):
        self._strategies: Dict[str, Dict[str, Any]] = {}

    def record_strategy(
        self,
        strategy_id: str,
        context: List[str],
        effectiveness: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Registra uso de uma estrategia.

        Se a strategy_id ja existe, atualiza a media running
        de effectiveness e incrementa n_uses.

        Args:
            strategy_id: Identificador unico da estrategia.
            context: Lista de tags de contexto (ex: ['nlp', 'retrieval']).
            effectiveness: Score de 0 a 100.
            metadata: Dict opcional com dados extras.
        """
        effectiveness = max(0.0, min(100.0, float(effectiveness)))
        now = time.time()

        if strategy_id in self._strategies:
            s = self._strategies[strategy_id]
            # Running mean
            old_total = s["effectiveness"] * s["n_uses"]
            s["n_uses"] += 1
            s["effectiveness"] = round(
                (old_total + effectiveness) / s["n_uses"], 1
            )
            s["last_used"] = now
            s["timestamps"].append(now)
            if metadata:
                s["metadata"].update(metadata)
        else:
            self._strategies[strategy_id] = {
                "strategy_id": strategy_id,
                "context": context,
                "effectiveness": effectiveness,
                "n_uses": 1,
                "metadata": metadata or {},
                "created": now,
                "last_used": now,
                "timestamps": [now],
            }

        logger.debug(
            "Experimentation: recorded '%s' (eff=%.1f, ctx=%s)",
            strategy_id, effectiveness, context
        )

    def get_reusable_strategies(
        self, context: List[str], top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Recupera estrategias relevantes para um contexto.

        Estrategias sao filtradas por overlap de contexto, depois
        ordenadas por effectiveness descendente.

        Args:
            context: Lista de tags de contexto alvo.
            top_k: Maximo de resultados.

        Returns:
            Lista de estrategias viaveis, ordenadas por effectiveness.
        """
        ctx_set = set(c.lower() for c in context)
        candidates = []
        for s in self._strategies.values():
            s_ctx = set(c.lower() for c in s["context"])
            if ctx_set & s_ctx:  # overlap
                candidates.append(s)

        candidates.sort(key=lambda s: s["effectiveness"], reverse=True)
        return candidates[:top_k]

    def get_effectiveness_stats(self, strategy_id: str) -> Dict[str, Any]:
        """Retorna metricas de efetividade de uma estrategia.

        Args:
            strategy_id: ID da estrategia.

        Returns:
            Dict com mean_effectiveness, n_uses, max_effectiveness, trend,
            ou dict vazio se nao encontrada.
        """
        if strategy_id not in self._strategies:
            return {}

        s = self._strategies[strategy_id]
        return {
            "mean_effectiveness": s["effectiveness"],
            "n_uses": s["n_uses"],
            "max_effectiveness": max(
                s["effectiveness"],  # aproximacao via running mean
                key=lambda x: x if isinstance(x, (int, float)) else 0
            ) if False else s["effectiveness"],  # fallback
            "trend": "stable",  # simplificado
        }

    def get_strategy_portfolio(self) -> List[Dict[str, Any]]:
        """Retorna portfolio completo rankeado por effectiveness.

        Returns:
            Lista de dicts com strategy_id, mean_effectiveness,
            n_uses, context, ordenados por mean_effectiveness desc.
        """
        portfolio = []
        for s in self._strategies.values():
            portfolio.append({
                "strategy_id": s["strategy_id"],
                "mean_effectiveness": s["effectiveness"],
                "n_uses": s["n_uses"],
                "context": s["context"],
                "last_used": s.get("last_used", 0),
            })
        portfolio.sort(key=lambda p: p["mean_effectiveness"], reverse=True)
        return portfolio


# ============================================================
# C3 — HeartbeatReflection
# ============================================================

class HeartbeatReflection:
    """Reflexao periodica que consolida aprendizado.

    Attributes:
        _reflections: Lista de reflexoes realizadas.
    """

    def __init__(self):
        self._reflections: List[Dict[str, Any]] = []

    def should_reflect(self, cycle_count: int, interval: int = 5) -> bool:
        """Verifica se e hora de refletir.

        Args:
            cycle_count: Numero de ciclos executados.
            interval: A cada quantos ciclos refletir.

        Returns:
            True se cycle_count % interval == 0.
        """
        if interval <= 0:
            return False
        return cycle_count % interval == 0

    def reflect(
        self, memory_substrate: "EvolutionaryMemorySubstrate"
    ) -> Dict[str, Any]:
        """Executa ciclo de reflexao, consolidando insights.

        Args:
            memory_substrate: Instancia completa do substrate.

        Returns:
            Dict com reflection_id, timestamp, insights_count, insights.
        """
        insights = []

        # Insight 1: status da exploracao
        summary = memory_substrate.ideation.get_exploration_summary()
        if summary["total_ideas"] > 0:
            insights.append(
                f"Exploration: {summary['total_ideas']} ideas explored, "
                f"{summary['success_rate']*100:.0f}% success rate, "
                f"avg score {summary['avg_score']:.1f}"
            )

        # Insight 2: tendencia de novidade
        trend = memory_substrate.stagnation.get_novelty_trend()
        if trend == "declining":
            insights.append(
                "WARNING: Novelty trend is declining. "
                "Consider exploring new concept spaces."
            )
        elif trend == "improving":
            insights.append(
                "Positive: Novelty trend is improving. "
                "Current strategy appears effective."
            )
        else:
            insights.append(
                "Note: Novelty trend is stable. "
                "Room for breakthrough exploration."
            )

        # Insight 3: estrategias mais efetivas
        portfolio = memory_substrate.experimentation.get_strategy_portfolio()
        if portfolio:
            top_strat = portfolio[0]
            insights.append(
                f"Best strategy: '{top_strat['strategy_id']}' "
                f"(effectiveness: {top_strat['mean_effectiveness']:.1f}, "
                f"used {top_strat['n_uses']} times)"
            )

        # Insight 4: direcoes promissoras
        promising = memory_substrate.ideation.get_promising_directions(
            top_k=3, min_score=70
        )
        if promising:
            dirs = [p["direction"][:60] for p in promising]
            insights.append(
                f"Promising directions: {'; '.join(dirs)}"
            )

        # Insight 5: alerta de estagnacao
        if memory_substrate.stagnation.is_stagnated():
            report = memory_substrate.stagnation.get_stagnation_report()
            insights.append(
                f"STAGNATION ALERT: {report['recommendation']}"
            )

        reflection = {
            "reflection_id": str(uuid.uuid4())[:8],
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "insights_count": len(insights),
            "insights": insights,
        }

        self._reflections.append(reflection)
        logger.info(
            "HeartbeatReflection: %d insights generated",
            len(insights)
        )
        return reflection

    def get_reflection_history(self) -> List[Dict[str, Any]]:
        """Retorna historico de reflexoes.

        Returns:
            Lista de reflexoes ordenadas por timestamp.
        """
        return sorted(self._reflections, key=lambda r: r["timestamp"])

    def get_insights(self) -> str:
        """Retorna sintese textual dos insights mais recentes.

        Returns:
            String com insights concatenados, ou mensagem padrao.
        """
        if not self._reflections:
            return "No reflections recorded yet."
        latest = self._reflections[-1]
        insights = latest.get("insights", [])
        if not insights:
            return "No insights in latest reflection."
        return "\n".join(f"• {insight}" for insight in insights)


# ============================================================
# C4 — StagnationDetector
# ============================================================

class StagnationDetector:
    """Detector de estagnacao de novidade.

    Attributes:
        _scores: Lista de tuplas (cycle_index, score).
    """

    def __init__(self):
        self._scores: List[Tuple[int, float]] = []

    def record_novelty_score(self, cycle_index: int, score: float) -> None:
        """Alimenta serie temporal de novidade.

        Args:
            cycle_index: Indice do ciclo.
            score: Score de novidade medio do ciclo.
        """
        self._scores.append((cycle_index, float(score)))
        logger.debug("Stagnation: cycle %d score = %.2f", cycle_index, score)

    def is_stagnated(
        self, window: int = 5, threshold: float = 0.05
    ) -> bool:
        """Detecta se novidade esta estagnada nos ultimos N ciclos.

        Args:
            window: Janela de ciclos para analise.
            threshold: Variancia maxima para considerar estagnado.

        Returns:
            True se variancia dos ultimos window scores < threshold.
        """
        if len(self._scores) < 2:
            return False

        recent = self._scores[-window:]
        if len(recent) < 2:
            return False

        scores = [s[1] for s in recent]
        variance = statistics.variance(scores) if len(scores) >= 2 else 0
        return variance < threshold

    def get_stagnation_report(
        self, window: int = 5, threshold: float = 0.05
    ) -> Dict[str, Any]:
        """Retorna relatorio detalhado de estagnacao.

        Args:
            window: Janela de ciclos.
            threshold: Threshold de variancia.

        Returns:
            Dict com is_stagnated, window, variance, mean, recommendation.
        """
        if len(self._scores) < 2:
            return {
                "is_stagnated": False,
                "window": window,
                "variance": 0.0,
                "mean": 0.0,
                "recommendation": "Insufficient data.",
            }

        recent = self._scores[-window:]
        scores = [s[1] for s in recent]
        variance = statistics.variance(scores) if len(scores) >= 2 else 0
        mean = statistics.mean(scores)
        stagnated = variance < threshold

        if stagnated:
            recommendation = (
                "Novelty has plateaued. Consider exploring "
                "different concept spaces, changing generation "
                "strategies, or introducing interdisciplinary approaches."
            )
        else:
            recommendation = (
                "Novelty is evolving. Continue current exploration strategy."
            )

        return {
            "is_stagnated": stagnated,
            "window": min(window, len(scores)),
            "variance": round(variance, 4),
            "mean": round(mean, 2),
            "recommendation": recommendation,
        }

    def suggest_redirection(
        self, ideation_memory: IdeationMemory
    ) -> List[Dict[str, Any]]:
        """Sugere direcoes alternativas baseadas em falhas passadas.

        Args:
            ideation_memory: Instancia de IdeationMemory.

        Returns:
            Lista de sugestoes de direcoes alternativas.
        """
        failed = ideation_memory.get_failed_directions(max_score=40)
        suggestions = []
        for f in failed:
            direction = f.get("direction", "")
            # Sugere explorar o oposto ou uma variacao
            suggestions.append({
                "original": direction,
                "suggestion": f"Revisit '{direction}' with different methodology",
                "reason": (
                    f"Previous attempt scored {f['score']:.0f}/100. "
                    f"Consider alternative theoretical framework."
                ),
            })
        if not suggestions:
            suggestions.append({
                "original": "",
                "suggestion": "Explore entirely new concept space",
                "reason": "No failed directions to learn from.",
            })
        return suggestions

    def get_novelty_trend(self, window: int = 5) -> str:
        """Retorna tendencia de novidade.

        Args:
            window: Janela de ciclos para analise.

        Returns:
            'improving', 'stable' ou 'declining'.
        """
        if len(self._scores) < 3:
            return "stable"
        recent = self._scores[-window:]
        scores = [s[1] for s in recent]
        return _compute_trend(scores)


# ============================================================
# Classe Principal: EvolutionaryMemorySubstrate
# ============================================================

class EvolutionaryMemorySubstrate:
    """Substrato completo de memoria evolutiva.

    Compoe os 4 componentes e fornece metodos de persistencia.

    Attributes:
        ideation: IdeationMemory.
        experimentation: ExperimentationMemory.
        heartbeat: HeartbeatReflection.
        stagnation: StagnationDetector.
    """

    SCHEMA_VERSION = "1.0"

    def __init__(self):
        self.ideation = IdeationMemory()
        self.experimentation = ExperimentationMemory()
        self.heartbeat = HeartbeatReflection()
        self.stagnation = StagnationDetector()

    # --------------------------------------------------------
    # Ciclo completo
    # --------------------------------------------------------

    def run_full_reflection(self) -> Dict[str, Any]:
        """Executa ciclo completo de reflexao.

        Conveniencia: chama heartbeat.reflect() com self.

        Returns:
            Resultado da reflexao.
        """
        return self.heartbeat.reflect(self)

    # --------------------------------------------------------
    # Persistencia
    # --------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serializa estado completo para dict.

        Returns:
            Dict com schema_version, timestamp, ideation,
            experimentation, stagnation.
        """
        return {
            "schema_version": self.SCHEMA_VERSION,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "ideation": {
                "ideas": self.ideation._ideas,
            },
            "experimentation": {
                "strategies": {
                    sid: {
                        k: v for k, v in s.items()
                        if k != "timestamps"  # exclui timestamps historicos
                    }
                    for sid, s in self.experimentation._strategies.items()
                },
            },
            "stagnation": {
                "scores": self.stagnation._scores,
            },
            "reflections": {
                "history": self.heartbeat._reflections,
            },
        }

    def save(self, path: str) -> str:
        """Exporta estado completo para arquivo JSON.

        Args:
            path: Caminho do arquivo.

        Returns:
            Caminho do arquivo salvo.
        """
        data = self.to_dict()
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("EvolutionaryMemory saved to %s", path)
        return path

    @classmethod
    def load(cls, path: str) -> Optional["EvolutionaryMemorySubstrate"]:
        """Carrega estado de arquivo JSON.

        Args:
            path: Caminho do arquivo.

        Returns:
            Nova instancia com dados carregados, ou None se falhar.
        """
        if not os.path.exists(path):
            logger.warning("EvolutionaryMemory: file not found: %s", path)
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("EvolutionaryMemory: failed to load %s: %s", path, e)
            return None

        mem = cls()

        # Carrega ideation
        ideas = data.get("ideation", {}).get("ideas", [])
        mem.ideation._ideas = ideas

        # Carrega experimentation
        strategies = data.get("experimentation", {}).get("strategies", {})
        mem.experimentation._strategies = strategies

        # Carrega stagnation
        scores = data.get("stagnation", {}).get("scores", [])
        mem.stagnation._scores = [(int(s[0]), float(s[1])) for s in scores]

        # Carrega reflections
        reflections = data.get("reflections", {}).get("history", [])
        mem.heartbeat._reflections = reflections

        logger.info("EvolutionaryMemory loaded from %s", path)
        return mem
