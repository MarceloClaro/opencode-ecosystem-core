# -*- coding: utf-8 -*-
"""Atenção executiva para o Centro de Produção Global.

Analogia Transformer: em vez de apenas ranquear agentes, esta camada ranqueia
*ações de produção* (especificar, rotear, executar, verificar, refletir,
entregar, pedir consentimento, parar) por múltiplas cabeças de atenção.

É uma heurística determinística e auditável, não uma rede neural treinada.
Gates de disponibilidade, consentimento, orçamento e capacidades são
não negociáveis; somente candidatos elegíveis recebem scores softmax.
"""

from __future__ import annotations

import math
import unicodedata
from typing import Any, Dict, Iterable, List, Tuple

from .attention import _cosine_unit_interval, _softmax, _unit_score
from .embedder import TaskEmbedder, _tokenize

HEAD_NAMES = ("goal", "stage", "evidence", "risk", "confidence", "budget",
              "progress", "tags")
HEAD_WEIGHTS = {
    "goal": 0.15,
    "stage": 0.20,
    "evidence": 0.15,
    "risk": 0.15,
    "confidence": 0.10,
    "budget": 0.05,
    "progress": 0.10,
    "tags": 0.10,
}
DEFAULT_PROGRESS = {
    "specify": 0.6, "route": 0.5, "execute": 0.8, "verify": 0.7,
    "reflect": 0.4, "deliver": 0.9, "consent": 0.3, "stop": 0.0,
}

# Transições permitidas entre estágios. A ação pode pertencer ao estágio atual
# ou preparar o próximo; saltos são permitidos apenas quando explícitos.
STAGE_ORDER = (
    "intake", "spec", "route", "execute", "verify", "reflect", "deliver", "complete",
)
ALLOWED_TRANSITIONS = {
    "intake": {"intake", "spec"},
    "spec": {"spec", "route"},
    "route": {"route", "execute"},
    "execute": {"execute", "verify"},
    "verify": {"verify", "reflect", "execute"},
    "reflect": {"reflect", "deliver"},
    "deliver": {"deliver", "complete"},
    "complete": {"complete"},
    "blocked": {"blocked", "spec"},
    "awaiting_consent": {"awaiting_consent", "spec", "route", "execute"},
}


def _text(value: Any, limit: int = 400) -> str:
    if not isinstance(value, str):
        value = str(value)
    return "".join(char if char >= " " or char == "\n" else " " for char in value)[:limit]


