# -*- coding: utf-8 -*-
"""
Attention Router — Multi-Head Attention para Roteamento de Tarefas
==================================================================
Analogia Transformer: a tarefa é a *query* (Q), os Agent Cards são as *keys* (K)
e os próprios agentes são os *values* (V). O roteamento calcula
softmax(Q·K / sqrt(d)) e seleciona o agente com maior peso de atenção.

Quatro cabeças de atenção (multi-head), cada uma com um critério:
- head_semantic:  similaridade semântica tarefa × agente (embeddings)
- head_capability: cobertura exata das capacidades requeridas
- head_confidence: confidence ledger metacognitivo (histórico de sucesso)
- head_load:       disponibilidade/carga atual do agente

Inspiração:
- Multi-Head Attention (Vaswani et al. 2017)
- Perceiver (deepmind-research): cross-attention latente × entradas
- PrediNet (deepmind-research): atenção relacional para raciocínio

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import math
from typing import Dict, List, Tuple, Any

from .embedder import TaskEmbedder, D_MODEL


def _dot(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _softmax(scores: List[float]) -> List[float]:
    if not scores:
        return []
    m = max(scores)
    exps = [math.exp(s - m) for s in scores]
    total = sum(exps) or 1.0
    return [e / total for e in exps]


class AttentionRouter:
    """Roteador multi-cabeça: decide qual agente atende cada tarefa."""

    # Pesos de combinação das cabeças (aprendíveis no futuro; fixos por ora)
    HEAD_WEIGHTS = {
        "semantic": 0.30,
        "capability": 0.35,
        "confidence": 0.25,
        "load": 0.10,
    }

    def __init__(self):
        self.embedder = TaskEmbedder()

    # ------------------------------------------------------------------
    # Cabeças de atenção
    # ------------------------------------------------------------------
    def _head_semantic(self, task_vec: List[float], cards: List[Dict]) -> List[float]:
        """Q·K / sqrt(d) sobre embeddings semânticos."""
        scale = math.sqrt(D_MODEL)
        return [
            _dot(task_vec, self.embedder.embed_agent(card)) * 10.0 / scale * D_MODEL ** 0.5
            for card in cards
        ]

    def _head_capability(self, required: List[str], cards: List[Dict]) -> List[float]:
        """Cobertura das capacidades requeridas (Jaccard direcionado)."""
        scores = []
        for card in cards:
            caps = set(card.get("capabilities", []))
            if not required:
                scores.append(0.5)
                continue
            overlap = len(caps & set(required)) / len(set(required))
            scores.append(overlap * 4.0)  # amplifica para dominar o softmax
        return scores

    def _head_confidence(self, cards: List[Dict]) -> List[float]:
        """Confiança metacognitiva histórica (confidence ledger)."""
        return [card.get("confidence_score", 0.5) * 2.0 for card in cards]

    def _head_load(self, cards: List[Dict]) -> List[float]:
        """Disponibilidade: penaliza agentes ocupados."""
        return [1.0 if card.get("status") == "available" else -2.0 for card in cards]

    # ------------------------------------------------------------------
    # Atenção combinada
    # ------------------------------------------------------------------
    def route(self, description: str, required_capabilities: List[str],
              cards: List[Dict], positional_index: int = 0) -> List[Tuple[str, float]]:
        """
        Retorna ranking [(agent_id, attention_weight)] ordenado do melhor
        para o pior, com pesos softmax somando 1.
        """
        if not cards:
            return []

        task_vec = self.embedder.embed_task(description, required_capabilities, positional_index)

        heads = {
            "semantic": self._head_semantic(task_vec, cards),
            "capability": self._head_capability(required_capabilities, cards),
            "confidence": self._head_confidence(cards),
            "load": self._head_load(cards),
        }

        # Combinação linear das cabeças (projeção W_O do multi-head)
        combined = [0.0] * len(cards)
        for name, scores in heads.items():
            w = self.HEAD_WEIGHTS[name]
            for i, s in enumerate(scores):
                combined[i] += w * s

        weights = _softmax(combined)
        ranking = sorted(
            zip([c["agent_id"] for c in cards], weights),
            key=lambda x: x[1],
            reverse=True,
        )
        return ranking

    def explain(self, description: str, required_capabilities: List[str],
                cards: List[Dict]) -> Dict[str, Any]:
        """Auditoria: expõe os scores por cabeça para transparência total."""
        task_vec = self.embedder.embed_task(description, required_capabilities)
        return {
            "task": description,
            "heads": {
                "semantic": dict(zip([c["agent_id"] for c in cards],
                                     self._head_semantic(task_vec, cards))),
                "capability": dict(zip([c["agent_id"] for c in cards],
                                       self._head_capability(required_capabilities, cards))),
                "confidence": dict(zip([c["agent_id"] for c in cards],
                                       self._head_confidence(cards))),
                "load": dict(zip([c["agent_id"] for c in cards],
                                 self._head_load(cards))),
            },
            "ranking": self.route(description, required_capabilities, cards),
        }
