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
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from .metabus import metabus

logger = logging.getLogger("mci-blackboard")
logger.setLevel(logging.INFO)

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
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "status": self.status,
            "confidence_score": self.confidence_score
        }

class BlackboardTask:
    """Uma tarefa postada no Blackboard."""
    def __init__(self, task_id: str, description: str, required_capabilities: List[str], context: Dict[str, Any]):
        self.task_id = task_id
        self.description = description
        self.required_capabilities = required_capabilities
        self.context = context
        self.status = "open" # open, assigned, completed, failed
        self.assigned_to: Optional[str] = None
        self.result: Optional[Any] = None
        self.created_at = datetime.now(timezone.utc).isoformat()
        
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
        task = BlackboardTask(
            task_id=payload.get("task_id", str(uuid.uuid4())),
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
        eligible = []
        for agent_id, card in self.registry.items():
            if card.status != "available":
                continue
            # Verifica se o agente tem alguma das capacidades requeridas
            if any(cap in card.capabilities for cap in task.required_capabilities) or not task.required_capabilities:
                eligible.append(card)
                
        if eligible:
            # Ordena por score de confiança metacognitiva
            eligible.sort(key=lambda x: x.confidence_score, reverse=True)
            metabus.publish("task.cfp", {
                "task_id": task.task_id,
                "description": task.description,
                "eligible_agents": [a.agent_id for a in eligible]
            }, source_agent="blackboard")
            
    def _handle_volunteer(self, event: Dict[str, Any]):
        payload = event.get("payload", {})
        task_id = payload.get("task_id")
        agent_id = payload.get("agent_id")
        
        task = self.tasks.get(task_id)
        if task and task.status == "open":
            task.status = "assigned"
            task.assigned_to = agent_id
            if agent_id in self.registry:
                self.registry[agent_id].status = "busy"
                
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
        
        task = self.tasks.get(task_id)
        if task and task.assigned_to == agent_id:
            task.status = status
            task.result = payload.get("result")
            
            if agent_id in self.registry:
                self.registry[agent_id].status = "available"
                
            # Dispara reflexão metacognitiva
            metabus.publish("metacognition.reflect_request", {
                "task_id": task_id,
                "agent_id": agent_id,
                "context": task.description,
                "result": task.result,
                "success": status == "completed"
            }, source_agent="blackboard")
            
            logger.info(f"Tarefa {task_id} finalizada por {agent_id} com status {status}")

# Instância global Singleton
blackboard = Blackboard()