def _finite(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def _tag_tokens(value: str) -> set[str]:
    """Tokeniza ignorando acentos para casar 'vídeo' com 'video'."""
    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    return {token for token in _tokenize(normalized) if len(token) > 2}


def _stage_score(current: str, candidate: str) -> float:
    if candidate == current:
        return 1.0
    if candidate in ALLOWED_TRANSITIONS.get(current, set()):
        return 0.75
    return 0.0


def _normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    if set(weights) != set(HEAD_NAMES):
        raise ValueError("HEAD_WEIGHTS deve conter exatamente as oito cabeças")
    normalized: Dict[str, float] = {}
    for name in HEAD_NAMES:
        value = _finite(weights[name], float("nan"))
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError(f"peso inválido para a cabeça {name!r}")
        normalized[name] = value
    if not math.isclose(math.fsum(normalized.values()), 1.0, abs_tol=1e-12):
        raise ValueError("HEAD_WEIGHTS deve somar 1")
    return normalized


class ExecutiveAttention:
    """Ranqueia ações de produção por seis cabeças auditáveis."""

    def __init__(self, weights: Dict[str, float] | None = None):
        self.weights = _normalize_weights(weights or HEAD_WEIGHTS)
        self.embedder = TaskEmbedder()

    def _candidate_score(self, goal_text: str, goal_vec: List[float], state: Dict[str, Any],
                         candidate: Dict[str, Any], budget: float) -> Dict[str, float]:
        description = _text(candidate.get("description", candidate.get("action_id", "")))
        candidate_vec = self.embedder.embed_text(description)
        evidence_count = int(_finite(state.get("evidence_count", 0)))
        evidence_gain = _unit_score(candidate.get("evidence_gain", 0.0))
        if evidence_count < 2:
            evidence_gain = max(evidence_gain, 0.55)
        cost = max(0.0, _finite(candidate.get("cost", 0.0)))
        budget_score = 1.0 if budget <= 0 else max(0.0, 1.0 - min(1.0, cost / budget))
        progress_default = DEFAULT_PROGRESS.get(str(candidate.get("kind", "")), 0.2)
        goal_tokens = _tag_tokens(goal_text)
        keywords = candidate.get("keywords") or []
        if isinstance(keywords, str):
            keywords = [keywords]
        keyword_tokens = _tag_tokens(" ".join(str(x) for x in keywords))
        tags_score = (len(goal_tokens & keyword_tokens) / len(goal_tokens)
                      if goal_tokens and keyword_tokens else 0.5)
        return {
            "goal": _cosine_unit_interval(goal_vec, candidate_vec),
            "stage": _stage_score(str(state.get("stage", "intake")),
                                  str(candidate.get("stage", "intake"))),
            "evidence": evidence_gain,
            "risk": 1.0 - _unit_score(candidate.get("risk", 0.0)),
            "confidence": _unit_score(candidate.get("confidence", 0.5), 0.5),
            "budget": budget_score,
            "progress": _unit_score(candidate.get("progress", progress_default),
                                    progress_default),
            "tags": tags_score,
        }

    @staticmethod
    def _hard_gate_reasons(state: Dict[str, Any], candidate: Dict[str, Any],
                           budget: float) -> List[str]:
        reasons: List[str] = []
        if candidate.get("available") is not True:
            reasons.append("unavailable")
        if candidate.get("requires_consent") is True and state.get("consent") is not True:
            reasons.append("consent_required")
        cost = max(0.0, _finite(candidate.get("cost", 0.0)))
        if budget <= 0 or cost > budget:
            reasons.append("budget_exceeded")
        required = state.get("required_capabilities") or []
        if isinstance(required, str):
            required = [required]
        capabilities = candidate.get("capabilities") or []
        if isinstance(capabilities, str):
            capabilities = [capabilities]
        try:
            missing = sorted(set(required) - set(capabilities))
        except TypeError:
            missing = ["invalid_capabilities"]
        if missing:
            reasons.append("missing_capabilities:" + ",".join(missing))
        if _unit_score(candidate.get("risk", 0.0)) >= 0.9 and state.get("consent") is not True:
            reasons.append("high_risk_without_consent")
        return reasons

    def evaluate(self, goal: str, state: Dict[str, Any],
                 candidates: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        """Retorna ranking, gates e explicação por cabeça."""
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("O objetivo da produção deve conter texto.")
        if not isinstance(state, dict):
            raise ValueError("O estado da produção deve ser um objeto.")
        budget = max(0.0, _finite(state.get("budget", 0.0)))
        goal_vec = self.embedder.embed_text(goal)
        candidate_list = list(candidates)
        eligible: List[Dict[str, Any]] = []
        excluded: Dict[str, List[str]] = {}
        seen: set[str] = set()
        for index, raw in enumerate(candidate_list):
            if not isinstance(raw, dict):
                excluded[f"candidate-{index}"] = ["invalid_candidate"]
                continue
            action_id = raw.get("action_id")
            if not isinstance(action_id, str) or not action_id.strip():
                excluded[f"candidate-{index}"] = ["missing_action_id"]
                continue
            action_id = action_id.strip()
            if action_id in seen:
                excluded[action_id] = ["duplicate_action_id"]
                continue
            seen.add(action_id)
            reasons = self._hard_gate_reasons(state, raw, budget)
            if reasons:
                excluded[action_id] = reasons
            else:
                eligible.append({**raw, "action_id": action_id})

        if not eligible:
            return {
                "ranking": [], "selected": None, "consent_required": False,
                "excluded": excluded, "heads": {name: {} for name in HEAD_NAMES},
                "utility": {}, "weights": dict(self.weights),
                "policy": "atenção executiva determinística; não é rede neural treinada",
            }

        scores = {
            name: {} for name in HEAD_NAMES
        }
        for candidate in eligible:
            head_scores = self._candidate_score(goal, goal_vec, state, candidate, budget)
            for name in HEAD_NAMES:
                scores[name][candidate["action_id"]] = round(head_scores[name], 6)
        utility = {
            candidate["action_id"]: math.fsum(
                self.weights[name] * scores[name][candidate["action_id"]]
                for name in HEAD_NAMES
            )
            for candidate in eligible
        }
        weights = dict(zip(
            [candidate["action_id"] for candidate in eligible],
            _softmax([utility[candidate["action_id"]] for candidate in eligible]),
        ))
        ranking = sorted(weights.items(), key=lambda item: (-item[1], item[0]))
        consent_required = any(
            candidate.get("requires_consent") is True and state.get("consent") is not True
            for candidate in candidate_list if isinstance(candidate, dict)
        )
        return {
            "ranking": ranking,
            "selected": ranking[0][0] if ranking else None,
            "consent_required": consent_required,
            "excluded": excluded,
            "heads": scores,
            "utility": {key: round(value, 6) for key, value in utility.items()},
            "weights": dict(self.weights),
            "policy": "atenção executiva determinística; não é rede neural treinada",
        }

    def explain(self, goal: str, state: Dict[str, Any],
                candidates: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        return {"goal": goal, **self.evaluate(goal, state, candidates)}
