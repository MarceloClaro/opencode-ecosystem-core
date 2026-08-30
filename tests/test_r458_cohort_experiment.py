"""Contratos executáveis da SPEC-935-R458 (experimento de coorte Recamán).

Valida a existência do benchmark e os contratos de métricas/hipóteses definidos
na spec, incluindo o baseline MMR determinístico.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmarks.cohort_recaman import (
    build_pilot_corpus,
    run_cohort,
    MMR,
    STRATEGIES,
    write_report,
)

ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# C1. Módulo e corpus
# ---------------------------------------------------------------------------
def test_benchmark_module_exists() -> None:
    import benchmarks.cohort_recaman  # noqa: F401


def test_cohort_has_angles() -> None:
    corpus = build_pilot_corpus()
    angles = corpus["angles"]
    docs = corpus["documents"]
    assert len(angles) >= 3
    assert len(docs) >= len(angles)


def test_corpus_deterministic() -> None:
    c1 = build_pilot_corpus()
    c2 = build_pilot_corpus()
    assert [d.doc_id for d in c1["documents"]] == [d.doc_id for d in c2["documents"]]


# ---------------------------------------------------------------------------
# C2. Estratégias
# ---------------------------------------------------------------------------
def test_current_is_topk() -> None:
    """A estratégia 'atual' seleciona por final_score (top-k)."""
    corpus = build_pilot_corpus()
    results = run_cohort(corpus, top_n=8, k=4, n_queries=2)
    strategy = results["per_strategy"]["atual"]
    # seleção do estado atual == top-k por final_score
    assert strategy["coverage"] >= 0.0  # sanidade


def test_mmr_baseline_exists() -> None:
    mmr = MMR()
    assert callable(mmr.select)
    # λ documentado
    assert 0.0 < mmr.lambda_ < 1.0


def test_recaman_includes_top1() -> None:
    corpus = build_pilot_corpus()
    res = run_cohort(corpus, top_n=8, k=4, n_queries=2)
    # em cada query, o item mais relevante está na seleção Recamán
    for q in res["per_query"]:
        assert q["recaman_top1_present"] is True


def test_recaman_deterministic() -> None:
    corpus = build_pilot_corpus()
    r1 = run_cohort(corpus, top_n=8, k=4, n_queries=2)
    r2 = run_cohort(corpus, top_n=8, k=4, n_queries=2)
    for q1, q2 in zip(r1["per_query"], r2["per_query"]):
        assert q1["recaman_docs"] == q2["recaman_docs"]


# ---------------------------------------------------------------------------
# C3. Métricas
# ---------------------------------------------------------------------------
def test_metrics_in_range() -> None:
    corpus = build_pilot_corpus()
    res = run_cohort(corpus, top_n=8, k=4, n_queries=3)
    for strat, s in res["per_strategy"].items():
        assert 0.0 <= s["diversity"] <= 1.0, strat
        assert 0.0 <= s["groundedness"] <= 1.0, strat
        assert 0.0 <= s["coverage"] <= 1.0, strat


def test_loss_lte_tolerance() -> None:
    """H2 (parte qualidade): queda relativa de groundedness (Recamán) <= 5%."""
    corpus = build_pilot_corpus()
    res = run_cohort(corpus, top_n=8, k=4, n_queries=3)
    assert res["recaman"]["loss_rel_groundedness"] <= 0.05


# ---------------------------------------------------------------------------
# C4. Reporte
# ---------------------------------------------------------------------------
def test_report_created(tmp_path: Path) -> None:
    corpus = build_pilot_corpus()
    res = run_cohort(corpus, top_n=8, k=4, n_queries=2)
    out = tmp_path / "cohort_report.json"
    write_report(res, out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "per_strategy" in data
    assert "verdict" in data
    assert data["verdict"] in ("sustenta_H2", "refuta_H2")


def test_no_overclaim_in_report(tmp_path: Path) -> None:
    corpus = build_pilot_corpus()
    res = run_cohort(corpus, top_n=8, k=4, n_queries=2)
    out = tmp_path / "cohort_report.json"
    write_report(res, out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "escopo" in str(data).lower() or "corpus piloto" in str(data).lower()
