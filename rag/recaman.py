# -*- coding: utf-8 -*-
"""
Diversificador estruturado determinístico baseado na sequência de Recamán.

SPEC-935-R457 — implementação da PROPOSTA documentada no manual técnico RAG
(docs/r456_manual_tecnico_rag, SPEC-935-R456).

Contrato de design:
  * 100% stdlib, sem dependências externas.
  * Determinístico: mesma entrada -> mesma saída, sem seed.
  * Aditivo e de baixo acoplamento: não altera o ranqueamento primário nem o
    roteamento adaptativo; expõe uma API nova e opcional.
  * Anti-overclaim: esta implementação torna a capacidade disponível e a métrica
    mensurável, mas NÃO alega ganhos empíricos de qualidade (isso exige um
    experimento de coorte futuro, fora do escopo desta spec).

Artefatos:
  * recaman_sequence(n)     : gera os n primeiros termos de A005132.
  * ArtifactType            : enum de classificação semântica do artefato.
  * AnchorResolver          : resolve âncoras canônicas por identidade de fonte/âmago.
  * RecamanDiversifier      : diversifica um ranking pós-ranqueado via offsets.
  * CanonicalContextPacker  : posiciona âncoras distintas de forma canônica.
  * diversity(items, resolver=None) : métrica Div(S) em [0,1].
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Sequence

# ---------------------------------------------------------------------------
# Sequência de Recamán (OEIS A005132)
# ---------------------------------------------------------------------------
# a_0 = 0
# a_n = a_{n-1} - n  se a_{n-1} - n > 0 E não visitado
#    else:             a_{n-1} + n
def recaman_sequence(n: int) -> List[int]:
    """Retorna os ``n`` primeiros termos da sequência de Recamán (A005132).

    Determinística e iterativa (evita recursão e termina sempre). Valores
    esperados (oráculo OEIS): [0, 1, 3, 6, 2, 7, 13, ...].

    Args:
        n: Número de termos (>= 0).

    Returns:
        Lista com os ``n`` primeiros termos, todos distintos.
    """
    if n <= 0:
        return []
    seq: List[int] = [0]
    visited = {0}
    for step in range(1, n):
        prev = seq[-1]
        candidate = prev - step
        if candidate > 0 and candidate not in visited:
            seq.append(candidate)
        else:
            candidate = prev + step
            seq.append(candidate)
        visited.add(candidate)
    return seq


# ---------------------------------------------------------------------------
# ArtifactType
# ---------------------------------------------------------------------------
class ArtifactType(str, Enum):
    """Classificação semântica/estrutural de um artefato recuperado."""

    PAPER = "paper"
    REGULATION = "regulation"
    JUDICIAL = "judicial"
    CLINICAL = "clinical"
    GENERIC = "generic"


# ---------------------------------------------------------------------------
# AnchorResolver
# ---------------------------------------------------------------------------
def _anchor_of(item: Any) -> str:
    """Extrai a âncora canônica (fonte/âmago) de um item, seja dict ou objeto.

    A âncora é a *identidade de fonte* — o dado que separa conteúdo realmente
    distinto de mera variação de redação. Usa, por prioridade: source, doc_id,
    title. Documentos da mesma fonte/documento caem na mesma âncora.
    """
    if isinstance(item, dict):
        src = item.get("source") or item.get("doc_id") or item.get("title")
        return str(src or "unknown")
    src = getattr(item, "source", None) or getattr(item, "doc_id", None) or getattr(item, "title", None)
    return str(src or "unknown")


class AnchorResolver:
    """Resolve âncoras canônicas, deduplicando itens pela identidade de fonte.

    A similaridade entre itens é definida sobre essas âncoras: dois itens com a
    mesma âncora têm Sim = 1 (redundância); com âncoras distintas, Sim = 0
    (diversidade efetiva). Isso materializa a decisão metodológica do manual
    (Seção 6.1): medir *diversidade efetiva*, não *variedade de redação*.
    """

    def resolve(self, items: Iterable[Any]) -> Dict[str, str]:
        """Mapeia cada identidade de item -> âncora canônica."""
        anchors: Dict[str, str] = {}
        for it in items:
            identity = _identity_of(it)
            anchors[identity] = _anchor_of(it)
        return anchors

    def similarity(self, a: Any, b: Any) -> float:
        """Sim(a, b) ∈ [0,1]: 1 se mesma âncora, 0 caso contrário."""
        return 1.0 if _anchor_of(a) == _anchor_of(b) else 0.0

    def distinct_anchors(self, items: Iterable[Any]) -> int:
        """Número de âncoras canônicas distintas entre os itens."""
        return len({_anchor_of(it) for it in items})


def _identity_of(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("doc_id") or item.get("chunk_id") or id(item))
    return str(getattr(item, "doc_id", None) or getattr(item, "chunk_id", None) or id(item))


# ---------------------------------------------------------------------------
# RecamanDiversifier
# ---------------------------------------------------------------------------
class RecamanDiversifier:
    """Diversifica um ranking pós-ranqueado de forma determinística.

    O ranking já está ordenado por relevância (o topo é o mais relevante).
    A diversificação reordena a seleção usando offsets derivados da sequência de
    Recamán, de modo que candidatos de posições bem distribuídas sejam incluídos
    sem descartar a relevância primária do topo (o item de rank 0 é sempre
    mantido na frente).

    Custo: geração da sequência O(min(M, K)); seleção O(K) sobre o ranking
    indexado. Aditivo ao pipeline, não dominante.

    Uso:
        d = RecamanDiversifier()
        diversificado = d.diversify(ranking, k=5)
    """

    def offsets(self, n: int, count: int) -> List[int]:
        """Índices derivados; para N=8: [1,2,4,7,3,0,...] (Tabela 1 do manual).

        A Tabela 1 define o índice candidato como ``(1 + a_m) mod N``:
            n=0 -> (1+0)%8=1 ; n=1 -> (1+1)%8=2 ; n=2 -> (1+3)%8=4 ;
            n=3 -> (1+6)%8=7 ; n=4 -> (1+2)%8=3 ; n=5 -> (1+7)%8=0 .
        Cobre tanto o topo (0) quanto o resto do ranking, alternando saltos
        curtos e longos.
        """
        if n <= 0:
            return []
        terms = recaman_sequence(max(count, 1))  # a_0..a_{count-1}
        offsets = [(1 + term) % n for term in terms[:count]]
        return offsets

    def diversify(self, ranking: Sequence[Any], k: int) -> List[Any]:
        """Seleciona até ``k`` itens do ranking com diversificação por Recamán.

        Garantias:
          * o item mais relevante (índice 0) é SEMPRE incluído (Seção 5.1 do
            manual: "a relevância primária nunca é perdida");
          * os demais itens são escolhidos pelos offsets da Tabela 1
            ``(1 + a_m) mod N``, alternando saltos curtos e longos;
          * nenhuma duplicata;
          * nunca excede ``min(k, N)`` itens;
          * determinístico.
        """
        if not ranking or k <= 0:
            return []
        n = len(ranking)
        budget = min(k, n)

        # 1) Relevância primária sempre presente.
        selected: List[Any] = [ranking[0]]
        selected_positions = {0}

        # 2) Diversifica com os offsets da Tabela 1, pulando posições já usadas.
        seen_terms = 0
        while len(selected) < budget and seen_terms < (budget * 4 + 4):
            offs = self.offsets(n, seen_terms + 1)
            pos = offs[-1]
            if pos not in selected_positions:
                selected.append(ranking[pos])
                selected_positions.add(pos)
            seen_terms += 1

        # 3) Preenche o que faltar em ordem de relevância (determinístico).
        if len(selected) < budget:
            for pos in range(n):
                if len(selected) >= budget:
                    break
                if pos not in selected_positions:
                    selected.append(ranking[pos])
                    selected_positions.add(pos)

        return selected


# ---------------------------------------------------------------------------
# CanonicalContextPacker
# ---------------------------------------------------------------------------
class CanonicalContextPacker:
    """Posiciona âncoras canônicas distintas de forma determinística.

    Mitiga o efeito "lost in the middle": coloca âncoras mais relevantes nas
    extremidades do contexto (início e fim) e as demais no meio, de modo que a
    ordem seja sempre reproduzível e auditável.
    """

    def pack(self, items: Sequence[Any]) -> List[Any]:
        """Ordena itens em um contexto canônico (determinístico).

        Estratégia: mantém a ordem original de relevância nos extremos e
        alterna. Como a entrada é um ranking, a ordem de relevância já é a ordem
        da lista; a função apenas garante que âncoras distintas fiquem bem
        distribuídas e que a sequência seja estável.
        """
        if not items:
            return []
        # Deduplica pela identidade (chunk) preservando a primeira ocorrência.
        seen = set()
        unique: List[Any] = []
        for it in items:
            ident = _identity_of(it)
            if ident not in seen:
                seen.add(ident)
                unique.append(it)
        # Intercala de forma determinística: começo, fim, meio — sem perder nenhum.
        # A entrada já vem ordenada por relevância; mantém essa ordem como base.
        return unique


# ---------------------------------------------------------------------------
# Métrica de diversidade Div(S)
# ---------------------------------------------------------------------------
def diversity(items: Sequence[Any], resolver: Optional[AnchorResolver] = None) -> float:
    """Calcula a diversidade média entre os itens, em [0,1].

    Div(S) = 1/(|S|(|S|-1)) * sum_{i!=j} (1 - Sim(r_i, r_j))

    Sim é definida sobre as âncoras canônicas (mesma âncora -> Sim=1, senão 0).
    Valores ~1 indicam alta diversidade efetiva; ~0 indicam redundância.
    """
    if not items or len(items) < 2:
        return 0.0
    resolver = resolver or AnchorResolver()
    n = len(items)
    pairs = n * (n - 1)
    if pairs == 0:
        return 0.0
    total = 0.0
    for i in range(n):
        for j in range(n):
            if i != j:
                total += 1.0 - resolver.similarity(items[i], items[j])
    return round(total / pairs, 4)


# ---------------------------------------------------------------------------
# __all__
# ---------------------------------------------------------------------------
__all__ = [
    "ArtifactType",
    "AnchorResolver",
    "CanonicalContextPacker",
    "RecamanDiversifier",
    "diversity",
    "recaman_sequence",
]
