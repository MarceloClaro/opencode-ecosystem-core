"""
MiroFish Swarm Engine — Motor de Inteligência de Enxame para Predição.

Inspirado no repositório MarceloClaro/MiroFish ("A Simple and Universal Swarm
Intelligence Engine, Predicting Anything") e na integração MiroFish/BettaFish
do OpenCode_Ecosystem original (OASIS + Forum + Config + Graph + Report +
Nash + Stats + Qualis + Sensitivity + IMRAD + Debate).

Conceito central: em vez de um único modelo prever um desfecho, um enxame de
agentes heterogêneos (cada um com um viés/estratégia de raciocínio distinto)
emite previsões independentes que são agregadas por mecanismos de mercado
(wisdom of crowds ponderada por confiança e histórico de acertos), com
validação cruzada via Teoria dos Jogos (NashSolver) e debate estruturado.

Implementação 100% stdlib, integrada ao MetaBus/Blackboard do Core.
"""
from __future__ import annotations

import json
import math
import os
import random
import statistics
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional

from mci.metabus import metabus
from mirofish.graph_memory import GraphMemory

_STATE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".mci_state"
)


# ─────────────────────────────────────────────────────────────────────
# Agente de enxame
# ─────────────────────────────────────────────────────────────────────

@dataclass
class SwarmAgent:
    """Um peixe do cardume: previsor com viés e histórico próprios."""
    agent_id: str
    bias: str = "neutral"           # optimist | pessimist | contrarian | neutral | momentum
    reasoning: str = "critical"     # ReasoningType associado (nome em minúsculas)
    accuracy_history: List[float] = field(default_factory=list)
    weight: float = 1.0

    def predict(self, signal: float, noise: float = 0.1,
                rng: Optional[random.Random] = None) -> float:
        """Emite previsão em [0,1] a partir de um sinal-base, modulada pelo viés."""
        rng = rng or random
        bias_shift = {
            "optimist": 0.10,
            "pessimist": -0.10,
            "contrarian": (0.5 - signal) * 0.6,
            "momentum": (signal - 0.5) * 0.3,
            "neutral": 0.0,
        }.get(self.bias, 0.0)
        raw = signal + bias_shift + rng.gauss(0, noise)
        return max(0.0, min(1.0, raw))

    def update_accuracy(self, error: float) -> None:
        """Atualiza histórico e peso (agentes precisos ganham influência)."""
        accuracy = max(0.0, 1.0 - error)
        self.accuracy_history.append(accuracy)
        recent = self.accuracy_history[-10:]
        self.weight = max(0.1, sum(recent) / len(recent))


# ─────────────────────────────────────────────────────────────────────
# Enxame preditivo
# ─────────────────────────────────────────────────────────────────────

DEFAULT_BIASES = ["optimist", "pessimist", "contrarian", "neutral", "momentum"]

DEFAULT_REASONINGS = [
    "critical", "bayesian", "nash_equilibrium", "evolutionary", "probabilistic",
    "inductive", "abductive", "systems", "first_principles", "counterfactual",
]


