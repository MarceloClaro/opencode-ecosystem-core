# -*- coding: utf-8 -*-
"""
Metacognitive Bus (MetaBus) & Shared Memory
===========================================
Implementa o barramento de eventos metacognitivos unificado (Global Workspace) e
a memória compartilhada (episódica/semântica) para todos os agentes do ecossistema.

Inspirado em:
- Global Workspace Theory (GWT) / Unified Mind Model (arXiv:2503.03459)
- Reflexion Framework (Shinn et al. 2023)
- Collaborative Memory for Multi-Agent Systems (arXiv:2505.18279)

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import os
import json
import time
import uuid
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone

logger = logging.getLogger("mci-metabus")
logger.setLevel(logging.INFO)

# Caminho para persistência da memória metacognitiva
MCI_DIR = os.path.dirname(os.path.abspath(__file__))
ECOSYSTEM_ROOT = os.path.dirname(MCI_DIR)
STATE_DIR = os.environ.get("MCI_STATE_DIR", os.path.join(ECOSYSTEM_ROOT, ".mci_state"))
os.makedirs(STATE_DIR, exist_ok=True)

MEMORY_FILE = os.path.join(STATE_DIR, "shared_memory.json")
EVENTS_FILE = os.path.join(STATE_DIR, "metabus_events.jsonl")

class MetacognitiveMemory:
    """Memória episódica e semântica compartilhada entre agentes."""
    
    def __init__(self):
        self.episodic: List[Dict[str, Any]] = []  # Traces e reflexões de execução
        self.semantic: Dict[str, Any] = {}        # Conhecimento consolidado, lições aprendidas
        self.confidence_ledger: Dict[str, float] = {} # Score global de confiança por tópico/agente
        self._load()
        
    def _load(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.episodic = data.get("episodic", [])
                    self.semantic = data.get("semantic", {})
                    self.confidence_ledger = data.get("confidence_ledger", {})
            except Exception as e:
                logger.error(f"Erro ao carregar memória: {e}")
                
    def _save(self):
        try:
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    "episodic": self.episodic[-1000:], # Manter últimos 1000 eventos
                    "semantic": self.semantic,
                    "confidence_ledger": self.confidence_ledger,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar memória: {e}")

    def add_reflection(self, agent_id: str, task_context: str, reflection: str, score: float):
        """Adiciona uma reflexão pós-execução (padrão Reflexion)."""
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "reflection",
            "agent_id": agent_id,
            "context": task_context,
            "reflection": reflection,
            "score": score
        }
        self.episodic.append(entry)
        
        # Atualiza confidence ledger via EMA (Exponential Moving Average)
        current_conf = self.confidence_ledger.get(agent_id, 0.5)
        self.confidence_ledger[agent_id] = (current_conf * 0.7) + (score * 0.3)
        
        self._save()
        return entry["id"]

    def extract_lessons(self, topic: str) -> List[str]:
        """Extrai lições semânticas consolidadas sobre um tópico."""
        return self.semantic.get(topic, {}).get("lessons", [])
        
    def get_recent_context(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Recupera contexto recente do Global Workspace."""
        return self.episodic[-limit:]


class MetaBus:
    """Barramento de eventos unificado (Global Workspace Broadcast)."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetaBus, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        if self._initialized:
            return
        self.subscribers: Dict[str, List[Callable]] = {}
        self.memory = MetacognitiveMemory()
        self._initialized = True
        
    def subscribe(self, topic: str, callback: Callable):
        """Inscreve um handler em um tópico metacognitivo."""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        logger.info(f"Subscribed to topic: {topic}")
        
    def publish(self, topic: str, payload: Dict[str, Any], source_agent: str = "system"):
        """Publica um evento no Global Workspace e o persiste."""
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "topic": topic,
            "source": source_agent,
            "payload": payload
        }
        
        # Persiste no log append-only
        try:
            with open(EVENTS_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"Erro ao persistir evento: {e}")
            
        # Roteamento
        handlers = self.subscribers.get(topic, [])
        handlers.extend(self.subscribers.get("*", [])) # Wildcard
        
        dispatched = 0
        for handler in handlers:
            try:
                handler(event)
                dispatched += 1
            except Exception as e:
                logger.error(f"Erro no handler do evento {topic}: {e}")
                
        return dispatched

# Instância global Singleton
metabus = MetaBus()
