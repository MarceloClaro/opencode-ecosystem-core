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
import uuid
import logging
import math
from numbers import Real
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone

from mci.metabus_store import MetaBusPersistenceError, MetaBusSQLiteStore

logger = logging.getLogger("mci-metabus")
logger.setLevel(logging.INFO)


class _LogicalSubscription:
    """Callback substituível identificado pelo papel lógico do assinante."""

    __slots__ = ("identity", "callback")

    def __init__(self, identity: str, callback: Callable):
        self.identity = identity
        self.callback = callback

    def __call__(self, event: Dict[str, Any]):
        return self.callback(event)


# Caminho para persistência da memória metacognitiva
MCI_DIR = os.path.dirname(os.path.abspath(__file__))
ECOSYSTEM_ROOT = os.path.dirname(MCI_DIR)
STATE_DIR = os.environ.get("MCI_STATE_DIR", os.path.join(ECOSYSTEM_ROOT, ".mci_state"))
os.makedirs(STATE_DIR, exist_ok=True)

MEMORY_FILE = os.path.join(STATE_DIR, "shared_memory.json")
EVENTS_FILE = os.path.join(STATE_DIR, "metabus_events.jsonl")
DATABASE_FILE = os.environ.get("MCI_DATABASE_FILE", os.path.join(STATE_DIR, "metabus.sqlite3"))
_DEFAULT_MEMORY_FILE = MEMORY_FILE
_DEFAULT_EVENTS_FILE = EVENTS_FILE
_DEFAULT_DATABASE_FILE = DATABASE_FILE
MAX_MEMORY_LIMIT = 1000
MAX_AGENT_ID_LENGTH = 256
MAX_CONTEXT_LENGTH = 2000
MAX_REFLECTION_LENGTH = 16384


def _active_database_file() -> str:
    """Resolve o banco ativo, preservando isolamento de testes legados."""
    explicit = os.environ.get("MCI_DATABASE_FILE")
    if explicit:
        return os.path.abspath(os.path.expanduser(explicit))
    if DATABASE_FILE != _DEFAULT_DATABASE_FILE:
        return os.path.abspath(os.path.expanduser(DATABASE_FILE))
    changed = [
        path for path, original in (
            (MEMORY_FILE, _DEFAULT_MEMORY_FILE),
            (EVENTS_FILE, _DEFAULT_EVENTS_FILE),
        ) if path != original
    ]
    if changed:
        # Compatibility for tests and older callers that override only a
        # legacy filename: their SQLite file stays alongside the override.
        return os.path.join(os.path.dirname(os.path.abspath(changed[0])), "metabus.sqlite3")
    return DATABASE_FILE


def _validate_memory_limit(limit: int) -> int:
    """Valida um limite inteiro explícito, sem aceitar bool como inteiro."""
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise ValueError("limit deve ser um inteiro entre 0 e 1000.")
    if not 0 <= limit <= MAX_MEMORY_LIMIT:
        raise ValueError("limit deve estar entre 0 e 1000.")
    return limit


def _validate_reflection_text(value: Any, field: str, max_length: int) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field} deve ser texto.")
    if not value.strip():
        raise ValueError(f"{field} não pode ser vazio.")
    if len(value) > max_length:
        raise ValueError(f"{field} excede {max_length} caracteres.")
    return value


def memory_entry_text(entry: Dict[str, Any]) -> str:
    """Projeção textual comum às buscas lexical e hierárquica (R886)."""
    observation = entry.get("observation", {})
    try:
        body = json.dumps(observation, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError, RecursionError):
        body = ""
    return " ".join(str(entry.get(key, "")) for key in ("agent_id", "context", "reflection")) + " " + body


