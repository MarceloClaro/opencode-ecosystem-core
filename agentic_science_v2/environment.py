# -*- coding: utf-8 -*-
"""
Environment Engineering — R101
===============================
Engenharia de ambiente em 4 dimensoes, inspirada no EurekAgent
(Xin et al., arXiv 2606.13662, 2026).

  1. PermissionsEngine: Isolamento, evaluator oculto, controle de acesso
  2. ArtifactEngine: Workspaces Git-based, historico de solucoes
  3. BudgetEngine: Limites de tempo e custo de API
  4. HITLEngine: Terminal TUI + web monitor para supervisao

SPEC-935-R101.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


# ============================================================
# PermissionsEngine
# ============================================================

class PermissionsEngine:
    """Gerencia permissoes e isolamento de execucao.

    Dimensoes:
      - Filesystem isolation: agentes nao veem evaluator oculto
      - GPU access: default-deny, aquisicao via helper API
      - Same-round isolation: sessoes paralelas nao compartilham codigo
    """

    def __init__(self, sandbox_root: Optional[str] = None):
        self.sandbox_root = sandbox_root or tempfile.mkdtemp(
            prefix="evosandbox_"
        )
        self.evaluator_path = os.path.join(self.sandbox_root, ".evaluator")
        self._active_sessions: Set[str] = set()
        self._gpu_locks: Dict[str, str] = {}  # gpu_id -> session_id

    def create_session(self, session_id: Optional[str] = None) -> str:
        """Cria uma sessao isolada."""
        sid = session_id or f"sess-{uuid.uuid4().hex[:8]}"
        session_dir = os.path.join(self.sandbox_root, "sessions", sid)

        # Workspace do agente (nao contem evaluator)
        agent_workspace = os.path.join(session_dir, "workspace")
        os.makedirs(agent_workspace, exist_ok=True)

        # Resultados (somente leitura para agente)
        results_dir = os.path.join(session_dir, "results")
        os.makedirs(results_dir, exist_ok=True)

        self._active_sessions.add(sid)

        return sid

    def close_session(self, session_id: str) -> None:
        """Fecha uma sessao."""
        self._active_sessions.discard(session_id)
        # Liberar GPUs associadas
        to_release = [
            gid for gid, sid in self._gpu_locks.items()
            if sid == session_id
        ]
        for gid in to_release:
            del self._gpu_locks[gid]

    def acquire_gpu(self, session_id: str, gpu_id: str = "gpu:0") -> bool:
        """Tenta adquirir GPU (default-deny)."""
        if gpu_id in self._gpu_locks:
            return False
        if session_id not in self._active_sessions:
            return False
        self._gpu_locks[gpu_id] = session_id
        return True

    def release_gpu(self, gpu_id: str) -> None:
        """Libera GPU."""
        self._gpu_locks.pop(gpu_id, None)

    def can_access_evaluator(self, session_id: str) -> bool:
        """Verifica se sessao pode acessar evaluator (sempre False)."""
        return False

    def get_workspace(self, session_id: str) -> str:
        """Retorna caminho do workspace do agente."""
        return os.path.join(
            self.sandbox_root, "sessions", session_id, "workspace",
        )

    def get_results_path(self, session_id: str) -> str:
        """Retorna caminho de resultados."""
        return os.path.join(
            self.sandbox_root, "sessions", session_id, "results",
        )

    def status(self) -> Dict[str, Any]:
        """Status do engine de permissoes."""
        return {
            "sandbox": self.sandbox_root,
            "active_sessions": len(self._active_sessions),
            "gpu_locks": dict(self._gpu_locks),
        }


# ============================================================
# ArtifactEngine
# ============================================================

@dataclass
class Artifact:
    """Artefato de uma execucao."""
    id: str = field(default_factory=lambda: f"art-{uuid.uuid4().hex[:8]}")
    session_id: str = ""
    name: str = ""
    artifact_type: str = "output"  # output, log, score, hypothesis
    content: str = ""
    score: Optional[float] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "name": self.name,
            "type": self.artifact_type,
            "score": self.score,
            "timestamp": self.timestamp,
        }


class ArtifactEngine:
    """Gerencia artefatos como memoria compartilhada.

    O filesystem + Git constituem a memoria persistente.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or tempfile.mkdtemp(
            prefix="evoartifacts_"
        )
        self.artifacts: Dict[str, Artifact] = {}
        self.ranked_solutions: List[str] = []  # artifact ids ordenados

    def store(
        self,
        artifact: Artifact,
    ) -> str:
        """Armazena um artefato."""
        self.artifacts[artifact.id] = artifact

        # Persistir no filesystem
        artifact_dir = os.path.join(
            self.base_dir, "artifacts", artifact.session_id,
        )
        os.makedirs(artifact_dir, exist_ok=True)
        path = os.path.join(
            artifact_dir, f"{artifact.id}_{artifact.name}.json",
        )
        with open(path, "w") as f:
            json.dump(artifact.to_dict(), f)

        # Atualizar ranking se tem score
        if artifact.score is not None:
            self.ranked_solutions.append(artifact.id)
            self.ranked_solutions.sort(
                key=lambda aid: self.artifacts[aid].score or 0,
                reverse=True,
            )

        return artifact.id

    def get(self, artifact_id: str) -> Optional[Artifact]:
        """Recupera artefato por ID."""
        return self.artifacts.get(artifact_id)

    def get_top_k(self, k: int = 5) -> List[Artifact]:
        """Recupera os melhores artefatos por score."""
        top_ids = self.ranked_solutions[:k]
        return [self.artifacts[aid] for aid in top_ids if aid in self.artifacts]

    def get_session_artifacts(
        self,
        session_id: str,
    ) -> List[Artifact]:
        """Recupera artefatos de uma sessao."""
        return [
            a for a in self.artifacts.values()
            if a.session_id == session_id
        ]

    def summary(self) -> Dict[str, Any]:
        """Sumario dos artefatos."""
        return {
            "total_artifacts": len(self.artifacts),
            "ranked_solutions": len(self.ranked_solutions),
            "top_score": (
                self.artifacts[self.ranked_solutions[0]].score
                if self.ranked_solutions else None
            ),
            "base_dir": self.base_dir,
        }


