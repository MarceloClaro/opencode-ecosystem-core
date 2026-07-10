#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrustEngine v1.0 — SPEC-038: Trust Scoring + Behavioral Gate + Natural Forgetting
==================================================================================
Implementa padroes extraidos de wazionapps/nexo (metacognitive guard, trust scoring,
natural forgetting) adaptados para o OpenCode Ecosystem.

Arquitetura:
  1. TrustScorer        — pesos adaptativos que aprendem com feedback real
  2. BehavioralGate     — pre-execution guard: so executa se trust > threshold
  3. NaturalForgetting   — Atkinson-Shiffrin: sensorial -> curto prazo -> longo prazo
  4. OutcomeTracker      — registro de outcomes para aprendizado continuo

Uso:
    engine = TrustEngine()
    if engine.gate("scan_dimensao_raciocinio"):
        result = execute_scan()
        engine.record_outcome("scan_dimensao_raciocinio", success=True, delta=0.15)

Autor: OpenCode Ecosystem (2026) — R23: Behavioral Autonomy
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

BRAZIL_TZ = timezone.utc


# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ActionTrust:
    """Score de confianca para uma acao especifica."""
    action_id: str
    trust_score: float            # 0-1 (combina history + recent + penalty)
    total_executions: int = 0
    successful: int = 0
    recent_outcomes: list[bool] = field(default_factory=list)  # ultimos 10
    penalty: float = 0.0          # penalidade acumulada por falhas
    last_updated: str = ""


@dataclass
class MemorySlot:
    """Slot de memoria no modelo Atkinson-Shiffrin."""
    content: str
    importance: float             # 0-1 (calculado na entrada)
    decay_rate: float             # taxa de esquecimento
    created_at: str
    last_accessed: str
    access_count: int = 0
    memory_type: str = "sensory"  # sensory -> short_term -> long_term


@dataclass
class GateDecision:
    """Decisao do behavioral gate."""
    action_id: str
    allowed: bool
    trust_score: float
    threshold: float
    reason: str
    risk_level: str               # "safe" | "moderate" | "risky" | "blocked"


@dataclass
class DriftCheck:
    """Resultado de uma verificacao de goal drift."""
    session_id: str
    similarity: float              # sobreposicao lexical acao-vs-objetivo (0-1)
    drifted: bool
    window: list[float] = field(default_factory=list)
    reason: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# 1. TRUST SCORER (Adaptive Learned Weights)
# ═══════════════════════════════════════════════════════════════════════════

class TrustScorer:
    """Calcula e atualiza scores de confianca para acoes.

    Inspirado no NEXO Brain: pesos adaptativos que aprendem com feedback
    real via weighted moving average. Shadow mode de 5 execucoes antes de ativar.
    Rollback automatico se taxa de correcao dobrar.
    """

    SHADOW_MODE_THRESHOLD = 5
    ROLLBACK_RATIO = 2.0

    def __init__(self):
        self._actions: dict[str, ActionTrust] = {}
        self._baseline_success_rate: float = 0.7

    def get_trust(self, action_id: str) -> ActionTrust:
        """Retorna ou cria score de confianca para uma acao."""
        if action_id not in self._actions:
            self._actions[action_id] = ActionTrust(
                action_id=action_id,
                trust_score=0.5,        # default: neutro
                last_updated=datetime.now(BRAZIL_TZ).isoformat(),
            )
        return self._actions[action_id]

    def record_outcome(self, action_id: str, success: bool, delta: float = 0.0) -> ActionTrust:
        """Registra outcome de uma acao e atualiza trust score.

        Args:
            action_id: identificador da acao
            success: True se a acao foi bem-sucedida
            delta: melhoria observada (0-1)

        Returns:
            ActionTrust atualizado
        """
        trust = self.get_trust(action_id)
        trust.total_executions += 1
        if success:
            trust.successful += 1

        # Manter historico recente (ultimos 10)
        trust.recent_outcomes.append(success)
        if len(trust.recent_outcomes) > 10:
            trust.recent_outcomes.pop(0)

        # Calcular taxa de sucesso recente (peso maior)
        if trust.recent_outcomes:
            recent_rate = sum(trust.recent_outcomes) / len(trust.recent_outcomes)
        else:
            recent_rate = 0.5

        # Calcular taxa historica
        hist_rate = trust.successful / max(1, trust.total_executions)

        # Weighted blend: 70% recente, 30% historico
        raw_score = 0.7 * recent_rate + 0.3 * hist_rate

        # Penalidade por falhas consecutivas
        consecutive_failures = 0
        for outcome in reversed(trust.recent_outcomes):
            if not outcome:
                consecutive_failures += 1
            else:
                break
        trust.penalty = min(0.5, consecutive_failures * 0.1)

        # Trust score final
        trust.trust_score = max(0.0, min(1.0, raw_score - trust.penalty))

        # Shadow mode: nas primeiras execucoes, manter score conservador
        if trust.total_executions < self.SHADOW_MODE_THRESHOLD:
            trust.trust_score = min(trust.trust_score, 0.5)

        # Rollback detection: se success rate cair abaixo de 50% da baseline
        if trust.total_executions >= self.SHADOW_MODE_THRESHOLD:
            if recent_rate < self._baseline_success_rate / self.ROLLBACK_RATIO:
                trust.trust_score = max(0.1, trust.trust_score - 0.2)

        trust.last_updated = datetime.now(BRAZIL_TZ).isoformat()
        return trust

    def update_baseline(self, new_baseline: float) -> None:
        """Atualiza baseline de taxa de sucesso."""
        self._baseline_success_rate = max(0.3, min(0.95, new_baseline))

    def all_trust_scores(self) -> dict[str, float]:
        """Todos os scores de confianca atuais."""
        return {aid: at.trust_score for aid, at in self._actions.items()}

    def low_trust_actions(self, threshold: float = 0.3) -> list[str]:
        """Acoes com baixa confianca."""
        return [aid for aid, at in self._actions.items() if at.trust_score < threshold]

    def top_trusted(self, n: int = 5) -> list[tuple[str, float]]:
        """Acoes mais confiaveis."""
        ranked = sorted(self._actions.items(), key=lambda x: -x[1].trust_score)
        return [(aid, at.trust_score) for aid, at in ranked[:n]]


