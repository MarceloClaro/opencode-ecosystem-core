"""
MiroFish Social — motor de simulação determinístico (MIT, stdlib).

Simula rounds de interação em plataforma social: agentes ativos por faixa de
horário postam/curtem/repostam; opinião evolui por influência ponderada e
efeito câmara de eco. 100% stdlib, seed fixa → determinístico.
"""
from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from .contracts import (
    AgentActivityConfig,
    EventConfig,
    OasisAgentProfile,
    PlatformConfig,
    SimulationParameters,
    TimeSimulationConfig,
)

_STATE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    ".mci_state",
)

ACTIONS = ["CREATE_POST", "LIKE_POST", "REPOST", "QUOTE_POST", "DO_NOTHING"]


@dataclass
class AgentAction:
    round_num: int
    timestamp: str
    platform: str
    agent_id: int
    agent_name: str
    action_type: str
    action_args: Dict[str, Any] = field(default_factory=dict)
    success: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RoundSummary:
    round_num: int
    started_at_hour: int
    active_agents: List[int]
    actions: List[AgentAction] = field(default_factory=list)
    avg_sentiment: float = 0.0
    followers_gained: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "round_num": self.round_num,
            "started_at_hour": self.started_at_hour,
            "active_agents": self.active_agents,
            "actions": [a.to_dict() for a in self.actions],
            "avg_sentiment": self.avg_sentiment,
            "followers_gained": self.followers_gained,
        }


@dataclass
class SimulationResult:
    simulation_id: str
    parameters: SimulationParameters
    profiles: List[OasisAgentProfile]
    rounds: List[RoundSummary] = field(default_factory=list)
    final_opinions: Dict[int, float] = field(default_factory=dict)
    seed: Optional[int] = None
    completed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "parameters": self.parameters.to_dict(),
            "profiles": [p.to_dict() for p in self.profiles],
            "rounds": [r.to_dict() for r in self.rounds],
            "final_opinions": self.final_opinions,
            "seed": self.seed,
            "completed": self.completed,
        }


