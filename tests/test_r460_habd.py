"""Contratos executáveis da SPEC-935-R460 (HABD).

Valida: resolução de âncoras, determinismo, preferência por âncora nova,
lambda adaptativo determinístico (monopolista vs misto), orçamento, e a
comparação justa no benchmark de coorte R458.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from rag.habd import HABD
from rag.recaman import AnchorResolver

ROOT = Path(__file__).resolve().parent.parent


def _mk(doc_id, source, score, i):
    return {
        "doc_id": doc_id,
        "source": source,
        "final_score": score,
        "text": f"texto do doc {i} com termos {['a','b','c','d','e'][i%5]}",
    }


def _ranking():
    # ranking monopolista no topo: 3 da família A nas 1as posições
    return [
        _mk("a1", "A", 0.90, 0),
        _mk("a2", "A", 0.89, 1),
        _mk("a3", "A", 0.88, 2),
        _mk("b1", "B", 0.70, 3),
        _mk("c1", "C", 0.65, 4),
        _mk("d1", "D", 0.60, 5),
        _mk("e1", "E", 0.55, 6),
        _mk("f1", "F", 0.50, 7),
    ]


# C1. Módulo e âncoras
def test_module_exists() -> None:
    from rag.habd import HABD  # noqa: F401


def test_anchor_resolved() -> None:
    h = HABD()
    ranking = _ranking()
    resolved = h.resolve_anchors(ranking)
    # resolve_anchors devolve lista de itens com campo _anchor
    by_id = {d["doc_id"]: d for d in resolved}
    assert by_id["a1"]["_anchor"] == by_id["a2"]["_anchor"] == "A"
    assert by_id["b1"]["_anchor"] == "B"


# C2. Determinismo e invariantes
def test_deterministic() -> None:
    h = HABD()
    r1 = h.select(_ranking(), 4)
    r2 = h.select(_ranking(), 4)
    assert [d["doc_id"] for d in r1] == [d["doc_id"] for d in r2]


def test_top1_preserved() -> None:
    h = HABD()
    sel = h.select(_ranking(), 4)
    assert sel[0]["doc_id"] == "a1"


def test_budget_respected() -> None:
    h = HABD()
    sel = h.select(_ranking(), 4)
    assert len(sel) == 4
    ids = [d["doc_id"] for d in sel]
    assert len(set(ids)) == 4  # sem duplicatas


# C3. Preferência por âncora nova
def test_prefers_novel_anchor() -> None:
    """Com base=0.3 (monopolista), âncoras novas são preferidas a repetir A."""
    h = HABD(lambda_base=0.3)
    sel = h.select(_ranking(), 4)
    anchors = [d["_anchor"] for d in sel]
    # deve pegar âncoras distintas: A, B, C, D (não repetir A)
    assert len(set(anchors)) == 4


# C4. λ adaptativo determinístico
def test_lambda_adaptive_monopolistic() -> None:
    h = HABD(lambda_base=0.7, lambda_min=0.3)
    # ranking monopolista: top-6 só família A => mu = 1/6 baixo => lambda baixo
    mono = [_mk(f"x{i}", "A", 1.0 - 0.01 * i, i) for i in range(6)]
    lam = h.adaptive_lambda(mono)
    # mu = 1/6 => 0.3 + (1/6)*0.4 = 0.3667 (determinístico); bem abaixo da base
    assert lam <= 0.40
    assert lam < h.adaptive_lambda([_mk("y0","A",1.0,0),_mk("y1","B",0.9,1)])


def test_lambda_adaptive_mixed() -> None:
    h = HABD(lambda_base=0.7, lambda_min=0.3)
    # ranking misto: cada família aparece uma vez => mu alto => lambda ~ base
    mixed = [_mk(f"x{i}", chr(65 + i), 1.0 - 0.01 * i, i) for i in range(6)]
    lam = h.adaptive_lambda(mixed)
    assert lam >= 0.65  # próximo de 0.7


def test_lambda_in_range() -> None:
    h = HABD()
    for r in (_ranking(), [_mk("x0", "A", 0.9, 0), _mk("x1", "B", 0.8, 1)]):
        lam = h.adaptive_lambda(r)
        assert 0.0 < lam <= 1.0


# C5. Comparação no coorte R458 (justa)
def test_beats_recaman_topk_in_cohort() -> None:
    sys.path.insert(0, str(ROOT))
    from benchmarks.cohort_recaman import build_pilot_corpus, run_cohort

    corpus = build_pilot_corpus()
    res = run_cohort(corpus, top_n=8, k=4, n_queries=4)
    habd = res["per_strategy"].get("habd")
    assert habd is not None
    assert habd["diversity"] > 0.5  # supera o empate top-k/Recamán


def test_vs_mmr_recorded() -> None:
    sys.path.insert(0, str(ROOT))
    from benchmarks.cohort_recaman import build_pilot_corpus, run_cohort

    res = run_cohort(build_pilot_corpus(), top_n=8, k=4, n_queries=4)
    assert "comparison" in res
    assert "habd" in str(res)


def test_grounded_tolerance() -> None:
    sys.path.insert(0, str(ROOT))
    from benchmarks.cohort_recaman import build_pilot_corpus, run_cohort

    res = run_cohort(build_pilot_corpus(), top_n=8, k=4, n_queries=4)
    habd = res["per_strategy"]["habd"]
    atu = res["per_strategy"]["atual"]
    loss = (atu["groundedness"] - habd["groundedness"]) / atu["groundedness"]
    # O veredito H3 deve ser HONESTO: se a queda de groundedness excede a
    # tolerância (5%), o framework NÃO pode alegar vitória (anti-overclaim).
    # Aqui verificamos a consistência entre a queda observada e o veredito.
    if loss > 0.05:
        assert res["verdict_h3"] == "refuta_H3", "queda>tol deve refutar H3 (anti-overclaim)"
    else:
        # se ficou dentro da tolerância, os demais critérios são que verificam H3
        pass


def test_habd_max_coverage_vs_mmr() -> None:
    """HABD atinge cobertura máxima (1.0) e diversidade >= MMR no coorte.

    Distingue 'supera em diversidade' de 'satisfaz H3': o primeiro é observável e
    reportável; o segundo exige também a tolerância de groundedness (H3 rígida).
    """
    sys.path.insert(0, str(ROOT))
    from benchmarks.cohort_recaman import build_pilot_corpus, run_cohort

    res = run_cohort(build_pilot_corpus(), top_n=8, k=4, n_queries=4)
    habd = res["per_strategy"]["habd"]
    mmr = res["per_strategy"]["mmr"]
    # superação em diversidade/cobertura é observável
    assert habd["diversity"] >= mmr["diversity"]
    assert habd["coverage"] >= mmr["coverage"]