# ═══════════════════════════════════════════════════════════════════════════
# 2. BEHAVIORAL GATE (Pre-Execution Guard)
# ═══════════════════════════════════════════════════════════════════════════

class BehavioralGate:
    """Gate pre-execução: autoriza ou bloqueia ações baseado em confiança.

    Inspirado no NEXO Brain metacognitive guard:
    - So executa se trust_score > threshold
    - Classifica risco: safe, moderate, risky, blocked
    - Fornece justificativa auditável para cada decisão
    """

    DEFAULT_THRESHOLD = 0.25
    SAFE_THRESHOLD = 0.70
    MODERATE_THRESHOLD = 0.40

    def __init__(self, scorer: TrustScorer | None = None):
        self.scorer = scorer or TrustScorer()
        self._decisions: list[GateDecision] = []
        self.threshold = self.DEFAULT_THRESHOLD

    def gate(self, action_id: str,
             required_trust: float | None = None) -> GateDecision:
        """Decide se uma acao deve ser executada.

        Args:
            action_id: identificador da acao
            required_trust: threshold especifico (None = usa default)

        Returns:
            GateDecision com allowed, reason, risk_level
        """
        threshold = required_trust or self.threshold
        trust = self.scorer.get_trust(action_id)
        score = trust.trust_score

        # Classificar nivel de risco
        if score >= self.SAFE_THRESHOLD:
            risk = "safe"
            allowed = True
            reason = f"Trust {score:.0%} >= safe threshold {self.SAFE_THRESHOLD:.0%}"
        elif score >= self.MODERATE_THRESHOLD:
            risk = "moderate"
            allowed = score >= threshold
            reason = (f"Trust {score:.0%} moderate. "
                      f"{'Allowed' if allowed else 'Blocked'} (threshold={threshold:.0%})")
        elif score >= threshold:
            risk = "risky"
            allowed = True
            reason = f"Trust {score:.0%} low but above threshold {threshold:.0%} — proceed with caution"
        else:
            risk = "blocked"
            allowed = False
            reason = f"Trust {score:.0%} < threshold {threshold:.0%} — blocked"

        # Penalidade adicional: shadow mode actions
        if trust.total_executions < TrustScorer.SHADOW_MODE_THRESHOLD:
            reason += " [SHADOW MODE: limited trust]"

        decision = GateDecision(
            action_id=action_id,
            allowed=allowed,
            trust_score=score,
            threshold=threshold,
            reason=reason,
            risk_level=risk,
        )
        self._decisions.append(decision)
        return decision

    def set_threshold(self, new_threshold: float) -> None:
        """Ajusta threshold global."""
        self.threshold = max(0.1, min(0.9, new_threshold))

    @property
    def recent_decisions(self) -> list[GateDecision]:
        return self._decisions[-20:]

    @property
    def block_rate(self) -> float:
        """Taxa de bloqueios nas ultimas decisoes."""
        recent = self._decisions[-20:]
        if not recent:
            return 0.0
        return sum(1 for d in recent if not d.allowed) / len(recent)

    @property
    def gate_health(self) -> dict[str, Any]:
        """Saude do gate."""
        return {
            "threshold": self.threshold,
            "total_decisions": len(self._decisions),
            "block_rate": round(self.block_rate, 2),
            "safe_actions": len([d for d in self._decisions[-20:] if d.risk_level == "safe"]),
            "blocked_actions": len([d for d in self._decisions[-20:] if d.risk_level == "blocked"]),
        }


