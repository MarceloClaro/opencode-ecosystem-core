# -*- coding: utf-8 -*-
"""
Testes R107 — Auditoria sistêmica e hardening de contratos.

Foco:
- wrappers da webapp alinhados às APIs reais de agentic_science_v2
- helpers de consulta usando a API pública do EvidenceGraph
- parsers de qualidade interpretando corretamente a saída do pytest
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_module(module_name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(
        module_name,
        str(REPO_ROOT / relative_path),
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pipeline_helper_run_evosci_matches_ui_contract():
    from webapp.pipeline_helpers import run_evosci

    result = run_evosci("Ethical AI Governance", max_rounds=1)

    assert result["status"] == "completed"
    assert result["rounds_executed"] >= 1
    assert "best_solution" in result
    assert "content" in result["best_solution"]
    assert "score" in result["best_solution"]
    assert isinstance(result["evolutionary_trajectory"], list)


def test_pipeline_helper_run_deep_research_matches_ui_contract():
    from webapp.pipeline_helpers import run_deep_research

    result = run_deep_research("What drugs target BRAF?", max_depth=2, max_rounds=1)

    assert result["question"] == "What drugs target BRAF?"
    assert isinstance(result["answer"], str)
    assert result["entity_count"] >= 0
    assert result["evidence_count"] >= 0
    assert "status" in result["sufficiency_gate"]
    assert isinstance(result["research_plan"], dict)


def test_pipeline_helper_run_peer_review_matches_ui_contract():
    from webapp.pipeline_helpers import run_peer_review

    result = run_peer_review(
        title="Quantum Ethics",
        abstract="This paper studies ethical constraints in AI systems.",
        sections={
            "introduction": "We introduce the problem context.",
            "methods": "We use a synthetic evaluation protocol.",
            "results": "The approach improves traceability and governance.",
        },
    )

    assert "meta_review" in result
    assert "scores" in result
    assert "repair_plan" in result
    assert "gate_result" in result
    assert isinstance(result["scores"], dict)
    assert isinstance(result["verification_agenda"], list)


def test_pipeline_helper_run_manuscript_revision_accepts_normalized_review_package():
    from webapp.pipeline_helpers import run_manuscript_revision

    result = run_manuscript_revision(
        manuscript_text=(
            "# Title\n\n"
            "## Abstract\nA short abstract.\n\n"
            "## Introduction\nA short introduction.\n\n"
            "## Methods\nA short methods section.\n\n"
            "## Results\nA short results section.\n\n"
            "## Conclusion\nA short conclusion."
        ),
        review_package={
            "repair_plan": [
                {
                    "priority": "MAJOR",
                    "area": "methods",
                    "action": "Clarify the evaluation protocol and dataset sampling.",
                    "reviewer": "methodology",
                }
            ]
        },
    )

    assert "revised_manuscript" in result
    assert "rebuttal_letter" in result
    assert "diff_stats" in result
    assert result["changes_applied"] >= 0


def test_pipeline_helper_compose_paper_preserves_manual_sections():
    from webapp.pipeline_helpers import compose_paper

    result = compose_paper(
        title="Quantum Ethics",
        sections_content={
            "abstract": "This paper presents a governance framework.",
            "introduction": "We motivate the problem of ethical AI.",
            "methods": "We combine audit rules with synthetic review.",
            "results": "The system improves traceability.",
            "discussion": "The governance gains are substantial.",
            "conclusion": "The framework is promising.",
        },
        venue="abnt",
        citations=["Reference placeholder"],
    )

    assert result["venue"] == "abnt"
    assert "Quantum Ethics" in result["full_text"]
    assert "This paper presents a governance framework." in result["full_text"]
    assert isinstance(result["citations_formatted"], list)
    assert isinstance(result["consistency_report"], dict)
    assert isinstance(result["structure"], dict)


def test_pipeline_helper_run_full_pipeline_wires_stages(monkeypatch):
    from webapp import pipeline_helpers

    monkeypatch.setattr(
        pipeline_helpers,
        "run_evosci",
        lambda seed_domain, max_rounds, verbose=False: {
            "best_solution": {"content": f"best::{seed_domain}"},
            "status": "completed",
        },
    )
    monkeypatch.setattr(
        pipeline_helpers,
        "run_deep_research",
        lambda question, max_depth=3, max_rounds=5, verbose=False: {
            "answer": f"answer::{question}",
        },
    )
    monkeypatch.setattr(
        pipeline_helpers,
        "run_peer_review",
        lambda title, abstract, sections, verbose=False: {"scores": {"overall": 0.9}},
    )
    monkeypatch.setattr(
        pipeline_helpers,
        "run_manuscript_revision",
        lambda manuscript_text, review_package=None, verbose=False: {"changes_applied": 1},
    )
    monkeypatch.setattr(
        pipeline_helpers,
        "compose_paper",
        lambda title, sections_content, venue="abnt", citations=None, verbose=False: {
            "full_text": f"paper::{title}",
            "venue": venue,
        },
    )

    result = pipeline_helpers.run_full_academic_pipeline(
        seed_domain="Ethical AI",
        max_rounds=1,
        venue="ieee",
    )

    assert result["pipeline_result"] == "completed"
    assert result["deep_research"]["answer"] == "answer::best::Ethical AI"
    assert result["paper"]["venue"] == "ieee"
    assert "timeline" in result and "total" in result["timeline"]


def test_query_evidence_graph_accepts_exported_graph_and_entity_name():
    from agentic_science_v2.evidence_graph import EvidenceGraph
    from webapp.pipeline_helpers import query_evidence_graph

    graph = EvidenceGraph()
    braf = graph.add_entity(
        name="BRAF",
        entity_type="gene",
        evidence_text="BRAF is a proto-oncogene.",
        source="pmid:1",
        source_type="pubmed",
    )
    drug = graph.add_entity(
        name="Vemurafenib",
        entity_type="drug",
        evidence_text="Vemurafenib targets BRAF.",
        source="pmid:2",
        source_type="pubmed",
    )
    graph.add_relation(
        source_id=braf.id,
        target_id=drug.id,
        relation_type="TARGETS",
        evidence_text="Observed in trial.",
        source="pmid:3",
    )

    result = query_evidence_graph("BRAF", graph.to_dict())

    assert result["query"] == "BRAF"
    assert result["entities_found"] >= 1
    assert result["relations_found"] >= 1
    assert result["evidences_found"] >= 0
    assert isinstance(result["subgraph"], dict)


def test_consultation_helper_evidence_graph_summary_uses_public_api():
    from agentic_science_v2.evidence_graph import EvidenceGraph
    from webapp.consultation_helpers import get_evidence_graph_summary

    graph = EvidenceGraph()
    source = graph.add_entity(
        name="Transformer",
        entity_type="concept",
        evidence_text="Transformers are widely used.",
        source="paper:1",
        source_type="paper",
    )
    target = graph.add_entity(name="Attention", entity_type="method")
    graph.add_relation(
        source_id=source.id,
        target_id=target.id,
        relation_type="ASSOCIATED_WITH",
        evidence_text="Attention is a core mechanism.",
        source="paper:2",
    )

    summary = get_evidence_graph_summary(graph)

    assert summary["entity_count"] == 2
    assert summary["relation_count"] == 1
    assert summary["evidence_count"] >= 2
    assert "concept" in summary["entity_types"] or "method" in summary["entity_types"]


def test_quality_report_run_tests_parses_pass_skip_output(monkeypatch):
    mod = _load_module("quality_report_r107", "scripts/quality_report.py")

    class FakeCompletedProcess:
        returncode = 0
        stdout = "1050 passed, 5 skipped, 2 warnings in 12.34s\n"
        stderr = ""

    monkeypatch.setattr(mod.subprocess, "run", lambda *args, **kwargs: FakeCompletedProcess())

    result = mod.run_tests()

    assert result["passed"] == 1050
    assert result["failed"] == 0
    assert result["skipped"] == 5
    assert result["total"] == 1055
    assert result["pass_rate"] == 99.5


def test_check_coverage_check_tests_parses_failed_output(monkeypatch):
    mod = _load_module("check_coverage_r107", "scripts/check_coverage.py")

    class FakeCompletedProcess:
        returncode = 1
        stdout = "1048 passed, 2 failed, 5 skipped in 20.00s\n"
        stderr = ""

    monkeypatch.setattr(mod.subprocess, "run", lambda *args, **kwargs: FakeCompletedProcess())

    ok, stats = mod.check_tests()

    assert ok is False
    assert stats["passed"] == 1048
    assert stats["failed"] == 2
    assert stats["skipped"] == 5


def test_quality_report_run_tests_uses_extended_timeout(monkeypatch):
    mod = _load_module("quality_report_timeout_r107", "scripts/quality_report.py")
    captured = {}

    class FakeCompletedProcess:
        returncode = 0
        stdout = "1 passed in 0.10s\n"
        stderr = ""

    def fake_run(*args, **kwargs):
        captured.update(kwargs)
        return FakeCompletedProcess()

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    mod.run_tests()

    assert captured["timeout"] >= 300


def test_check_coverage_check_tests_uses_extended_timeout(monkeypatch):
    mod = _load_module("check_coverage_timeout_r107", "scripts/check_coverage.py")
    captured = {}

    class FakeCompletedProcess:
        returncode = 0
        stdout = "1 passed in 0.10s\n"
        stderr = ""

    def fake_run(*args, **kwargs):
        captured.update(kwargs)
        return FakeCompletedProcess()

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    mod.check_tests()

    assert captured["timeout"] >= 300
