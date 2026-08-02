# -*- coding: utf-8 -*-
"""Roteamento multicritério inspirado em atenção Transformer.

A implementação é uma heurística determinística e auditável, não uma camada
neural treinada. Capacidades obrigatórias e disponibilidade são *hard gates*;
somente os candidatos elegíveis recebem scores normalizados e pesos softmax.
"""

import math
from typing import Any, Dict, List, Tuple

from .embedder import TaskEmbedder


def _dot(a: List[float], b: List[float]) -> float:
    return math.fsum(x * y for x, y in zip(a, b))


def _unit_score(value: Any, default: float = 0.0) -> float:
    """Converte um valor numérico em score finito no intervalo ``[0, 1]``."""

    if isinstance(value, bool):
        return default
    try:
        score = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(score):
        return default
    return max(0.0, min(1.0, score))


def _cosine_unit_interval(a: List[float], b: List[float]) -> float:
    """Mapeia similaridade cosseno de ``[-1, 1]`` para ``[0, 1]``."""

    norm_a = math.sqrt(_dot(a, a))
    norm_b = math.sqrt(_dot(b, b))
    if not math.isfinite(norm_a) or not math.isfinite(norm_b):
        return 0.5
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.5
    cosine = _dot(a, b) / (norm_a * norm_b)
    if not math.isfinite(cosine):
        return 0.5
    cosine = max(-1.0, min(1.0, cosine))
    return (cosine + 1.0) / 2.0


def _softmax(scores: List[float]) -> List[float]:
    if not scores:
        return []
    m = max(scores)
    exps = [math.exp(s - m) for s in scores]
    total = math.fsum(exps) or 1.0
    return [e / total for e in exps]


