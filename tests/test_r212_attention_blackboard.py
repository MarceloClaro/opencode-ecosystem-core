# -*- coding: utf-8 -*-
"""Testes RED da SPEC-935-R212 para Blackboard e roteamento por atenção.

Os testes são herméticos: não carregam o catálogo, não acessam a rede e isolam
os singletons globais do MetaBus, Blackboard e registro de loop specs.
"""

from __future__ import annotations

import importlib
import math
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from marceloclaro.orchestrator import MarceloClaroOrchestrator
from mci.blackboard import AgentCard, Blackboard, BlackboardTask, blackboard
from mci.metabus import MetaBus, metabus
from sdd.loop_spec import LoopSpecRegistry, loop_spec_registry
from transformer.attention import AttentionRouter
from transformer.embedder import D_MODEL


@pytest.fixture(autouse=True)
def _isolate_global_singletons(monkeypatch: pytest.MonkeyPatch, tmp_path):
    """Entrega estado vazio a cada teste e restaura os singletons ao final."""

    metabus_module = importlib.import_module("mci.metabus")
    snapshot = {
        "subscribers": metabus.subscribers,
        "episodic": metabus.memory.episodic,
        "semantic": metabus.memory.semantic,
        "confidence_ledger": metabus.memory.confidence_ledger,
        "registry": blackboard.registry,
        "tasks": blackboard.tasks,
        "loops": loop_spec_registry.loops,
        "metabus_instance": MetaBus._instance,
        "blackboard_instance": Blackboard._instance,
        "loop_registry_instance": LoopSpecRegistry._instance,
    }

    metabus.subscribers = {}
    metabus.memory.episodic = []
    metabus.memory.semantic = {}
    metabus.memory.confidence_ledger = {}
    blackboard.registry = {}
    blackboard.tasks = {}
    loop_spec_registry.loops = {}
    MetaBus._instance = metabus
    Blackboard._instance = blackboard
    LoopSpecRegistry._instance = loop_spec_registry
    monkeypatch.setattr(metabus_module, "EVENTS_FILE", str(tmp_path / "events.jsonl"))

    try:
        yield
    finally:
        metabus.subscribers = snapshot["subscribers"]
        metabus.memory.episodic = snapshot["episodic"]
        metabus.memory.semantic = snapshot["semantic"]
        metabus.memory.confidence_ledger = snapshot["confidence_ledger"]
        blackboard.registry = snapshot["registry"]
        blackboard.tasks = snapshot["tasks"]
        loop_spec_registry.loops = snapshot["loops"]
        MetaBus._instance = snapshot["metabus_instance"]
        Blackboard._instance = snapshot["blackboard_instance"]
        LoopSpecRegistry._instance = snapshot["loop_registry_instance"]


def _register_card(
    agent_id: str,
    capabilities: list[str],
    *,
    confidence: float = 0.5,
    status: str = "available",
    description: str = "agente de teste",
) -> AgentCard:
    """Registra um AgentCard local com confiança inicial controlada."""

    metabus.memory.confidence_ledger[agent_id] = confidence
    card = AgentCard(
        agent_id=agent_id,
        name=agent_id,
        description=description,
        capabilities=capabilities,
        schema={},
    )
    card.status = status
    blackboard.registry[agent_id] = card
    return card


def _router_card(
    agent_id: str,
    *,
    capabilities: list[str] | None = None,
    confidence: float = 0.5,
    status: str = "available",
    description: str = "agente de teste",
) -> dict[str, Any]:
    """Cria um cartão em forma de dicionário para o AttentionRouter."""

    return {
        "agent_id": agent_id,
        "name": agent_id,
        "description": description,
        "capabilities": capabilities or ["python", "review"],
        "confidence_score": confidence,
        "status": status,
    }


