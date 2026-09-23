"""
MiroFish Social — contratos de dados (MIT, stdlib).

Reimplementação dos contratos do MiroFish-Offline (AGPL-3.0) em código próprio
MIT-compatível. Nenhum código-fonte do projeto original é copiado — apenas o
formato público dos dados (dataclasses) é reproduzido para interoperabilidade.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class OasisAgentProfile:
    """Perfil de agente social (contrato compatível com OASIS)."""

    user_id: int
    user_name: str
    name: str
    bio: str
    persona: str

    # Reddit
    karma: int = 1000

    # Twitter
    friend_count: int = 100
    follower_count: int = 150
    statuses_count: int = 500

    # Persona extra
    age: Optional[int] = None
    gender: Optional[str] = None
    mbti: Optional[str] = None
    country: Optional[str] = None
    profession: Optional[str] = None
    interested_topics: List[str] = field(default_factory=list)

    # Origem
    source_entity_uuid: Optional[str] = None
    source_entity_type: Optional[str] = None

    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    # Simulação (interno do Core)
    sentiment_bias: float = 0.0          # ∈ [-1, 1]
    stance: str = "neutral"              # supportive | opposing | neutral | observer
    influence_weight: float = 1.0
    activity_level: float = 0.5

    def to_reddit_format(self) -> Dict[str, Any]:
        profile = {
            "user_id": self.user_id,
            "username": self.user_name,
            "name": self.name,
            "bio": self.bio,
            "persona": self.persona,
            "karma": self.karma,
            "created_at": self.created_at,
        }
        self._add_persona_fields(profile)
        return profile

    def to_twitter_format(self) -> Dict[str, Any]:
        profile = {
            "user_id": self.user_id,
            "username": self.user_name,
            "name": self.name,
            "bio": self.bio,
            "persona": self.persona,
            "friend_count": self.friend_count,
            "follower_count": self.follower_count,
            "statuses_count": self.statuses_count,
            "created_at": self.created_at,
        }
        self._add_persona_fields(profile)
        return profile

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "name": self.name,
            "bio": self.bio,
            "persona": self.persona,
            "karma": self.karma,
            "friend_count": self.friend_count,
            "follower_count": self.follower_count,
            "statuses_count": self.statuses_count,
            "created_at": self.created_at,
            "source_entity_uuid": self.source_entity_uuid,
            "source_entity_type": self.source_entity_type,
            "sentiment_bias": self.sentiment_bias,
            "stance": self.stance,
            "influence_weight": self.influence_weight,
            "activity_level": self.activity_level,
        }
        self._add_persona_fields(d)
        return d

    def _add_persona_fields(self, target: Dict[str, Any]) -> None:
        for key in ("age", "gender", "mbti", "country", "profession"):
            value = getattr(self, key)
            if value:
                target[key] = value
        if self.interested_topics:
            target["interested_topics"] = self.interested_topics


# ══════════════════════════════════════════════════════════════════
# Configuração de simulação (contrato compatível com SimulationParameters)
# ══════════════════════════════════════════════════════════════════

@dataclass
class AgentActivityConfig:
    agent_id: int
    entity_uuid: str = ""
    entity_name: str = ""
    entity_type: str = "Person"
    activity_level: float = 0.5
    posts_per_hour: float = 1.0
    comments_per_hour: float = 2.0
    active_hours: List[int] = field(default_factory=lambda: list(range(8, 23)))
    response_delay_min: int = 5
    response_delay_max: int = 60
    sentiment_bias: float = 0.0
    stance: str = "neutral"
    influence_weight: float = 1.0


@dataclass
class TimeSimulationConfig:
    total_simulation_hours: int = 72
    minutes_per_round: int = 60
    agents_per_hour_min: int = 5
    agents_per_hour_max: int = 20
    peak_hours: List[int] = field(default_factory=lambda: [19, 20, 21, 22])
    peak_activity_multiplier: float = 1.5
    off_peak_hours: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4, 5])
    off_peak_activity_multiplier: float = 0.05
    morning_hours: List[int] = field(default_factory=lambda: [6, 7, 8])
    morning_activity_multiplier: float = 0.4
    work_hours: List[int] = field(default_factory=lambda: [9, 10, 11, 12, 13, 14, 15, 16, 17, 18])
    work_activity_multiplier: float = 0.7


@dataclass
class EventConfig:
    initial_posts: List[Dict[str, Any]] = field(default_factory=list)
    scheduled_events: List[Dict[str, Any]] = field(default_factory=list)
    hot_topics: List[str] = field(default_factory=list)
    narrative_direction: str = ""


@dataclass
class PlatformConfig:
    platform: str = "twitter"  # twitter | reddit
    recency_weight: float = 0.4
    popularity_weight: float = 0.3
    relevance_weight: float = 0.3
    viral_threshold: int = 10
    echo_chamber_strength: float = 0.5


@dataclass
class SimulationParameters:
    simulation_id: str
    project_id: str = "default"
    graph_id: str = ""
    simulation_requirement: str = ""
    time_config: TimeSimulationConfig = field(default_factory=TimeSimulationConfig)
    agent_configs: List[AgentActivityConfig] = field(default_factory=list)
    event_config: EventConfig = field(default_factory=EventConfig)
    twitter_config: Optional[PlatformConfig] = None
    reddit_config: Optional[PlatformConfig] = None
    llm_model: str = "local-deterministic"
    llm_base_url: str = ""
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    generation_reasoning: str = "reimplementation MIT (SPEC-976)"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "project_id": self.project_id,
            "graph_id": self.graph_id,
            "simulation_requirement": self.simulation_requirement,
            "time_config": asdict_safe(self.time_config),
            "agent_configs": [asdict_safe(a) for a in self.agent_configs],
            "event_config": asdict_safe(self.event_config),
            "twitter_config": asdict_safe(self.twitter_config) if self.twitter_config else None,
            "reddit_config": asdict_safe(self.reddit_config) if self.reddit_config else None,
            "llm_model": self.llm_model,
            "llm_base_url": self.llm_base_url,
            "generated_at": self.generated_at,
            "generation_reasoning": self.generation_reasoning,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationParameters":
        time_config = TimeSimulationConfig(**data.get("time_config", {}))
        agent_configs = [AgentActivityConfig(**a) for a in data.get("agent_configs", [])]
        event_config = EventConfig(**data.get("event_config", {}))
        return cls(
            simulation_id=data["simulation_id"],
            project_id=data.get("project_id", "default"),
            graph_id=data.get("graph_id", ""),
            simulation_requirement=data.get("simulation_requirement", ""),
            time_config=time_config,
            agent_configs=agent_configs,
            event_config=event_config,
            twitter_config=(
                PlatformConfig(**data["twitter_config"]) if data.get("twitter_config") else None
            ),
            reddit_config=(
                PlatformConfig(**data["reddit_config"]) if data.get("reddit_config") else None
            ),
            llm_model=data.get("llm_model", "local-deterministic"),
            llm_base_url=data.get("llm_base_url", ""),
            generated_at=data.get("generated_at", ""),
            generation_reasoning=data.get("generation_reasoning", ""),
        )


def asdict_safe(obj: Any) -> Dict[str, Any]:
    """dataclasses.asdict tolerante a campos opcionais None."""
    from dataclasses import asdict

    d = asdict(obj)
    if isinstance(d, dict):
        return {k: v for k, v in d.items() if v is not None}
    return d