class AttentionRouter:
    """Ranqueia agentes elegíveis por quatro critérios normalizados.

    Melhoria R347 — Semantic Matching + Skill Handbook:
      - A cabeça 'semantic' usa agora o SemanticMatcher (embeddings semânticos
        via LiteRT-LM/Colibri com fallback hash) em vez de feature hashing puro.
      - A cabeça 'confidence' usa o SkillHandbook (confiança per-skill) quando
        disponível, em vez de confidence ledger genérico.
      - Fallback automático para o comportamento legado se SemanticMatcher
        não estiver disponível.
    """

    _HEAD_NAMES = ("semantic", "capability", "confidence", "load")
    HEAD_WEIGHTS = {
        "semantic": 0.30,
        "capability": 0.35,
        "confidence": 0.25,
        "load": 0.10,
    }

    def __init__(self):
        self._head_weights = self._validated_weights(self.HEAD_WEIGHTS)
        self.embedder = TaskEmbedder()

        # SemanticMatcher (Melhoria #2) — carregamento lazy
        self._semantic_matcher = None

    @property
    def semantic_matcher(self):
        if self._semantic_matcher is None:
            try:
                from transformer.semantic_matcher import semantic_matcher
                self._semantic_matcher = semantic_matcher
            except Exception:
                self._semantic_matcher = False  # False = falhou
        return self._semantic_matcher if self._semantic_matcher else None

    @classmethod
    def _validated_weights(cls, weights: Dict[str, float]) -> Dict[str, float]:
        """Exige uma combinação convexa completa para evitar scores ambíguos."""

        if set(weights) != set(cls._HEAD_NAMES):
            raise ValueError("HEAD_WEIGHTS deve conter exatamente as quatro cabeças")
        normalized: Dict[str, float] = {}
        for name in cls._HEAD_NAMES:
            value = weights[name]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"peso inválido para a cabeça {name!r}")
            score = float(value)
            if not math.isfinite(score) or not 0.0 <= score <= 1.0:
                raise ValueError(f"peso fora de [0, 1] para a cabeça {name!r}")
            normalized[name] = score
        if not math.isclose(math.fsum(normalized.values()), 1.0, abs_tol=1e-12):
            raise ValueError("HEAD_WEIGHTS deve somar 1")
        return normalized

    # ------------------------------------------------------------------
    # Cabeças de atenção
    # ------------------------------------------------------------------
    def _head_semantic(self, task_vec: List[float], cards: List[Dict],
                       description: str = "", required: Optional[List[str]] = None) -> List[float]:
        """Similaridade semântica: SemanticMatcher > feature hashing legado.

        Se o SemanticMatcher estiver disponível, usa matching semântico
        por skills. Caso contrário, usa feature hashing (comportamento legado).
        """
        matcher = self.semantic_matcher

        # Tenta matching semântico por skills primeiro
        if matcher and description:
            try:
                # Busca no Handbook por skills que correspondem à descrição
                matches = matcher.match_capabilities(
                    task_description=description,
                    required_capabilities=required or [],
                    top_k=20,  # busca ampla
                )
                # Constrói score baseado nos matches
                match_scores = {}
                for m in matches:
                    aid = m["agent_id"]
                    if aid not in match_scores or m["score"] > match_scores[aid]:
                        match_scores[aid] = m["score"]

                result = []
                for card in cards:
                    agent_id = card.get("agent_id", "")
                    if agent_id in match_scores:
                        result.append(match_scores[agent_id])
                    else:
                        # Agente sem match semântico — usa legado como fallback
                        result.append(
                            _cosine_unit_interval(task_vec, self.embedder.embed_agent(card))
                        )
                return result
            except Exception:
                pass

        # Fallback: feature hashing legado
        return [
            _cosine_unit_interval(task_vec, self.embedder.embed_agent(card))
            for card in cards
        ]

    def _head_capability(self, required: List[str], cards: List[Dict]) -> List[float]:
        """Cobertura direcionada das capacidades obrigatórias."""

        required_set = set(required)
        scores = []
        for card in cards:
            caps = set(card.get("capabilities", []))
            if not required_set:
                scores.append(1.0)
                continue
            scores.append(len(caps & required_set) / len(required_set))
        return scores

    def _head_confidence(self, cards: List[Dict],
                         description: str = "") -> List[float]:
        """Confiança: SkillHandbook per-skill > confidence ledger genérico.

        Se o SemanticMatcher/SkillHandbook estiver disponível, usa a
        confiança média das skills do agente que correspondem à tarefa.
        Caso contrário, usa o confidence ledger (comportamento legado).
        """
        matcher = self.semantic_matcher

        # Tenta confidence per-skill primeiro
        if matcher and description:
            try:
                matches = matcher.match_capabilities(
                    task_description=description,
                    top_k=50,
                )
                # Constrói confidence score por agente baseado nas skills
                agent_confidences: Dict[str, List[float]] = {}
                for m in matches:
                    aid = m["agent_id"]
                    agent_confidences.setdefault(aid, []).append(m["confidence"])

                result = []
                for card in cards:
                    agent_id = card.get("agent_id", "")
                    if agent_id in agent_confidences:
                        confs = agent_confidences[agent_id]
                        result.append(sum(confs) / len(confs))  # média
                    else:
                        result.append(_unit_score(card.get("confidence_score", 0.5), 0.5))
                return result
            except Exception:
                pass

        # Fallback: confidence ledger genérico
        return [_unit_score(card.get("confidence_score", 0.5), 0.5) for card in cards]

    def _head_load(self, cards: List[Dict]) -> List[float]:
        """Capacidade livre declarada; ausência de carga equivale a livre."""

        return [1.0 - _unit_score(card.get("load", 0.0), 1.0) for card in cards]

    @staticmethod
    def _hard_gate_reasons(required: List[str], card: Dict[str, Any]) -> List[str]:
        """Explica por que um cartão falhou nos gates não negociáveis."""

        reasons: List[str] = []
        if card.get("status") != "available":
            reasons.append("status_not_available")
        capabilities = card.get("capabilities", ())
        if isinstance(capabilities, str):
            capabilities = (capabilities,)
        try:
            capability_set = set(capabilities)
        except TypeError:
            capability_set = set()
            reasons.append("invalid_capabilities")
        missing = sorted(set(required) - capability_set)
        if missing:
            reasons.append("missing_capabilities:" + ",".join(missing))
        return reasons

    def _partition_cards(
        self,
        required: List[str],
        cards: List[Dict],
    ) -> Tuple[List[Dict], Dict[str, List[str]]]:
        eligible_by_id: Dict[str, Dict] = {}
        excluded: Dict[str, List[str]] = {}
        seen: set[str] = set()
        for index, card in enumerate(cards):
            if not isinstance(card, dict):
                excluded[f"candidate-{index}"] = ["invalid_card"]
                continue
            raw_agent_id = card.get("agent_id")
            if not isinstance(raw_agent_id, str) or not raw_agent_id.strip():
                excluded[f"candidate-{index}"] = ["missing_agent_id"]
                continue
            agent_id = raw_agent_id.strip()
            if agent_id in seen:
                eligible_by_id.pop(agent_id, None)
                excluded[agent_id] = ["duplicate_agent_id"]
                continue
            seen.add(agent_id)
            reasons = self._hard_gate_reasons(required, card)
            if reasons:
                excluded[agent_id] = reasons
            else:
                normalized = dict(card)
                normalized["agent_id"] = agent_id
                eligible_by_id[agent_id] = normalized
        return list(eligible_by_id.values()), excluded

    def _evaluate(
        self,
        description: str,
        required_capabilities: List[str],
        cards: List[Dict],
    ) -> Dict[str, Any]:
        """Executa gates, cabeças, utilidade convexa e ranking uma única vez."""

        if isinstance(required_capabilities, str):
            required = [required_capabilities]
        else:
            required = list(dict.fromkeys(required_capabilities))
        eligible, excluded = self._partition_cards(required, cards)
        agent_ids = [str(card["agent_id"]) for card in eligible]

        empty_heads = {name: {} for name in self._HEAD_NAMES}
        if not eligible:
            return {
                "eligible": [],
                "excluded": excluded,
                "heads": empty_heads,
                "utility": {},
                "weights": dict(self._head_weights),
                "ranking": [],
            }

        # O índice global de tarefas não pode alterar uma decisão idêntica.
        task_vec = self.embedder.embed_task(description, required, positional_index=0)
        scores_by_head = {
            "semantic": self._head_semantic(task_vec, eligible, description, required),
            "capability": self._head_capability(required, eligible),
            "confidence": self._head_confidence(eligible, description),
            "load": self._head_load(eligible),
        }
        heads = {
            name: dict(zip(agent_ids, scores_by_head[name]))
            for name in self._HEAD_NAMES
        }
        utility = {
            agent_id: math.fsum(
                self._head_weights[name] * heads[name][agent_id]
                for name in self._HEAD_NAMES
            )
            for agent_id in agent_ids
        }
        final_weights = dict(zip(agent_ids, _softmax([utility[item] for item in agent_ids])))
        ranking = sorted(
            final_weights.items(),
            key=lambda item: (-item[1], item[0]),
        )
        return {
            "eligible": [agent_id for agent_id, _ in ranking],
            "excluded": excluded,
            "heads": heads,
            "utility": utility,
            "weights": dict(self._head_weights),
            "ranking": ranking,
        }

    # ------------------------------------------------------------------
    # Atenção combinada
    # ------------------------------------------------------------------
    def route(self, description: str, required_capabilities: List[str],
               cards: List[Dict], positional_index: int = 0) -> List[Tuple[str, float]]:
        """
        Retorna ranking [(agent_id, attention_weight)] ordenado do melhor
        para o pior, com pesos softmax somando 1.
        """
        del positional_index  # compatibilidade de API; deliberadamente não participa do score
        return self._evaluate(description, required_capabilities, cards)["ranking"]

    def explain(self, description: str, required_capabilities: List[str],
                 cards: List[Dict]) -> Dict[str, Any]:
        """Expõe gates, scores, utilidade, pesos e ranking da heurística."""

        explanation = self._evaluate(description, required_capabilities, cards)
        return {
            "task": description,
            "required_capabilities": list(required_capabilities),
            **explanation,
        }