class SocialSimulationEngine:
    """Executa a simulação social round a round (determinístico com seed)."""

    def __init__(
        self,
        profiles: List[OasisAgentProfile],
        parameters: SimulationParameters,
        seed: Optional[int] = None,
    ):
        self.profiles = profiles
        self.parameters = parameters
        self.seed = seed if seed is not None else 42
        self._rng = random.Random(self.seed)
        self._opinions: Dict[int, float] = {
            p.user_id: p.sentiment_bias for p in profiles
        }

    # ── faixa horária ───────────────────────────────────────────────

    def _hour_multiplier(self, hour: int, tc: TimeSimulationConfig) -> float:
        if hour in tc.peak_hours:
            return tc.peak_activity_multiplier
        if hour in tc.off_peak_hours:
            return tc.off_peak_activity_multiplier
        if hour in tc.morning_hours:
            return tc.morning_activity_multiplier
        if hour in tc.work_hours:
            return tc.work_activity_multiplier
        return 1.0

    def _active_agents(self, hour: int) -> List[OasisAgentProfile]:
        tc = self.parameters.time_config
        multiplier = self._hour_multiplier(hour, tc)
        result: List[OasisAgentProfile] = []
        for p in self.profiles:
            # Faixa ativa determinística por agente: janela de 12h deslocada pelo id
            start = (p.user_id * 3) % 12
            active_hours = [(start + h) % 24 for h in range(12)]
            if hour in active_hours:
                prob = p.activity_level * multiplier
                if self._rng.random() < prob:
                    result.append(p)
        return result

    # ── ação ────────────────────────────────────────────────────────

    def _pick_action(self, profile: OasisAgentProfile) -> str:
        # Agentes com mais influência tendem a criar conteúdo
        r = self._rng.random()
        influence = profile.influence_weight
        if r < 0.20 * min(1.0, influence):
            return "CREATE_POST"
        if r < 0.45:
            return "LIKE_POST"
        if r < 0.62:
            return "REPOST"
        if r < 0.75:
            return "QUOTE_POST"
        return "DO_NOTHING"

    def _post_text(self, profile: OasisAgentProfile, topics: List[str]) -> str:
        topic = self._rng.choice(topics) if topics else "notícia"
        if profile.sentiment_bias > 0.3:
            return f"Apoio a evolução em {topic}. #opinião"
        if profile.sentiment_bias < -0.3:
            return f"Preocupação com os rumos de {topic}. #debate"
        return f"Observações sobre {topic}. #análise"

    # ── opinião ─────────────────────────────────────────────────────

    def _update_opinion(self, active: List[OasisAgentProfile], pc: PlatformConfig) -> None:
        if not active:
            return
        for p in active:
            # Referência: câmara de eco forte → grupo da MESMA postura;
            # eco fraco → grupo completo (mistura global).
            if pc.echo_chamber_strength > 0.5:
                reference = [q for q in active if q.stance == p.stance] or active
            else:
                reference = active
            group_mean = sum(self._opinions[q.user_id] for q in reference) / len(reference)
            cur = self._opinions[p.user_id]
            pull = pc.echo_chamber_strength * (0.4 - 0.1 * p.influence_weight)
            drift = (group_mean - cur) * max(0.0, pull) * p.activity_level
            # Contrários mantêm ceticismo: pequena resistência à convergência.
            if p.stance == "opposing":
                drift -= pc.echo_chamber_strength * 0.02
            new_val = cur + drift
            self._opinions[p.user_id] = max(-1.0, min(1.0, new_val))

    # ── run ─────────────────────────────────────────────────────────

    def run(self, rounds: Optional[int] = None, platform: str = "twitter") -> SimulationResult:
        params = self.parameters
        tc = params.time_config
        total_rounds = rounds or max(
            1, int(tc.total_simulation_hours * 60 / max(1, tc.minutes_per_round))
        )
        pc = params.twitter_config or PlatformConfig(platform=platform)
        topics = params.event_config.hot_topics or ["notícia"]
        result = SimulationResult(
            simulation_id=params.simulation_id,
            parameters=params,
            profiles=self.profiles,
            seed=self.seed,
        )

        for round_num in range(1, total_rounds + 1):
            simulated_hour = (round_num - 1) * (tc.minutes_per_round // 60) % 24
            active = self._active_agents(simulated_hour)
            summary = RoundSummary(
                round_num=round_num,
                started_at_hour=simulated_hour,
                active_agents=[p.user_id for p in active],
            )
            for profile in active:
                action = self._pick_action(profile)
                args: Dict[str, Any] = {}
                if action in ("CREATE_POST", "QUOTE_POST"):
                    args["text"] = self._post_text(profile, topics)
                summary.actions.append(
                    AgentAction(
                        round_num=round_num,
                        timestamp=f"h+{simulated_hour}",
                        platform=platform,
                        agent_id=profile.user_id,
                        agent_name=profile.user_name,
                        action_type=action,
                        action_args=args,
                    )
                )
            if active:
                summary.avg_sentiment = round(
                    sum(self._opinions[p.user_id] for p in active) / len(active), 4
                )
            self._update_opinion(active, pc)
            result.rounds.append(summary)

        result.final_opinions = {k: round(v, 4) for k, v in self._opinions.items()}
        result.completed = total_rounds > 0
        return result

    # ── persistência ────────────────────────────────────────────────

    def save(self, result: SimulationResult) -> str:
        os.makedirs(_STATE_DIR, exist_ok=True)
        path = os.path.join(_STATE_DIR, f"mirofish_social_{result.simulation_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        return path

    @classmethod
    def load(cls, simulation_id: str) -> SimulationResult:
        path = os.path.join(_STATE_DIR, f"mirofish_social_{simulation_id}.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        params = SimulationParameters.from_dict(data["parameters"])
        profiles = [OasisAgentProfile(**{k: v for k, v in p.items() if k != "interested_topics" or v} | {"interested_topics": p.get("interested_topics") or []}) for p in data["profiles"]]
        rounds = [
            RoundSummary(
                round_num=r["round_num"],
                started_at_hour=r["started_at_hour"],
                active_agents=r["active_agents"],
                actions=[AgentAction(**a) for a in r["actions"]],
                avg_sentiment=r["avg_sentiment"],
                followers_gained=r["followers_gained"],
            )
            for r in data["rounds"]
        ]
        result = SimulationResult(
            simulation_id=simulation_id,
            parameters=params,
            profiles=profiles,
            rounds=rounds,
            final_opinions=data.get("final_opinions", {}),
            seed=data.get("seed"),
            completed=data.get("completed", True),
        )
        return result