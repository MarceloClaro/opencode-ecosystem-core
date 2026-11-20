# -*- coding: utf-8 -*-
"""
Blackboard Architecture & Agent Cards (A2A Protocol)
====================================================
Implementa um quadro negro compartilhado onde agentes se voluntariam para tarefas
baseados em suas capacidades declaradas via Agent Cards.

Inspirado em:
- LLM-Based Multi-Agent Blackboard System (arXiv:2510.01285)
- Agent-to-Agent Protocol (A2A) / Agent Cards (arXiv:2505.02279)

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import os
import json
import uuid
import logging
import math
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from .metabus import metabus

logger = logging.getLogger("mci-blackboard")
logger.setLevel(logging.INFO)


def _live_confidence(agent_id: str) -> float:
    """Lê e normaliza a confiança atual, sem reutilizar snapshot do cartão."""

    value = metabus.memory.confidence_ledger.get(agent_id, 0.5)
    if isinstance(value, bool):
        return 0.5
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.5
    if not math.isfinite(score):
        return 0.5
    return max(0.0, min(1.0, score))


_LOAD_REFERENCE_CAPACITY = 5
ACTIVE_TASK_STATES = frozenset({"assigned"})


def _live_load(agent_id: str) -> float:
    """Carga real em [0, 1]: tarefas hoje atribuídas a este agente sobre uma
    capacidade de referência (não apenas "ocupado agora" — agentes ocupados
    já são excluídos antes da fase de pontuação pelos hard gates do
    AttentionRouter, então diferenciar só por status "busy"/"available"
    não daria sinal algum entre os elegíveis). Sem isso, ``AgentCard.
    to_dict()`` nunca publicava a chave ``load``, e ``_head_load`` caía
    sempre no mesmo valor constante para todo agente, tornando 10% do peso
    da decisão de roteamento por atenção pura constante sem diferenciação."""

    active = sum(
        1
        for task in blackboard.tasks.values()
        if task.assigned_to == agent_id and task.status in ACTIVE_TASK_STATES
    )
    if _LOAD_REFERENCE_CAPACITY <= 0:
        return 0.0
    return max(0.0, min(1.0, active / _LOAD_REFERENCE_CAPACITY))


def _capability_set(value: Any) -> Optional[set[str]]:
    """Normaliza capacidades sem dividir strings em caracteres."""

    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple, set, frozenset)):
        return None
    if any(not isinstance(item, str) or not item.strip() for item in value):
        return None
    return {item.strip() for item in value}


class AgentCard:
    """Representa as capacidades de um agente (Padrão A2A Protocol)."""
    def __init__(self, agent_id: str, name: str, description: str, capabilities: List[str], schema: Dict[str, Any]):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.input_schema = schema
        self.status = "available"
        self.confidence_score = metabus.memory.confidence_ledger.get(agent_id, 0.5)

    def to_dict(self):
        # O ledger é a fonte viva; ``confidence_score`` permanece apenas como
        # atributo compatível com consumidores legados do AgentCard.
        self.confidence_score = _live_confidence(self.agent_id)
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "status": self.status,
            "confidence_score": self.confidence_score,
            "load": _live_load(self.agent_id),
        }


class BlackboardTask:
    """Uma tarefa postada no Blackboard."""
    def __init__(self, task_id: str, description: str, required_capabilities: List[str], context: Dict[str, Any]):
        self.task_id = task_id
        self.description = description
        self.required_capabilities = required_capabilities
        self.context = context
        self.status = "open" # open, assigned, completed, failed, blocked, awaiting_supervision
        self.assigned_to: Optional[str] = None
        self.result: Optional[Any] = None
        self.created_at = datetime.now(timezone.utc).isoformat()
        # Snapshot da elegibilidade do CFP corrente. A atribuição ainda refaz
        # os gates para evitar que uma resposta atrasada reserve agente inelegível.
        self.eligible_agents: List[str] = []
        self.supervision_required = False
        self.supervision_candidates: List[Dict[str, Any]] = []
        self.blocked_reason: Optional[str] = None


class Blackboard:
    """O quadro negro central para coordenação multi-agente."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Blackboard, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        if self._initialized:
            return
        self.registry: Dict[str, AgentCard] = {}
        self.tasks: Dict[str, BlackboardTask] = {}
        self._initialized = True
        
        # Inscreve no MetaBus
        metabus.subscribe("agent.register", self._handle_registration)
        metabus.subscribe("task.post", self._handle_task_post)
        metabus.subscribe("task.volunteer", self._handle_volunteer)
        metabus.subscribe("task.complete", self._handle_completion)

    def _handle_registration(self, event: Dict[str, Any]):
        payload = event.get("payload", {})
        card = AgentCard(
            agent_id=payload.get("agent_id"),
            name=payload.get("name"),
            description=payload.get("description"),
            capabilities=payload.get("capabilities", []),
            schema=payload.get("schema", {})
        )
        self.registry[card.agent_id] = card
        logger.info(f"Agente registrado no Blackboard: {card.name} ({card.agent_id})")

    def _handle_task_post(self, event: Dict[str, Any]):
        payload = event.get("payload", {})
        raw_task_id = payload.get("task_id")
        task_id = raw_task_id if isinstance(raw_task_id, str) and raw_task_id.strip() else str(uuid.uuid4())
        task = BlackboardTask(
            task_id=task_id.strip(),
            description=payload.get("description"),
            required_capabilities=payload.get("required_capabilities", []),
            context=payload.get("context", {})
        )
        self.tasks[task.task_id] = task
        logger.info(f"Nova tarefa postada no Blackboard: {task.task_id}")
        
        # Notifica agentes disponíveis que possuem as capacidades
        self._match_task(task)

    def _match_task(self, task: BlackboardTask):
        """Busca agentes elegíveis e emite Call for Proposals (CFP)."""
        if task.status != "open":
            return
        eligible = []
        required = _capability_set(task.required_capabilities)
        if required is None:
            task.status = "blocked"
            task.blocked_reason = "invalid_required_capabilities"
            task.eligible_agents = []
            return
        for agent_id, card in self.registry.items():
            if card.status != "available":
                continue
            # Capacidades obrigatórias têm semântica all_of, nunca any_of.
            capabilities = _capability_set(card.capabilities)
            if capabilities is not None and required.issubset(capabilities):
                eligible.append(card)
                
        if eligible:
            # Consulta o ledger no instante da decisão e desempata por ID.
            for card in eligible:
                card.confidence_score = _live_confidence(card.agent_id)
            eligible.sort(key=lambda card: (-card.confidence_score, card.agent_id))
            task.eligible_agents = [card.agent_id for card in eligible]
            metabus.publish("task.cfp", {
                "task_id": task.task_id,
                "description": task.description,
                "eligible_agents": list(task.eligible_agents),
            }, source_agent="blackboard")
        else:
            task.eligible_agents = []
            task.status = "blocked"
            task.blocked_reason = "no_eligible_agent"
            
    def _handle_volunteer(self, event: Dict[str, Any]):
        payload = event.get("payload", {})
        task_id = payload.get("task_id")
        agent_id = payload.get("agent_id")
        if not isinstance(task_id, str) or not task_id.strip():
            return
        task_id = task_id.strip()
        task = self.tasks.get(task_id)
        if not task or task.status != "open":
            return
        if not isinstance(agent_id, str) or not agent_id.strip():
            return
        agent_id = agent_id.strip()
        card = self.registry.get(agent_id)
        if card is None or agent_id not in task.eligible_agents or card.status != "available":
            return
        required = _capability_set(task.required_capabilities)
        capabilities = _capability_set(card.capabilities)
        if required is None or capabilities is None or not required.issubset(capabilities):
            return

        task.status = "assigned"
        task.assigned_to = agent_id
        card.status = "busy"

        metabus.publish("task.assigned", {
            "task_id": task_id,
            "agent_id": agent_id
        }, source_agent="blackboard")
        logger.info(f"Tarefa {task_id} atribuída ao agente {agent_id}")

    def _handle_completion(self, event: Dict[str, Any]):
        payload = event.get("payload", {})
        task_id = payload.get("task_id")
        agent_id = payload.get("agent_id")
        status = payload.get("status", "completed") # completed or failed
        if not isinstance(task_id, str) or not task_id.strip():
            return
        task_id = task_id.strip()
        task = self.tasks.get(task_id)
        if (
            not task
            or task.status != "assigned"
            or task.assigned_to != agent_id
            or not isinstance(status, str)
            or status not in {"completed", "failed"}
        ):
            return

        task.status = status
        task.result = payload.get("result")

        card = self.registry.get(agent_id)
        if card is not None:
            still_assigned = any(
                other.task_id != task_id
                and other.assigned_to == agent_id
                and other.status in ACTIVE_TASK_STATES
                for other in self.tasks.values()
            )
            card.status = "busy" if still_assigned else "available"

        # Dispara uma única reflexão, após validar a transição de estado.
        metabus.publish("metacognition.reflect_request", {
            "task_id": task_id,
            "agent_id": agent_id,
            "context": task.description,
            "result": task.result,
            "success": status == "completed",
            "sdd_verification": payload.get("sdd_verification"),
        }, source_agent="blackboard")

        logger.info(f"Tarefa {task_id} finalizada por {agent_id} com status {status}")

# Instância global Singleton
blackboard = Blackboard()