# ═══════════════════════════════════════════════════════════════════════════
# 3. NATURAL FORGETTING (Atkinson-Shiffrin Memory Model)
# ═══════════════════════════════════════════════════════════════════════════

class NaturalForgetting:
    """Modelo de memoria com esquecimento natural.

    Inspirado no NEXO Brain (Atkinson-Shiffrin):
    - Sensory memory: TTL muito curto (30s), alta capacidade
    - Short-term: TTL medio (5min), capacidade 7+-2 itens
    - Long-term: TTL longo (24h+), promovido por acesso repetido

    Promocao: sensory -> short_term (apos 3 acessos)
              short_term -> long_term (apos 5 acessos + alta importance)
    """

    SENSORY_TTL = 30       # segundos
    SHORT_TERM_TTL = 300   # 5 minutos
    LONG_TERM_TTL = 86400  # 24 horas

    PROMOTE_TO_SHORT = 3   # acessos para promover de sensory
    PROMOTE_TO_LONG = 5    # acessos para promover de short

    def __init__(self):
        self._slots: list[MemorySlot] = []
        self._decay_clock: float = time.time()

    def store(self, content: str, importance: float = 0.5) -> MemorySlot:
        """Armazena novo item na memoria sensorial.

        Args:
            content: conteudo a armazenar
            importance: 0-1 (calculado na entrada)
        """
        now = datetime.now(BRAZIL_TZ).isoformat()
        slot = MemorySlot(
            content=content,
            importance=importance,
            decay_rate=0.01 + (1.0 - importance) * 0.05,  # itens importantes decaem devagar
            created_at=now,
            last_accessed=now,
            memory_type="sensory",
        )
        self._slots.append(slot)

        # Limitar capacidade sensorial (50 itens)
        if len([s for s in self._slots if s.memory_type == "sensory"]) > 50:
            self._prune_sensory()

        return slot

    def recall(self, content_hint: str) -> MemorySlot | None:
        """Tenta recuperar um item da memoria.

        Acessar um item aumenta seu contador e pode promovê-lo.
        """
        now = datetime.now(BRAZIL_TZ)
        self._prune_expired()

        for slot in reversed(self._slots):
            # Correspondencia parcial (substring)
            if content_hint.lower() in slot.content.lower():
                slot.access_count += 1
                slot.last_accessed = now.isoformat()

                # Promover: sensory -> short_term
                if slot.memory_type == "sensory" and slot.access_count >= self.PROMOTE_TO_SHORT:
                    slot.memory_type = "short_term"
                    slot.decay_rate *= 0.5  # decai mais devagar

                # Promover: short_term -> long_term
                if (slot.memory_type == "short_term"
                        and slot.access_count >= self.PROMOTE_TO_LONG
                        and slot.importance >= 0.6):
                    slot.memory_type = "long_term"
                    slot.decay_rate *= 0.2  # decai muito devagar

                return slot

        return None

    def _prune_expired(self) -> None:
        """Remove itens cujo TTL expirou."""
        now = datetime.now(BRAZIL_TZ)
        surviving: list[MemorySlot] = []

        for slot in self._slots:
            elapsed = (now - datetime.fromisoformat(slot.last_accessed)).total_seconds()
            ttl = {
                "sensory": self.SENSORY_TTL,
                "short_term": self.SHORT_TERM_TTL,
                "long_term": self.LONG_TERM_TTL,
            }.get(slot.memory_type, self.SENSORY_TTL)

            # Decaimento: items menos importantes esquecem mais rapido
            effective_ttl = ttl / (1.0 + slot.importance * 2)

            if elapsed < effective_ttl:
                surviving.append(slot)

        self._slots = surviving

    def _prune_sensory(self) -> None:
        """Remove itens sensoriais mais antigos (FIFO)."""
        sensory = [s for s in self._slots if s.memory_type == "sensory"]
        if len(sensory) > 40:
            to_remove = sorted(sensory, key=lambda s: s.last_accessed)[:10]
            for slot in to_remove:
                if slot in self._slots:
                    self._slots.remove(slot)

    @property
    def memory_stats(self) -> dict[str, int]:
        """Estatisticas de memoria por tipo."""
        stats = defaultdict(int)
        for slot in self._slots:
            stats[slot.memory_type] += 1
        stats["total"] = len(self._slots)
        return dict(stats)