class MetacognitiveMemory:
    """Memória episódica e semântica compartilhada entre agentes."""

    def __init__(self):
        self.episodic: List[Dict[str, Any]] = []  # Traces e reflexões de execução
        self.semantic: Dict[str, Any] = {}        # Conhecimento consolidado, lições aprendidas
        self.confidence_ledger: Dict[str, float] = {} # Score global de confiança por tópico/agente
        self._store: Optional[MetaBusSQLiteStore] = None
        self._store_identity = None
        self._load()

    def _ensure_store(self) -> MetaBusSQLiteStore:
        database_file = _active_database_file()
        identity = (database_file, os.path.abspath(MEMORY_FILE), os.path.abspath(EVENTS_FILE))
        if self._store is None or self._store_identity != identity:
            self._store = MetaBusSQLiteStore(
                database_file,
                legacy_memory_path=MEMORY_FILE,
                legacy_events_path=EVENTS_FILE,
            )
            self._store_identity = identity
        return self._store

    def _refresh_from_store(self) -> None:
        episodes, semantic, confidence = self._ensure_store().load_memory()
        self.episodic = episodes
        self.semantic = semantic
        self.confidence_ledger = confidence

    def _load(self):
        # A inicialização do store faz a importação legada idempotente e
        # fail-closed. Arquivo de memória presente, porém corrompido, não pode
        # ser mascarado por um estado vazio.
        self._refresh_from_store()

    def _save(self, *, strict: bool = False) -> bool:
        try:
            episodic = self.episodic[-MAX_MEMORY_LIMIT:]
            self._ensure_store().save_memory_snapshot(
                episodic, self.semantic, self.confidence_ledger
            )
            self.episodic = episodic
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar memória: {e}")
            if strict:
                raise RuntimeError("Falha ao persistir memória metacognitiva.") from e
            return False

    def add_reflection(self, agent_id: str, task_context: str, reflection: str, score: float):
        """Adiciona uma reflexão pós-execução (padrão Reflexion)."""
        agent_id = _validate_reflection_text(agent_id, "agent_id", MAX_AGENT_ID_LENGTH)
        task_context = _validate_reflection_text(
            task_context, "task_context", MAX_CONTEXT_LENGTH
        )
        reflection = _validate_reflection_text(
            reflection, "reflection", MAX_REFLECTION_LENGTH
        )
        if isinstance(score, bool) or not isinstance(score, Real):
            raise TypeError("score deve ser numérico e não booleano.")
        score = float(score)
        if not math.isfinite(score) or not 0.0 <= score <= 1.0:
            raise ValueError("score deve ser finito e estar entre 0 e 1.")

        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "reflection",
            "agent_id": agent_id,
            "context": task_context,
            "reflection": reflection,
            "score": score
        }
        # Episode e EMA são calculados no writer SQLite sob BEGIN IMMEDIATE;
        # nenhuma mutação local ocorre antes do commit.
        updated_confidence = self._ensure_store().add_reflection(entry, agent_id, score)
        self.episodic.append(entry)
        if len(self.episodic) > MAX_MEMORY_LIMIT:
            del self.episodic[:-MAX_MEMORY_LIMIT]
        self.confidence_ledger[agent_id] = updated_confidence
        return entry["id"]

    def record_observation(self, agent_id: str, task_context: str,
                           observation: Dict[str, Any]) -> str:
        """R666: persiste um resultado delimitado sem aumentar confiança por autoavaliação."""
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("agent_id deve ser texto útil.")
        if not isinstance(task_context, str) or len(task_context) > 2000:
            raise ValueError("Contexto deve ser texto de até 2000 caracteres.")
        if not isinstance(observation, dict):
            raise ValueError("Observação deve ser objeto JSON.")
        payload = json.dumps(observation, ensure_ascii=False, allow_nan=False)
        if len(payload.encode("utf-8")) > 131072:
            raise ValueError("Observação excede 128 KiB.")
        entry = {"id": str(uuid.uuid4()), "timestamp": datetime.now(timezone.utc).isoformat(),
                 "type": "observation", "agent_id": agent_id, "context": task_context,
                 "observation": json.loads(payload)}
        self._ensure_store().add_observation(entry)
        self.episodic.append(entry)
        if len(self.episodic) > MAX_MEMORY_LIMIT:
            del self.episodic[:-MAX_MEMORY_LIMIT]
        return entry["id"]

    def extract_lessons(self, topic: str) -> List[str]:
        """Extrai lições semânticas consolidadas sobre um tópico."""
        return self.semantic.get(topic, {}).get("lessons", [])

    def get_recent_context(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Recupera contexto recente do Global Workspace."""
        limit = _validate_memory_limit(limit)
        if limit == 0:
            return []
        return self.episodic[-limit:]

    def search_memory(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Busca simples em memória episódica e semântica por substring normalizada."""
        limit = _validate_memory_limit(limit)
        if limit == 0:
            return []
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
            if not isinstance(entry, dict):
                continue
            hay = memory_entry_text(entry).lower()
            if _matches(hay):
                results.append({"kind": "episodic", **entry})
                if len(results) >= limit:
                    return results

        for topic, data in self.semantic.items():
            if not isinstance(data, dict):
                continue
            hay = " ".join([
                topic,
                json.dumps(data.get("lessons", []), ensure_ascii=False),
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
                              metadata: Optional[Dict[str, Any]] = None,
                              *, strict: bool = False) -> Dict[str, Any]:
        """Atualiza/inicializa um tópico semântico preservando histórico de lições."""
        entry = self._ensure_store().upsert_semantic_topic(
            topic, lesson, metadata, datetime.now(timezone.utc).isoformat()
        )
        self.semantic[topic] = entry
        return entry

    def update_domain_confidence(self, domain_id: str, score: float) -> float:
        """Atualiza confiança EMA para um domínio jurídico específico."""
        key = f"legal:{domain_id}"
        return self.update_topic_confidence(key, score)

    def update_topic_confidence(self, topic_key: str, score: float) -> float:
        """Atualiza confiança EMA para qualquer tópico/subsistema."""
        updated = self._ensure_store().update_confidence(topic_key, score)
        self.confidence_ledger[topic_key] = updated
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
        
    def subscribe(self, topic: str, callback: Callable,
                  logical_identity: Optional[str] = None):
        """Inscreve um handler, opcionalmente idempotente por identidade lógica.

        Chamadas legadas sem ``logical_identity`` preservam a semântica de
        anexação. Quando a identidade é fornecida, uma nova instância lógica
        substitui o callback anterior no mesmo tópico, sem efeito duplicado.
        """
        if not callable(callback):
            raise TypeError("callback deve ser chamável")
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        handlers = self.subscribers[topic]
        if logical_identity is None:
            handlers.append(callback)
        else:
            identity = str(logical_identity).strip()
            if not identity:
                raise ValueError("logical_identity não pode ser vazia")
            replacement = _LogicalSubscription(identity, callback)
            for index, registered in enumerate(handlers):
                if (
                    isinstance(registered, _LogicalSubscription)
                    and registered.identity == identity
                ):
                    handlers[index] = replacement
                    break
            else:
                handlers.append(replacement)
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
        
        # O evento só pode ser observado localmente depois de um commit
        # durável. Falha de persistência bloqueia o despacho.
        self.memory._ensure_store().append_event(event)

        # Roteamento
        # Copiar impede que o wildcard seja anexado permanentemente à lista do
        # tópico a cada publicação.
        handlers = list(self.subscribers.get(topic, []))
        if topic != "*":
            handlers.extend(list(self.subscribers.get("*", []))) # Wildcard
        
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
        limit = _validate_memory_limit(limit)
        if limit == 0:
            return []
        return self.memory._ensure_store().recent_events(limit, topic_prefix, source)

    def search_memory(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Atalho para busca metacognitiva na memória compartilhada."""
        return self.memory.search_memory(query, limit=limit)

# Instância global Singleton
metabus = MetaBus()
