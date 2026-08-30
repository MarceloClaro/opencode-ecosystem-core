# -*- coding: utf-8 -*-
"""
HABD — Diversificador Híbrido Anchor-Blended Determinístico (SPEC-935-R460).

Combina a virtude do Recamán (determinismo, custo baixo, sem parâmetros) com a
virtude do MMR (diversidade de conteúdo), operando sobre **âncoras canônicas** e
ajustando o balanço relevância↔diversidade (lambda) **por query**, de forma
determinística e sem LLM/fine-tuning.

Fundamentação (literatura 2024–2026):
- DF-RAG (arXiv 2601.17212): o lambda ótimo do MMR varia por query; lambda
  adaptativo melhora sobre MMR vanilla. Aqui o lambda é derivado por heurística
  determinística (índice de mistura de âncoras), não por LLM.
- "Over-retrieve before MMR" e rotação de lambda (RAG Cookbook 2026 / Qdrant).
- "Reranking trap" (Chauzov 2025): rerankers de relevância colapsam diversidade
  por design; diversificação exige dissimilaridade explícita.

Ideia central: cada item pertence a uma âncora canônica (fonte/âmago). A seleção
gulosa maximiza relevância ponderada por lambda, penalizando itens cuja âncora já
foi representada (Sim_anchor = 1 se mesma âncora, 0 caso contrário). O lambda é
reduzido quando o ranking é "localmente monopolista" (poucas âncoras distintas no
topo), forçando a seleção a buscar âncoras novas — resolvendo o gargalo estrutural
do esquema posicional puro.

Sem overclaim: avalia-se em corpus-piloto controlado; não se alega superioridade
absoluta sem evidência no benchmark.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from rag.recaman import AnchorResolver


class HABD:
    """Diversificador híbrido anchor-blended determinístico."""

    def __init__(
        self,
        lambda_base: float = 0.7,
        lambda_min: float = 0.3,
        mu_window: int = 6,
    ):
        if not (0.0 < lambda_min <= lambda_base <= 1.0):
            raise ValueError("precisa 0 < lambda_min <= lambda_base <= 1")
        self.lambda_base = lambda_base
        self.lambda_min = lambda_min
        self.mu_window = mu_window
        self.resolver = AnchorResolver()

    # -- Resolução de âncoras -------------------------------------------
    @staticmethod
    def _anchor_of(item: Any) -> str:
        if isinstance(item, dict):
            src = item.get("_anchor") or item.get("source") or item.get("doc_id") or item.get("title")
            return str(src or "unknown")
        src = getattr(item, "_anchor", None) or getattr(item, "source", None) or \
              getattr(item, "doc_id", None) or getattr(item, "title", None)
        return str(src or "unknown")

    def resolve_anchors(self, ranking: Sequence[Any]) -> List[Dict[str, Any]]:
        """Retorna os itens enriquecidos com o campo '_anchor'."""
        out: List[Dict[str, Any]] = []
        for it in ranking:
            if isinstance(it, dict):
                d = dict(it)
                d["_anchor"] = d.get("_anchor") or self._anchor_of(d)
                out.append(d)
            else:
                out.append(it)
        return out

    # -- Lambda adaptativo determinístico -------------------------------
    @staticmethod
    def _score(item: Any) -> float:
        return float(
            item.get("final_score", 0) if isinstance(item, dict)
            else getattr(item, "final_score", 0) or 0.0
        )

    def mix_index(self, ranking: Sequence[Any]) -> float:
        """Índice de mistura de âncoras no topo (janela mu_window).

        mu = (# âncoras distintas no topo) / min(window, # itens).
        mu alto => ranking já misto; mu baixo => ranking monopolista.
        """
        window = ranking[: self.mu_window]
        if not window:
            return 0.0
        distinct = len({self._anchor_of(it) for it in window})
        denom = min(self.mu_window, len(window))
        return distinct / max(1, denom)

    def adaptive_lambda(self, ranking: Sequence[Any]) -> float:
        """lambda por query derivado do índice de mistura, determinístico.

        Monopolista (mu -> 0) => lambda -> lambda_min (busca diversidade).
        Misto (mu -> 1)      => lambda -> lambda_base (favorece relevância).
        """
        mu = self.mix_index(ranking)
        lam = self.lambda_min + mu * (self.lambda_base - self.lambda_min)
        return round(max(0.0, min(1.0, lam)), 4)

    # -- Seleção MMR anchor-blended ---------------------------------------
    def select(self, ranking: Sequence[Any], k: int) -> List[Any]:
        """Seleciona até k itens com MMR anchor-blended determinístico.

        A cada passo, itens de âncora já representada sofrem penalidade de
        similaridade; itens de âncora nova, não. Entre itens da mesma âncora,
        vence o mais relevante. Desempates por ordem no ranking (determinístico).
        """
        if not ranking or k <= 0:
            return []
        items = self.resolve_anchors(list(ranking))
        budget = min(k, len(items))
        lam = self.adaptive_lambda(items)

        selected: List[Any] = []
        represented: set = set()

        # Passo 1: relevância primária (âncora do top-1 sempre representada).
        first = items[0]
        selected.append(first)
        represented.add(self._anchor_of(first))

        remaining = list(items[1:])
        while len(selected) < budget and remaining:
            best_idx, best_score = -1, -1e18
            for i, cand in enumerate(remaining):
                rel = self._score(cand)
                anchor = self._anchor_of(cand)
                # similaridade à seleção: 1 se a âncora já está representada, senão 0
                max_sim = 1.0 if anchor in represented else 0.0
                obj = lam * rel - (1 - lam) * max_sim
                # desempate determinístico: critério de relevância decrescente
                if obj > best_score + 1e-12 or (
                    abs(obj - best_score) <= 1e-12 and rel > self._score(remaining[best_idx] if best_idx >= 0 else cand)
                ):
                    best_score = obj
                    best_idx = i
            chosen = remaining.pop(best_idx)
            selected.append(chosen)
            represented.add(self._anchor_of(chosen))

        return selected


# funções de conveniência para o benchmark
def habd_select(ranking: Sequence[Any], k: int, **kw) -> List[Any]:
    h = HABD(**kw)
    return h.select(ranking, k)