class MiroFishSwarm:
    """
    Enxame de previsão universal (wisdom of crowds ponderada).

    Uso:
        swarm = MiroFishSwarm(n_agents=25, seed=42)
        result = swarm.predict("O manuscrito será aprovado?", signal=0.7)
        swarm.feedback(result["prediction_id"], actual=1.0)
    """

    def __init__(self, n_agents: int = 25, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.agents: List[SwarmAgent] = []
        for i in range(n_agents):
            self.agents.append(SwarmAgent(
                agent_id=f"fish-{i:03d}",
                bias=DEFAULT_BIASES[i % len(DEFAULT_BIASES)],
                reasoning=DEFAULT_REASONINGS[i % len(DEFAULT_REASONINGS)],
            ))
        self.predictions: Dict[str, Dict[str, Any]] = {}
        self.graph = GraphMemory()   # memória de grafo (MiroFish-Offline)
        self._load_state()

    # ── Predição agregada ──
    def predict(self, question: str, signal: float = 0.5,
                noise: float = 0.12) -> Dict[str, Any]:
        """
        Cada agente prevê independentemente; a agregação é a média ponderada
        pelos pesos (histórico de acurácia), com intervalo de dispersão.
        """
        individual: Dict[str, float] = {}
        for agent in self.agents:
            individual[agent.agent_id] = agent.predict(signal, noise, self.rng)

        weights = {a.agent_id: a.weight for a in self.agents}
        total_w = sum(weights.values()) or 1.0
        aggregate = sum(individual[aid] * weights[aid] for aid in individual) / total_w
        values = list(individual.values())
        stdev = statistics.pstdev(values) if len(values) > 1 else 0.0

        # Consenso: 1 - dispersão normalizada (dispersão máx teórica 0.5)
        consensus = max(0.0, 1.0 - (stdev / 0.5))

        prediction_id = uuid.uuid4().hex[:12]
        record = {
            "prediction_id": prediction_id,
            "question": question,
            "signal": signal,
            "aggregate": round(aggregate, 4),
            "stdev": round(stdev, 4),
            "consensus": round(consensus, 4),
            "n_agents": len(self.agents),
            "individual": {k: round(v, 4) for k, v in individual.items()},
            "timestamp": time.time(),
            "resolved": False,
        }
        self.predictions[prediction_id] = record
        self._save_state()
        metabus.publish_subsystem_event(
            "mirofish",
            "prediction.created",
            {
                "prediction_id": prediction_id,
                "question": question,
                "aggregate": record["aggregate"],
                "consensus": record["consensus"],
            },
            source_agent="mirofish",
        )
        metabus.memory.upsert_semantic_topic(
            "mirofish.predictions",
            lesson=f"MiroFish gerou previsão agregada {record['aggregate']} para '{question[:80]}'.",
            metadata={"last_prediction_id": prediction_id, "last_consensus": record["consensus"]},
        )
        metabus.memory.update_topic_confidence("mirofish", record["consensus"])
        return record

    # ── Feedback (aprendizado do enxame) ──
    def feedback(self, prediction_id: str, actual: float) -> Dict[str, Any]:
        """Resolve a previsão: recalibra o peso de cada agente pelo erro."""
        record = self.predictions.get(prediction_id)
        if record is None:
            raise KeyError(f"Previsão desconhecida: {prediction_id}")
        for agent in self.agents:
            pred = record["individual"].get(agent.agent_id)
            if pred is not None:
                agent.update_accuracy(abs(pred - actual))
        record["resolved"] = True
        record["actual"] = actual
        record["swarm_error"] = round(abs(record["aggregate"] - actual), 4)
        self._save_state()
        metabus.publish_subsystem_event(
            "mirofish",
            "prediction.resolved",
            {
                "prediction_id": prediction_id,
                "actual": actual,
                "swarm_error": record["swarm_error"],
            },
            source_agent="mirofish",
        )
        return record

    # ── Simulação de debate interno (Forum simplificado) ──
    def debate(self, question: str, rounds: int = 3,
               signal: float = 0.5) -> Dict[str, Any]:
        """
        Debate iterativo estilo Delphi: a cada rodada os agentes veem a média
        anterior e ajustam parcialmente suas previsões (convergência social).
        """
        history: List[float] = []
        current_signal = signal
        last_result: Optional[Dict[str, Any]] = None
        for _ in range(rounds):
            result = self.predict(question, current_signal)
            history.append(result["aggregate"])
            last_result = result
            # ancoragem parcial na média do enxame (peso social 0.5)
            current_signal = 0.5 * current_signal + 0.5 * result["aggregate"]

        # Ingestão do debate no grafo de memória (MiroFish-Offline)
        graph_consensus = None
        if last_result is not None:
            opinions = [
                {"agent": aid, "position": pos,
                 "argument": f"{aid} ({self._bias_of(aid)}) prevê {pos:.2f} para: {question[:80]}"}
                for aid, pos in last_result["individual"].items()
            ]
            self.graph.ingest_debate(question, opinions)
            graph_consensus = self.graph.consensus_score()

        payload = {
            "question": question,
            "rounds": rounds,
            "trajectory": [round(v, 4) for v in history],
            "final": round(history[-1], 4),
            "converged": len(history) >= 2 and abs(history[-1] - history[-2]) < 0.02,
            "graph_consensus": graph_consensus,
            "graph_contradictions": len(self.graph.contradictions()),
        }
        metabus.publish_subsystem_event(
            "mirofish",
            "debate.completed",
            {
                "question": question,
                "final": payload["final"],
                "converged": payload["converged"],
                "graph_consensus": graph_consensus,
            },
            source_agent="mirofish",
        )
        return payload

    def _bias_of(self, agent_id: str) -> str:
        for a in self.agents:
            if a.agent_id == agent_id:
                return a.bias
        return "neutral"

    # ── Relatório ──
    def report(self) -> Dict[str, Any]:
        resolved = [p for p in self.predictions.values() if p.get("resolved")]
        errors = [p["swarm_error"] for p in resolved if "swarm_error" in p]
        top = sorted(self.agents, key=lambda a: -a.weight)[:5]
        return {
            "n_agents": len(self.agents),
            "total_predictions": len(self.predictions),
            "resolved": len(resolved),
            "mean_error": round(sum(errors) / len(errors), 4) if errors else None,
            "top_agents": [
                {"agent_id": a.agent_id, "bias": a.bias,
                 "reasoning": a.reasoning, "weight": round(a.weight, 3)}
                for a in top
            ],
        }

    # ── Persistência ──
    def _state_path(self) -> str:
        os.makedirs(_STATE_DIR, exist_ok=True)
        return os.path.join(_STATE_DIR, "mirofish_swarm.json")

    def _save_state(self) -> None:
        try:
            data = {
                "agents": [asdict(a) for a in self.agents],
                "predictions": self.predictions,
            }
            with open(self._state_path(), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except OSError:
            pass

    def _load_state(self) -> None:
        try:
            with open(self._state_path(), "r", encoding="utf-8") as f:
                data = json.load(f)
            saved = {a["agent_id"]: a for a in data.get("agents", [])}
            for agent in self.agents:
                if agent.agent_id in saved:
                    s = saved[agent.agent_id]
                    agent.accuracy_history = s.get("accuracy_history", [])
                    agent.weight = s.get("weight", 1.0)
            self.predictions = data.get("predictions", {})
        except (OSError, json.JSONDecodeError, KeyError):
            pass
