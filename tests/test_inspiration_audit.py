# -*- coding: utf-8 -*-

import os
import sys
import tempfile

os.environ["MCI_STATE_DIR"] = tempfile.mkdtemp(prefix="mci_inspiration_audit_")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _item(report, item_id: str):
    return next(i for i in report["items"] if i["item_id"] == item_id)


def test_audit_inspirations_returns_canonical_items():
    from marceloclaro.inspiration_audit import audit_inspirations

    report = audit_inspirations()

    assert report["summary"]["total_items"] >= 8
    item_ids = {i["item_id"] for i in report["items"]}
    assert {
        "superhuman_scientific_core",
        "scientific_governance_pipeline_architecture",
        "scientific_governance_tdd_plan",
        "research_run_batch",
        "research_analyze_batch",
        "research_final_report_template",
        "research_scenario_matrix",
        "mira_presentation_system",
    } <= item_ids


def test_scientific_governance_pipeline_architecture_is_implemented():
    from marceloclaro.inspiration_audit import audit_inspirations

    report = audit_inspirations()
    item = _item(report, "scientific_governance_pipeline_architecture")

    assert item["status"] == "implemented"
    assert item["mandatory_coverage_pct"] == 100


def test_research_run_batch_is_implemented():
    from marceloclaro.inspiration_audit import audit_inspirations

    report = audit_inspirations()
    item = _item(report, "research_run_batch")

    assert item["status"] == "implemented"
    assert any(path.endswith("research/pipelines/run_research_batch.py") for path in item["evidence_paths"])


def test_research_analyze_batch_is_implemented():
    from marceloclaro.inspiration_audit import audit_inspirations

    report = audit_inspirations()
    item = _item(report, "research_analyze_batch")

    assert item["status"] == "implemented"
    assert item["mandatory_coverage_pct"] == 100


def test_research_final_report_template_is_implemented():
    from marceloclaro.inspiration_audit import audit_inspirations

    report = audit_inspirations()
    item = _item(report, "research_final_report_template")

    assert item["status"] == "implemented"
    assert item["evidence_paths"]
    assert item["missing_paths"] == []


def test_mira_presentation_system_is_partial():
    from marceloclaro.inspiration_audit import audit_inspirations

    report = audit_inspirations()
    item = _item(report, "mira_presentation_system")

    assert item["status"] == "partial"
    assert any(path.endswith("illustrations/mira_engine.py") for path in item["evidence_paths"])
    assert any("mira-" in path for path in item["missing_paths"])


def test_markdown_report_contains_summary_and_statuses():
    from marceloclaro.inspiration_audit import audit_inspirations, render_inspiration_audit_markdown

    report = audit_inspirations()
    md = render_inspiration_audit_markdown(report)

    assert "# Auditoria de Inspirações" in md
    assert "scientific_governance_pipeline_architecture" in md
    assert "research_analyze_batch" in md
    assert "implemented" in md
    assert "partial" in md
    assert "absent" in md


def test_orchestrator_audit_inspirations_records_reflection():
    from mci.metabus import metabus
    from marceloclaro.orchestrator import MarceloClaroOrchestrator

    before = len(metabus.memory.episodic)
    orch = MarceloClaroOrchestrator(auto_load_agents=False)
    report = orch.audit_inspirations()

    assert report["summary"]["total_items"] >= 8
    assert len(metabus.memory.episodic) > before
