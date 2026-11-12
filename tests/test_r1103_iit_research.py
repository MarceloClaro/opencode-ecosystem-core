"""Contrato documental R1103; não homologa as métricas legadas ou consciência."""
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
DOSSIER = ROOT / "docs/research/iit-autonomia-r1103"


def load(name):
    return json.loads((DOSSIER / name).read_text(encoding="utf-8"))


def validate_sources(sources):
    ids = [item["id"] for item in sources]
    assert len(ids) >= 8 and len(ids) == len(set(ids))
    for item in sources:
        for key in ("title", "authors", "year", "identifier", "url", "read_scope",
                    "locator", "technique", "limit", "publication_status", "receipt"):
            assert item.get(key), (item["id"], key)
        assert item["url"].startswith("https://")
        assert item["status"] == "primary_resolved"
    assert any(s["role"] == "counterevidence" for s in sources)


def test_sources_are_resolved_and_delimited():
    validate_sources(load("sources.json"))


def test_documentary_gate_rejects_unresolved_source():
    sources = load("sources.json")
    sources[0]["status"] = "unresolved"
    with pytest.raises(AssertionError):
        validate_sources(sources)


def test_documentary_gate_rejects_duplicate_source():
    sources = load("sources.json")
    sources.append(sources[0])
    with pytest.raises(AssertionError):
        validate_sources(sources)


def test_gaps_have_local_evidence_and_acceptance_tests():
    source_ids = {s["id"] for s in load("sources.json")}
    gaps = load("gaps.json")
    assert len(gaps) >= 8
    assert len({g["id"] for g in gaps}) == len(gaps)
    for gap in gaps:
        assert (ROOT / gap["path"]).is_file()
        assert gap["locator"] and gap["acceptance_test"] and gap["mitigation"]
        assert gap["status"] in {"reproduced", "inspected"}
        assert gap["implementation"] == "proposed_not_deployed"
        assert set(gap["sources"]) <= source_ids


def test_experiment_uses_independent_outcomes_and_bounded_scope():
    plan = load("experiments.json")
    assert plan["status"] == "proposed_not_run"
    assert plan["synthetic_fallback"] is False
    assert plan["self_rating_promotes_trust"] is False
    assert plan["phenomenal_consciousness_endpoint"] is False
    assert plan["production_permissions_changed"] is False
    assert plan["safe_abstention_penalized"] is False
    assert set(plan["metrics"]) >= {
        "task_correctness", "brier_score", "risk_coverage", "repeated_error_rate",
        "unauthorized_actions", "cost_per_correct_task", "citation_support",
    }
    assert plan["baseline"] and plan["held_out_policy"] and plan["stop_rules"]
    assert plan["promotion_gate"] and plan["ablation_arms"]


def test_audit_has_isolation_receipt_not_performance_claim():
    report = load("audit.json")
    assert report["scope"] == "legacy_counterexamples_not_benchmark"
    assert report["production_unchanged_during_probes"] is True
    assert report["observations"] and report["source_sha256"]
    assert report["state_isolation"]["MCI_STATE_DIR"].startswith("/tmp/opencode/")
    assert report["state_isolation"]["EVOLUTION_STATE_PATH"].startswith("/tmp/opencode/")
    for path, digest in report["source_sha256"].items():
        assert path and len(digest) == 64
    for item in report["observations"]:
        assert item["id"] and item["expected_contract"] and item["observed"]


def test_report_boundaries_and_tool_failures_are_explicit():
    text = (DOSSIER / "README.md").read_text(encoding="utf-8")
    for token in ("IIT 3.0", "IIT 4.0", "Shannon", "autorrelato", "causalidade",
                  "não homologa", "não foi implantada", "pesquisa dirigida"):
        assert token in text
    operations = load("operations.json")
    assert operations["external_review_executed"] is False
    assert any(i["status"] == "blocked" for i in operations["incidents"])
    assert operations["searches"] and operations["exclusions"]
    assert operations["trust_update"] != "promoted"