def _capture_publications(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """Substitui a publicação por um coletor sem efeitos externos."""

    publications: list[dict[str, Any]] = []

    def fake_publish(topic: str, payload: dict[str, Any], source_agent: str = "system") -> int:
        publications.append({"topic": topic, "payload": payload, "source": source_agent})
        return 1

    monkeypatch.setattr(metabus, "publish", fake_publish)
    return publications


def _cfp_payloads(publications: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item["payload"] for item in publications if item["topic"] == "task.cfp"]


def _volunteer_payloads(publications: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item["payload"] for item in publications if item["topic"] == "task.volunteer"]


def _unit_vector(index: int, sign: float = 1.0) -> list[float]:
    vector = [0.0] * D_MODEL
    vector[index] = sign
    return vector


class _FixedEmbedder:
    """Double determinístico para exercitar os extremos da cabeça semântica."""

    def __init__(self, task_vector: list[float], agent_vectors: dict[str, list[float]]):
        self.task_vector = task_vector
        self.agent_vectors = agent_vectors

    def embed_task(
        self,
        description: str,
        required_capabilities: list[str],
        positional_index: int = 0,
    ) -> list[float]:
        return list(self.task_vector)

    def embed_agent(self, card: dict[str, Any]) -> list[float]:
        return list(self.agent_vectors[card["agent_id"]])


class _PositionSensitiveEmbedder:
    """Expõe qualquer uso indevido do índice global no ranking."""

    def embed_task(
        self,
        description: str,
        required_capabilities: list[str],
        positional_index: int = 0,
    ) -> list[float]:
        return _unit_vector(0 if positional_index == 0 else 1)

    def embed_agent(self, card: dict[str, Any]) -> list[float]:
        return _unit_vector(0 if card["agent_id"] == "agent-a" else 1)


class _SelectiveTrust:
    """Trust Engine local que autoriza somente agentes explicitados."""

    def __init__(self, allowed_agents: set[str]):
        self.allowed_agents = allowed_agents

    def execute(self, action_id: str):
        agent_id = action_id.removeprefix("delegate:")
        allowed = agent_id in self.allowed_agents
        return SimpleNamespace(
            allowed=allowed,
            reason="permitido pelo teste" if allowed else "bloqueado pelo teste",
        )


class _NoopEconomy:
    """Evita efeitos econômicos nos testes unitários do gate."""

    def post_task(self, *args, **kwargs):
        return None

    def commit(self, *args, **kwargs):
        return None


class _NoopReduction:
    """Nunca atinge o threshold — força o fallback de atenção multi-cabeça,
    preservando o comportamento testado antes da integração SPEC-967."""

    def route(self, description: str) -> dict[str, Any]:
        return {"agent": "", "confidence": 0.0, "method": "noop"}


def _bare_orchestrator(allowed_agents: set[str]) -> MarceloClaroOrchestrator:
    """Monta somente o estado utilizado por ``_on_cfp``."""

    orchestrator = object.__new__(MarceloClaroOrchestrator)
    orchestrator.id = "marceloclaro"
    orchestrator.pending_cfps = {}
    orchestrator.trust = _SelectiveTrust(allowed_agents)
    orchestrator.attention_router = AttentionRouter()
    orchestrator.economy = _NoopEconomy()
    orchestrator.task_stakes = {}
    orchestrator._task_counter = 0
    orchestrator.reduction_layer = _NoopReduction()
    orchestrator.reduction_threshold = 0.85
    orchestrator._llm_calls_saved = 0
    return orchestrator


def _configured_logical_orchestrator(allowed_agents: set[str]) -> MarceloClaroOrchestrator:
    """Cria uma instância lógica real sem catálogo nem integrações externas."""

    orchestrator = MarceloClaroOrchestrator(auto_load_agents=False)
    orchestrator.trust = _SelectiveTrust(allowed_agents)
    orchestrator.economy = _NoopEconomy()
    return orchestrator


def _head_scores(explanation: dict[str, Any]) -> list[float]:
    return [
        float(score)
        for scores_by_agent in explanation["heads"].values()
        for score in scores_by_agent.values()
    ]


def _ranked_agent_ids(ranking: list[Any]) -> list[str]:
    ids: list[str] = []
    for item in ranking:
        if isinstance(item, dict):
            ids.append(str(item["agent_id"]))
        else:
            ids.append(str(item[0]))
    return ids


def _excluded_agent_ids(excluded: Any) -> set[str]:
    if isinstance(excluded, dict):
        return {str(agent_id) for agent_id in excluded}

    ids: set[str] = set()
    for item in excluded:
        if isinstance(item, dict):
            ids.add(str(item["agent_id"]))
        else:
            ids.add(str(item))
    return ids


class TestR212BlackboardAllOf:
    """CA13: capacidades obrigatórias usam semântica ``all_of``."""

    def test_agent_with_every_required_capability_receives_cfp(self, monkeypatch):
        # Arrange
        task = BlackboardTask("task-all", "pesquisar e citar", ["search", "cite"], {})
        _register_card("complete", ["search", "cite", "review"])
        publications = _capture_publications(monkeypatch)

        # Act
        blackboard._match_task(task)

        # Assert
        cfps = _cfp_payloads(publications)
        assert len(cfps) == 1
        assert cfps[0]["eligible_agents"] == ["complete"]

    def test_agent_with_only_one_required_capability_is_excluded(self, monkeypatch):
        # Arrange
        task = BlackboardTask("task-partial", "pesquisar e citar", ["search", "cite"], {})
        _register_card("partial", ["search"])
        publications = _capture_publications(monkeypatch)

        # Act
        blackboard._match_task(task)

        # Assert
        assert _cfp_payloads(publications) == []


class TestR212TrustFailClosed:
    """CA14: o Behavioral Gate nunca reutiliza a lista anterior como fallback."""

    def test_allowed_agent_is_selected_while_denied_agent_stays_excluded(self, monkeypatch):
        # Arrange
        task = BlackboardTask("task-mixed-trust", "implementar", ["python"], {})
        blackboard.tasks[task.task_id] = task
        _register_card("denied", ["python"])
        _register_card("allowed", ["python"])
        orchestrator = _bare_orchestrator({"allowed"})
        publications = _capture_publications(monkeypatch)
        event = {
            "payload": {
                "task_id": task.task_id,
                "description": task.description,
                "eligible_agents": ["denied", "allowed"],
            }
        }

        # Act
        orchestrator._on_cfp(event)

        # Assert
        assert orchestrator.pending_cfps[task.task_id] == ["allowed"]
        assert _volunteer_payloads(publications) == [
            {"task_id": task.task_id, "agent_id": "allowed"}
        ]

    def test_all_denied_agents_leave_task_blocked_without_fallback(self, monkeypatch):
        # Arrange
        task = BlackboardTask("task-denied", "implementar", ["python"], {})
        blackboard.tasks[task.task_id] = task
        _register_card("denied-a", ["python"])
        _register_card("denied-b", ["python"])
        orchestrator = _bare_orchestrator(set())
        publications = _capture_publications(monkeypatch)
        event = {
            "payload": {
                "task_id": task.task_id,
                "description": task.description,
                "eligible_agents": ["denied-a", "denied-b"],
            }
        }

        # Act
        orchestrator._on_cfp(event)

        # Assert
        assert _volunteer_payloads(publications) == []
        assert not orchestrator.pending_cfps.get(task.task_id)
        assert task.assigned_to is None
        assert task.status == "blocked"


class TestR212NormalizedAttention:
    """CA15: cabeças e pesos obedecem aos invariantes numéricos."""

    def test_all_heads_stay_in_unit_interval_at_positive_extreme(self):
        # Arrange
        router = AttentionRouter()
        router.embedder = _FixedEmbedder(
            _unit_vector(0),
            {"matching": _unit_vector(0)},
        )
        cards = [_router_card("matching", confidence=0.9)]

        # Act
        explanation = router.explain("implementar e revisar", ["python", "review"], cards)

        # Assert
        scores = _head_scores(explanation)
        assert scores
        assert all(0.0 <= score <= 1.0 for score in scores)

    def test_all_heads_stay_in_unit_interval_at_negative_semantic_extreme(self):
        # Arrange
        router = AttentionRouter()
        router.embedder = _FixedEmbedder(
            _unit_vector(0),
            {"opposite": _unit_vector(0, sign=-1.0)},
        )
        cards = [_router_card("opposite", confidence=0.5)]

        # Act
        explanation = router.explain("implementar e revisar", ["python", "review"], cards)

        # Assert
        scores = _head_scores(explanation)
        assert scores
        assert all(0.0 <= score <= 1.0 for score in scores)

    def test_default_head_weights_are_a_convex_combination(self):
        # Arrange
        weights = AttentionRouter.HEAD_WEIGHTS

        # Act
        total = math.fsum(weights.values())

        # Assert
        assert set(weights) == {"semantic", "capability", "confidence", "load"}
        assert all(math.isfinite(weight) and 0.0 <= weight <= 1.0 for weight in weights.values())
        assert total == pytest.approx(1.0)

    def test_invalid_head_weights_are_rejected_or_normalized(self):
        # Arrange
        class InvalidWeightsRouter(AttentionRouter):
            HEAD_WEIGHTS = {
                "semantic": 0.20,
                "capability": 0.20,
                "confidence": 0.20,
                "load": 0.20,
            }

        # Act
        try:
            router = InvalidWeightsRouter()
        except ValueError:
            router = None

        # Assert
        assert router is None or math.fsum(router.HEAD_WEIGHTS.values()) == pytest.approx(1.0)


class TestR212DeterministicRanking:
    """CA15: a ordem global das tarefas não participa da decisão."""

    @staticmethod
    def _router_and_cards() -> tuple[AttentionRouter, list[dict[str, Any]]]:
        router = AttentionRouter()
        router.embedder = _PositionSensitiveEmbedder()
        cards = [
            _router_card("agent-a", confidence=0.5),
            _router_card("agent-b", confidence=0.5),
        ]
        return router, cards

    def test_repeated_routing_with_same_input_is_deterministic(self):
        # Arrange
        router, cards = self._router_and_cards()

        # Act
        first = router.route("implementar", ["python", "review"], cards, positional_index=0)
        second = router.route("implementar", ["python", "review"], cards, positional_index=0)

        # Assert
        assert first == second

    def test_ranking_is_independent_of_positional_index(self):
        # Arrange
        router, cards = self._router_and_cards()

        # Act
        first = router.route("implementar", ["python", "review"], cards, positional_index=0)
        after_other_tasks = router.route(
            "implementar",
            ["python", "review"],
            cards,
            positional_index=999,
        )

        # Assert
        assert first == after_other_tasks


class TestR212ExplainContract:
    """CA16: a auditoria torna gates e cálculo da decisão observáveis."""

    def test_explain_includes_excluded_heads_utility_and_ranking(self):
        # Arrange
        router = AttentionRouter()
        cards = [_router_card("eligible")]

        # Act
        explanation = router.explain("implementar", ["python", "review"], cards)

        # Assert
        assert {"excluded", "heads", "utility", "ranking"} <= explanation.keys()
        assert set(explanation["heads"]) == {"semantic", "capability", "confidence", "load"}
        assert explanation["utility"] is not None
        assert _ranked_agent_ids(explanation["ranking"]) == ["eligible"]

    def test_explain_reports_hard_gate_exclusions_outside_ranking(self):
        # Arrange
        router = AttentionRouter()
        cards = [
            _router_card("eligible"),
            _router_card("partial", capabilities=["python"]),
            _router_card("busy", status="busy"),
        ]

        # Act
        explanation = router.explain("implementar", ["python", "review"], cards)

        # Assert
        assert "excluded" in explanation
        assert _excluded_agent_ids(explanation["excluded"]) == {"partial", "busy"}
        assert _ranked_agent_ids(explanation["ranking"]) == ["eligible"]


class TestR212LiveConfidenceLedger:
    """CA13: o CFP usa a confiança presente no ledger no instante da decisão."""

    def test_blackboard_orders_agents_by_current_ledger_on_registration(self, monkeypatch):
        # Arrange
        task = BlackboardTask("task-ledger-current", "implementar", ["python"], {})
        _register_card("high", ["python"], confidence=0.9)
        _register_card("low", ["python"], confidence=0.1)
        publications = _capture_publications(monkeypatch)

        # Act
        blackboard._match_task(task)

        # Assert
        cfps = _cfp_payloads(publications)
        assert len(cfps) == 1
        assert cfps[0]["eligible_agents"] == ["high", "low"]

    def test_blackboard_refreshes_confidence_after_agent_registration(self, monkeypatch):
        # Arrange
        task = BlackboardTask("task-ledger-live", "implementar", ["python"], {})
        _register_card("formerly-high", ["python"], confidence=0.9)
        _register_card("now-high", ["python"], confidence=0.1)
        metabus.memory.confidence_ledger.update({"formerly-high": 0.05, "now-high": 0.95})
        publications = _capture_publications(monkeypatch)

        # Act
        blackboard._match_task(task)

        # Assert
        cfps = _cfp_payloads(publications)
        assert len(cfps) == 1
        assert cfps[0]["eligible_agents"] == ["now-high", "formerly-high"]


class TestR212IdempotentLogicalSubscriptions:
    """CA22: uma identidade lógica produz um único efeito por evento."""

    @staticmethod
    def _arrange_task() -> BlackboardTask:
        task = BlackboardTask("task-subscription", "implementar", ["python"], {})
        blackboard.tasks[task.task_id] = task
        _register_card("worker", ["python"])
        return task

    @staticmethod
    def _publish_cfp(task: BlackboardTask) -> None:
        metabus.publish(
            "task.cfp",
            {
                "task_id": task.task_id,
                "description": task.description,
                "eligible_agents": ["worker"],
            },
            source_agent="blackboard",
        )

    def test_one_logical_orchestrator_produces_one_volunteer_effect(self):
        # Arrange
        orchestrator = _configured_logical_orchestrator({"worker"})
        task = self._arrange_task()
        effects: list[dict[str, Any]] = []
        metabus.subscribe("task.volunteer", lambda event: effects.append(event["payload"]))

        # Act
        self._publish_cfp(task)

        # Assert
        assert orchestrator.id == "marceloclaro"
        assert effects == [{"task_id": task.task_id, "agent_id": "worker"}]

    def test_multiple_instances_of_same_logical_orchestrator_do_not_duplicate_effects(self):
        # Arrange
        first = _configured_logical_orchestrator({"worker"})
        second = _configured_logical_orchestrator({"worker"})
        task = self._arrange_task()
        effects: list[dict[str, Any]] = []
        metabus.subscribe("task.volunteer", lambda event: effects.append(event["payload"]))

        # Act
        self._publish_cfp(task)

        # Assert
        assert first.id == second.id == "marceloclaro"
        assert effects == [{"task_id": task.task_id, "agent_id": "worker"}]


def test_orquestrador_autonomo_usa_sdd_estrito_por_padrao():
    """Autocura/autosolução não pode aceitar entrega sem gate SDD disponível."""

    orchestrator = MarceloClaroOrchestrator(auto_load_agents=False)

    assert orchestrator.strict_sdd is True
