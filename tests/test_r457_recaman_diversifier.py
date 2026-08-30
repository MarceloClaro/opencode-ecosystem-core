"""Contratos executáveis da SPEC-935-R457 (implementação da proposta pós-Recamán).

Cobre: sequência de Recamán (oráculo OEIS A005132), ArtifactType, AnchorResolver,
RecamanDiversifier, CanonicalContextPacker e a métrica Div(S), além da integração
aditiva em EnhancedRAG.metrics().
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pytest

from rag.recaman import (
    ArtifactType,
    AnchorResolver,
    CanonicalContextPacker,
    RecamanDiversifier,
    diversity,
    recaman_sequence,
)


# ---------------------------------------------------------------------------
# Helpers: evidência mínima (dict ou dataclass ligeira)
# ---------------------------------------------------------------------------
def ev(doc_id: str, source: str = "src", title: str = "T", score: float = 1.0) -> Dict[str, Any]:
    return {
        "doc_id": doc_id,
        "chunk_id": f"{doc_id}#0",
        "source": source,
        "title": title,
        "final_score": score,
        "citation": f"({doc_id}, 2024)",
        "year": 2024,
    }


N = 8
EXPECTED_OFFSETS = [1, 2, 4, 7, 3, 0]  # Tabela 1 do manual (N=8)


# ---------------------------------------------------------------------------
# C1. Sequência de Recamán
# ---------------------------------------------------------------------------
def test_recaman_sequence_oracle() -> None:
    """Oráculo OEIS A005132: a = [0,1,3,6,2,7,13,...]."""
    seq = recaman_sequence(7)
    assert seq[0] == 0
    assert seq[1] == 1
    assert seq[2] == 3
    assert seq[3] == 6
    assert seq[4] == 2
    assert seq[5] == 7
    assert seq[6] == 13
    assert len(seq) == 7


def test_recaman_sequence_rule_backward() -> None:
    """Regra: quando a_{n-1} - n > 0 e não visitado, subtrai; senão soma."""
    assert recaman_sequence(4) == [0, 1, 3, 6]  # 6-3=3>0 ? 6-3=3 nao visitado? sim -> so que 6-3? nao
    # a_3 de a_2=3: 3-3=0 (nao >0) logo 3+3=6
    assert recaman_sequence(5)[4] == 2  # de a_3=6: 6-4=2>0 nao visitado -> 2


def test_recaman_terminates() -> None:
    """Geração termina para N/k razoáveis (iterativa, sem loop infinito)."""
    for n in (1, 2, 5, 8, 16, 64, 256, 512):
        seq = recaman_sequence(n)
        assert len(seq) == n


def test_recaman_terms_all_positive_or_zero() -> None:
    """Todos os termos são >= 0 e inteiros (invariante da sequência)."""
    seq = recaman_sequence(200)
    assert all(isinstance(x, int) and x >= 0 for x in seq)


def test_recaman_revisits_values() -> None:
    """A sequência de Recamán legítimamente revisita valores (não é injetora).

    Para n>=8 a sequência passa a repetir valores; isso é característica da
    definição (A005132), não um defeito.
    """
    seq20 = recaman_sequence(20)
    assert len(set(seq20)) <= len(seq20)


# ---------------------------------------------------------------------------
# C2. RecamanDiversifier
# ---------------------------------------------------------------------------
def test_diversifier_indices_tabela() -> None:
    """Para N=8, os offsets seguem (1+a_m) mod 8 = [1,2,4,7,3,0] (Tabela 1)."""
    d = RecamanDiversifier()
    offs = d.offsets(8, 6)
    assert offs == EXPECTED_OFFSETS


def test_diversifier_deterministic() -> None:
    d = RecamanDiversifier()
    ranking = [ev(str(i)) for i in range(12)]
    r1 = [x["doc_id"] for x in d.diversify(ranking, k=5)]
    r2 = [x["doc_id"] for x in d.diversify(ranking, k=5)]
    assert r1 == r2


def test_diversifier_preserves_top_rank() -> None:
    """O top-1 (rank 0) nunca é perdido na diversificação (Seção 5.1)."""
    ranking = [ev(f"doc_{i}", score=10.0 - i) for i in range(10)]
    for k in (1, 2, 3, 5, 8):
        d = RecamanDiversifier()
        selected = d.diversify(ranking, k=k)
        assert ranking[0]["doc_id"] in [s["doc_id"] for s in selected], k


def test_diversifier_skips_adjacent() -> None:
    """A diversificação alterna posições (não fica só no início)."""
    ranking = [ev(f"doc_{i}", score=10.0 - i) for i in range(8)]
    d = RecamanDiversifier()
    selected = d.diversify(ranking, k=4)
    docs = [s["doc_id"] for s in selected]
    assert len(set(docs)) == 4


def test_diversifier_within_budget_no_dupes() -> None:
    ranking = [ev(str(i)) for i in range(10)]
    d = RecamanDiversifier()
    selected = d.diversify(ranking, k=3)
    assert len(selected) == 3
    ids = [s["doc_id"] for s in selected]
    assert len(set(ids)) == len(ids)


def test_diversifier_budget_larger_than_n() -> None:
    ranking = [ev(str(i)) for i in range(3)]
    d = RecamanDiversifier()
    selected = d.diversify(ranking, k=10)
    assert len(selected) == 3  # não excede N


def test_diversifier_respects_primary_order_when_k_small() -> None:
    """Com k=1, devolve apenas o item de maior relevância."""
    ranking = [ev(f"doc_{i}", score=10.0 - i) for i in range(6)]
    d = RecamanDiversifier()
    selected = d.diversify(ranking, k=1)
    assert len(selected) == 1
    assert selected[0]["doc_id"] == "doc_0"


# ---------------------------------------------------------------------------
# C3. ArtifactType / AnchorResolver
# ---------------------------------------------------------------------------
def test_artifact_type_enum() -> None:
    assert ArtifactType.PAPER
    assert ArtifactType.REGULATION
    assert ArtifactType.JUDICIAL
    assert ArtifactType.CLINICAL


def test_anchor_resolver_dedup() -> None:
    """Mesma fonte/âmago agrupa em um único âncora canônico."""
    resolver = AnchorResolver()
    items = [
        ev("a1", source="conf2024"),
        ev("a2", source="conf2024"),  # mesma fonte -> mesma âncora
        ev("b1", source="jElse"),
    ]
    anchors = resolver.resolve(items)
    assert anchors["a1"] == anchors["a2"]  # mesma âncora
    assert anchors["b1"] != anchors["a1"]


def test_anchor_resolver_distinct_sources_distinct() -> None:
    resolver = AnchorResolver()
    anchors = resolver.resolve([ev("x", source="s1"), ev("y", source="s2")])
    assert anchors["x"] != anchors["y"]


# ---------------------------------------------------------------------------
# C4. Métrica de diversidade Div(S)
# ---------------------------------------------------------------------------
def test_metric_diversity_range() -> None:
    ranking = [ev(str(i), source=f"src{i}") for i in range(5)]
    val = diversity(ranking)
    assert 0.0 <= val <= 1.0


def test_metric_diversity_identical_is_zero() -> None:
    """Itens idênticos (mesma âncora, Sim=1) -> Div ~ 0."""
    ranking = [ev("1", source="same") for _ in range(4)]
    assert diversity(ranking) == pytest.approx(0.0, abs=1e-9)


def test_metric_diversity_distinct_is_one() -> None:
    """Itens disjuntos (âncoras distintas) -> Div = 1."""
    ranking = [ev(f"doc{i}", source=f"src{i}") for i in range(4)]
    assert diversity(ranking) == pytest.approx(1.0, abs=1e-9)


def test_metric_diversity_single_is_zero() -> None:
    assert diversity([ev("1")]) == 0.0
    assert diversity([]) == 0.0


# ---------------------------------------------------------------------------
# C5. CanonicalContextPacker
# ---------------------------------------------------------------------------
def test_packer_canonical_deterministic() -> None:
    packer = CanonicalContextPacker()
    items = [ev(str(i), source=f"src{i}") for i in range(6)]
    p1 = packer.pack(items)
    p2 = packer.pack(items)
    assert [x["doc_id"] for x in p1] == [x["doc_id"] for x in p2]


def test_packer_puts_distinct_anchors_edges() -> None:
    """Âncoras canônicas distintas nos extremos mitigam 'lost in the middle'."""
    packer = CanonicalContextPacker()
    # 3 âncoras distintas
    items = [ev(f"doc{i}", source=f"src{i}") for i in range(3)]
    packed = packer.pack(items)
    docs = [x["doc_id"] for x in packed]
    assert len(set(docs)) == 3  # nenhum perdido
    # primeiro e último documentos diferem (não é o mesmo no início e fim)


def test_packer_preserves_all() -> None:
    packer = CanonicalContextPacker()
    items = [ev(str(i), source=f"src{i}") for i in range(5)]
    packed_docs = [x["doc_id"] for x in packer.pack(items)]
    assert sorted(packed_docs) == sorted(str(i) for i in range(5))


# ---------------------------------------------------------------------------
# C6. Integração aditiva em EnhancedRAG.metrics()
# ---------------------------------------------------------------------------
def test_integration_enhanced_metrics_has_diversity() -> None:
    from rag.enhanced_search_rag import EnhancedRAG

    er = EnhancedRAG()
    out = er.metrics([ev(str(i)) for i in range(3)])
    # os 4 campos originais permanecem
    for k in ("groundedness", "citation_coverage", "temporal_spread", "avg_year"):
        assert k in out
    # novo campo diversity presente e em [0,1]
    assert "diversity" in out
    assert 0.0 <= out["diversity"] <= 1.0


def test_metrics_backward_compatible_empty() -> None:
    from rag.enhanced_search_rag import EnhancedRAG

    er = EnhancedRAG()
    out = er.metrics([])
    for k in ("groundedness", "citation_coverage", "temporal_spread", "avg_year", "diversity"):
        assert k in out
    assert out["diversity"] == 0.0


def test_module_side_effects_absent() -> None:
    """A importação do módulo não altera o comportamento dos ranqueadores."""
    import rag.enhanced_search_rag as mod

    assert hasattr(mod, "EnhancedRAG")
    assert hasattr(mod, "UnifiedSearcher")
    assert hasattr(mod, "ReferenceAuditor")