# ============================================================
# BudgetEngine
# ============================================================

@dataclass
class Budget:
    """Orcamento para uma sessao."""
    max_wall_clock_seconds: float = 3600.0
    max_api_cost_usd: float = 10.0
    api_cost_spent: float = 0.0
    start_time: float = field(default_factory=time.time)

    def remaining_time(self) -> float:
        """Tempo restante em segundos."""
        elapsed = time.time() - self.start_time
        return max(0.0, self.max_wall_clock_seconds - elapsed)

    def remaining_budget(self) -> float:
        """Orcamento restante em USD."""
        return max(0.0, self.max_api_cost_usd - self.api_cost_spent)

    def is_exhausted(self) -> bool:
        """Verifica se orcamento acabou."""
        return self.remaining_time() <= 0 or self.remaining_budget() <= 0

    def spend(self, cost: float) -> bool:
        """Registra gasto. Retorna False se estourou orcamento."""
        self.api_cost_spent += cost
        return not self.is_exhausted()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_time": self.max_wall_clock_seconds,
            "max_cost": self.max_api_cost_usd,
            "cost_spent": round(self.api_cost_spent, 4),
            "time_remaining": round(self.remaining_time(), 1),
            "budget_remaining": round(self.remaining_budget(), 4),
            "exhausted": self.is_exhausted(),
        }


class BudgetEngine:
    """Gerencia orcamentos multiplas sessoes."""

    def __init__(self):
        self.budgets: Dict[str, Budget] = {}

    def create_budget(
        self,
        session_id: str,
        max_time: float = 3600.0,
        max_cost: float = 10.0,
    ) -> Budget:
        """Cria orcamento para sessao."""
        budget = Budget(
            max_wall_clock_seconds=max_time,
            max_api_cost_usd=max_cost,
        )
        self.budgets[session_id] = budget
        return budget

    def spend(self, session_id: str, cost: float) -> bool:
        """Registra gasto. Retorna False se estourou."""
        budget = self.budgets.get(session_id)
        if not budget:
            return False
        return budget.spend(cost)

    def get_budget(self, session_id: str) -> Optional[Budget]:
        """Recupera orcamento da sessao."""
        return self.budgets.get(session_id)

    def is_exhausted(self, session_id: str) -> bool:
        """Verifica se sessao estourou orcamento."""
        budget = self.budgets.get(session_id)
        return budget.is_exhausted() if budget else True

    def all_exhausted(self) -> bool:
        """Verifica se todos os orcamentos acabaram."""
        if not self.budgets:
            return True
        return all(b.is_exhausted() for b in self.budgets.values())

    def summary(self) -> Dict[str, Any]:
        """Sumario dos orcamentos."""
        return {
            "active_budgets": sum(
                1 for b in self.budgets.values() if not b.is_exhausted()
            ),
            "exhausted_budgets": sum(
                1 for b in self.budgets.values() if b.is_exhausted()
            ),
            "total_budgets": len(self.budgets),
        }


# ============================================================
# HITLEngine
# ============================================================

class HITLEngine:
    """Interface humano-no-loop para supervisao e intervencao.

    Fornece monitoramento via terminal e web.
    """

    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.paused: bool = False
        self.interventions: List[Dict[str, Any]] = []

    def log_event(
        self,
        event_type: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Registra evento para monitoramento."""
        event = {
            "type": event_type,
            "message": message,
            "metadata": metadata or {},
            "timestamp": time.time(),
        }
        self.events.append(event)
        logger.info(f"[HITL] {event_type}: {message}")

    def request_approval(
        self,
        action: str,
        context: Dict[str, Any],
    ) -> bool:
        """Solicita aprovacao humana (simulada: sempre True)."""
        self.log_event(
            "approval_requested",
            f"Action: {action}",
            context,
        )
        # Em producao: bloquearia ate resposta humana
        # Aqui: auto-aprovar
        self.log_event("approval_granted", f"Approved: {action}", context)
        return True

    def pause(self) -> None:
        """Pausa execucao."""
        self.paused = True
        self.log_event("paused", "Execution paused by user")

    def resume(self) -> None:
        """Resume execucao."""
        self.paused = False
        self.log_event("resumed", "Execution resumed by user")

    def intervene(self, instruction: str) -> None:
        """Registra intervencao humana."""
        intervention = {
            "instruction": instruction,
            "timestamp": time.time(),
        }
        self.interventions.append(intervention)
        self.log_event("intervention", f"Human intervention: {instruction}")

    def recent_events(self, n: int = 10) -> List[Dict[str, Any]]:
        """Retorna os n eventos mais recentes."""
        return self.events[-n:]

    def summary(self) -> Dict[str, Any]:
        """Sumario do estado HITL."""
        return {
            "total_events": len(self.events),
            "total_interventions": len(self.interventions),
            "paused": self.paused,
            "last_event": self.events[-1] if self.events else None,
        }