# ═══════════════════════════════════════════════════════════════════════════
# 4. OUTCOME TRACKER
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TrackedOutcome:
    """Outcome rastreado para aprendizado continuo."""
    action_id: str
    success: bool
    delta: float
    timestamp: str
    trust_before: float
    trust_after: float


class OutcomeTracker:
    """Registra outcomes e alimenta o aprendizado do TrustScorer."""

    def __init__(self, scorer: TrustScorer | None = None):
        self.scorer = scorer or TrustScorer()
        self._outcomes: list[TrackedOutcome] = []

    def record(self, action_id: str, success: bool, delta: float = 0.0) -> TrackedOutcome:
        """Registra outcome e atualiza trust score."""
        trust_before = self.scorer.get_trust(action_id).trust_score
        self.scorer.record_outcome(action_id, success, delta)
        trust_after = self.scorer.get_trust(action_id).trust_score

        outcome = TrackedOutcome(
            action_id=action_id,
            success=success,
            delta=delta,
            timestamp=datetime.now(BRAZIL_TZ).isoformat(),
            trust_before=trust_before,
            trust_after=trust_after,
        )
        self._outcomes.append(outcome)

        # Atualizar baseline se necessario
        if len(self._outcomes) >= 20:
            recent_rate = sum(1 for o in self._outcomes[-20:] if o.success) / 20
            self.scorer.update_baseline(recent_rate)

        return outcome

    @property
    def recent_success_rate(self) -> float:
        recent = self._outcomes[-20:]
        if not recent:
            return 0.5
        return sum(1 for o in recent if o.success) / len(recent)

    @property
    def total_improvement(self) -> float:
        """Delta acumulado total."""
        return sum(o.delta for o in self._outcomes if o.success)


# ═══════════════════════════════════════════════════════════════════════════
# 5. GOAL DRIFT DETECTOR (R112)
# ═══════════════════════════════════════════════════════════════════════════

class GoalDriftDetector:
    """Detecta desvio de objetivo (goal drift): compara o contexto das
    acoes recentes de uma sessao contra o objetivo originalmente
    declarado, usando sobreposicao lexical (Jaccard) sobre uma janela
    deslizante — heuristico e determinístico, no mesmo espirito de outros
    comparadores de similaridade ja usados no ecossistema (ex.:
    ``agentic_science_v2.revision_agent.SectionMapper``, que mapeia
    claims para secoes por overlap de palavras).

    Nao e um classificador semantico/LLM — deteccao de deriva textual
    grosseira, mas real e testavel, distinta de nao ter deteccao nenhuma.
    """

    def __init__(self, window: int = 5, drift_threshold: float = 0.15):
        self.window = window
        self.drift_threshold = drift_threshold
        self._goals: dict[str, str] = {}
        self._history: dict[str, list[float]] = defaultdict(list)

    def set_goal(self, session_id: str, goal_text: str) -> None:
        """Declara (ou redeclara) o objetivo de uma sessao, reiniciando
        sua janela de historico de similaridade."""
        self._goals[session_id] = goal_text
        self._history[session_id] = []

    @staticmethod
    def _similarity(a: str, b: str) -> float:
        """Sobreposicao lexical de Jaccard entre dois textos."""
        wa = set(a.lower().split())
        wb = set(b.lower().split())
        if not wa or not wb:
            return 0.0
        return len(wa & wb) / len(wa | wb)

    def check(self, session_id: str, action_context: str) -> DriftCheck:
        """Verifica se a acao atual ainda esta alinhada ao objetivo
        declarado. So classifica ``drifted=True`` depois que a janela
        completa (``window`` acoes) mostrar similaridade media abaixo do
        limiar — uma unica acao fora do tema nao basta."""
        goal = self._goals.get(session_id, "")
        sim = self._similarity(goal, action_context) if goal else 1.0

        hist = self._history[session_id]
        hist.append(sim)
        if len(hist) > self.window:
            hist.pop(0)

        drifted = False
        if not goal:
            reason = "sem objetivo declarado para esta sessao — nada a comparar"
        elif len(hist) < self.window:
            reason = f"janela incompleta ({len(hist)}/{self.window}) — aguardando mais acoes"
        else:
            avg = sum(hist) / len(hist)
            if avg < self.drift_threshold:
                drifted = True
                reason = (
                    f"similaridade media com o objetivo caiu para {avg:.2f} "
                    f"(< limiar {self.drift_threshold}) nas ultimas {self.window} acoes"
                )
            else:
                reason = f"similaridade media {avg:.2f} dentro do limiar ({self.drift_threshold})"

        return DriftCheck(
            session_id=session_id, similarity=round(sim, 4),
            drifted=drifted, window=list(hist), reason=reason,
        )

    def status(self, session_id: str) -> dict[str, Any]:
        return {
            "goal": self._goals.get(session_id, ""),
            "history": list(self._history.get(session_id, [])),
        }


