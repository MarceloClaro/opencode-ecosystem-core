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

    def search_memory(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Busca simples em memória episódica e semântica por substring normalizada."""
        q = (query or "").lower().strip()
        if not q:
            return []
        tokens = [t for t in q.split() if len(t) > 2]

        def _matches(hay: str) -> bool:
            hay_l = hay.lower()
            if q in hay_l:
                return True
            if tokens and all(t in hay_l for t in tokens):
                return True
            if tokens and sum(1 for t in tokens if t in hay_l) >= max(1, min(2, len(tokens))):
                return True
            return False

        results: List[Dict[str, Any]] = []

        for entry in reversed(self.episodic):
            hay = " ".join([
                str(entry.get("agent_id", "")),
                str(entry.get("context", "")),
                str(entry.get("reflection", "")),
            ]).lower()
            if _matches(hay):
                results.append({"kind": "episodic", **entry})
                if len(results) >= limit:
                    return results

        for topic, data in self.semantic.items():
            hay = " ".join([
                topic,
                " ".join(data.get("lessons", []) or []),
                json.dumps(data.get("metadata", {}), ensure_ascii=False),
            ]).lower()
            if _matches(hay):
                results.append({
                    "kind": "semantic",
                    "topic": topic,
                    "lessons": data.get("lessons", []),
                    "metadata": data.get("metadata", {}),
                })
                if len(results) >= limit:
                    return results
        return results

    def upsert_semantic_topic(self, topic: str,
                              lesson: Optional[str] = None,
                              metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Atualiza/inicializa um tópico semântico preservando histórico de lições."""
        entry = self.semantic.setdefault(topic, {
            "lessons": [],
            "metadata": {},
            "updated_at": None,
        })
        if lesson and lesson not in entry["lessons"]:
            entry["lessons"].append(lesson)
        if metadata:
            entry["metadata"].update(metadata)
        entry["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save()
        return entry

    def update_domain_confidence(self, domain_id: str, score: float) -> float:
        """Atualiza confiança EMA para um domínio jurídico específico."""
        key = f"legal:{domain_id}"
        return self.update_topic_confidence(key, score)

    def update_topic_confidence(self, topic_key: str, score: float) -> float:
        """Atualiza confiança EMA para qualquer tópico/subsistema."""
        key = topic_key
        current_conf = self.confidence_ledger.get(key, 0.5)
        updated = (current_conf * 0.7) + (max(0.0, min(1.0, score)) * 0.3)
        self.confidence_ledger[key] = updated
        self._save()
        return updated


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

    def publish_legal_event(self, event_name: str, domain_id: str,
                            payload: Dict[str, Any],
                            source_agent: str = "legal.system") -> int:
        """Publica um evento especializado do subsistema jurídico."""
        enriched = dict(payload or {})
        enriched.setdefault("domain_id", domain_id)
        return self.publish(f"legal.{event_name}", enriched, source_agent=source_agent)

    def publish_subsystem_event(self, subsystem: str, event_name: str,
                                payload: Dict[str, Any],
                                source_agent: str = "system") -> int:
        """Publica evento padronizado por subsistema."""
        enriched = dict(payload or {})
        enriched.setdefault("subsystem", subsystem)
        return self.publish(f"{subsystem}.{event_name}", enriched, source_agent=source_agent)

    def get_recent_events(self, limit: int = 20,
                          topic_prefix: Optional[str] = None,
                          source: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lê eventos recentes persistidos com filtros opcionais."""
        events: List[Dict[str, Any]] = []
        if not os.path.exists(EVENTS_FILE):
            return events
        try:
            with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if topic_prefix and not str(event.get("topic", "")).startswith(topic_prefix):
                        continue
                    if source and event.get("source") != source:
                        continue
                    events.append(event)
        except Exception as e:
            logger.error(f"Erro ao ler eventos recentes: {e}")
            return []
        return events[-limit:]

    def search_memory(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Atalho para busca metacognitiva na memória compartilhada."""
        return self.memory.search_memory(query, limit=limit)

# Instância global Singleton
metabus = MetaBus()