# ═══════════════════════════════════════════════════════════════════════════
# TRUST ENGINE (Orquestrador)
# ═══════════════════════════════════════════════════════════════════════════

class TrustEngine:
    """Orquestrador de autonomia comportamental.

    Integra TrustScorer + BehavioralGate + NaturalForgetting + OutcomeTracker.

    Uso:
        engine = TrustEngine()
        if engine.gate("scan_raciocinio").allowed:
            result = execute()
            engine.learn("scan_raciocinio", success=True, delta=0.15)
    """

    def __init__(self):
        self.scorer = TrustScorer()
        self.gate = BehavioralGate(self.scorer)
        self.memory = NaturalForgetting()
        self.tracker = OutcomeTracker(self.scorer)
        self.goal_drift = GoalDriftDetector()

    def execute(self, action_id: str, required_trust: float | None = None) -> GateDecision:
        """Verifica se uma acao pode ser executada (behavioral gate).

        Returns:
            GateDecision — verificar .allowed antes de executar
        """
        return self.gate.gate(action_id, required_trust)

    def learn(self, action_id: str, success: bool, delta: float = 0.0,
              context: str = "") -> TrackedOutcome:
        """Aprende com o outcome de uma acao.

        Atualiza trust score e registra na memoria.
        """
        outcome = self.tracker.record(action_id, success, delta)

        # Armazenar na memoria para referencia futura
        if context:
            importance = 0.5 + (delta * 0.5)  # grandes melhorias = mais importantes
            self.memory.store(
                f"{action_id}: {'SUCCESS' if success else 'FAILURE'} — {context}",
                importance=min(1.0, importance),
            )

        return outcome

    def recall(self, query: str) -> list[str]:
        """Recupera memorias relevantes."""
        result = self.memory.recall(query)
        return [result.content] if result else []

    def set_goal(self, session_id: str, goal_text: str) -> None:
        """Declara o objetivo de uma sessao para deteccao de goal drift (R112)."""
        self.goal_drift.set_goal(session_id, goal_text)

    def check_drift(self, session_id: str, action_context: str) -> DriftCheck:
        """Verifica desvio de objetivo (goal drift) para a acao atual.

        Quando a deriva e confirmada (janela completa, similaridade media
        abaixo do limiar), o outcome e registrado como falha para a acao
        ``goal_drift:{session_id}`` — a mesma penalidade de confianca
        aplicada a qualquer outra falha rastreada, sem mecanismo separado.
        """
        result = self.goal_drift.check(session_id, action_context)
        if result.drifted:
            self.tracker.record(f"goal_drift:{session_id}", success=False, delta=0.0)
        return result

    @property
    def status(self) -> dict[str, Any]:
        return {
            "gate_health": self.gate.gate_health,
            "memory_stats": self.memory.memory_stats,
            "recent_success_rate": round(self.tracker.recent_success_rate, 2),
            "total_improvement": round(self.tracker.total_improvement, 4),
            "trusted_actions": self.scorer.top_trusted(3),
            "low_trust_actions": self.scorer.low_trust_actions(),
        }


# ═══════════════════════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════════════════════

def create_trust_engine() -> TrustEngine:
    """Factory: cria TrustEngine pronto para uso."""
    return TrustEngine()
