# -*- coding: utf-8 -*-
"""Testes do landscape-curator (R482) — curadoria da paisagem externa.

Hermético: sem rede, sem credenciais, sem código de terceiros. Valida que o
manifest curado dos 20 agentes auto-contidos da coleção 500-AI-Agents-Projects
é íntegro e que o cruzamento com o catálogo do Core produz sugestões honestas.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from landscape.curator import LandscapeCurator

ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def curator() -> LandscapeCurator:
    return LandscapeCurator(repo_root=str(ROOT))


def _manifest(curator: LandscapeCurator) -> dict:
    return json.loads(
        (ROOT / "landscape" / "manifest.json").read_text(encoding="utf-8")
    )


def test_manifest_has_20_curated_agents(curator):
    manifest = _manifest(curator)
    agents = manifest["agents"]
    assert len(agents) == 20
    assert manifest["license"] == "MIT"
    assert manifest["source_repo"].startswith("https://github.com/MarceloClaro/")


def test_manifest_fields_complete(curator):
    required = {"id", "title", "industry", "framework", "dependencies",
                "env_required", "swift", "reference_url", "license"}
    for agent in _manifest(curator)["agents"]:
        assert required <= set(agent), agent["id"]
        assert agent["license"] == "MIT"
        assert agent["reference_url"].startswith(
            "https://github.com/MarceloClaro/500-AI-Agents-Projects/tree/main/agents/"
        )


def test_manifest_scope_note_honest(curator):
    """Não promete '500 integrados'; manifest cobre os 20 auto-contidos."""
    note = _manifest(curator)["scope_note"].lower()
    assert "auto-contidos" in note
    assert "não são integrações" in note


def test_catalog_cards_loaded(curator):
    assert len(curator.agent_cards) >= 100
    sample = curator.agent_cards[0]
    assert {"name", "description", "tags"} <= set(sample)


def test_every_use_case_has_suggestions_or_is_declared_unmatched(curator):
    report = curator.build_report()
    for entry in report["cases"]:
        has_suggestion = len(entry["suggestions"]) > 0
        declared_unmatched = entry["case_id"] in {
            item["case_id"] for item in report["unmatched"]
        }
        assert has_suggestion or declared_unmatched, entry["case_id"]


def test_web_research_maps_to_researcher_family(curator):
    report = curator.build_report()
    case = next(c for c in report["cases"] if c["case_id"].startswith("01-"))
    names = " ".join(s["core_agent"] for s in case["suggestions"]).lower()
    assert any(k in names for k in ("web-search-researcher", "researcher", "explore"))


def test_code_review_maps_to_reviewer_family(curator):
    report = curator.build_report()
    case = next(c for c in report["cases"] if c["case_id"].startswith("02-"))
    names = " ".join(s["core_agent"] for s in case["suggestions"]).lower()
    assert any(k in names for k in ("code-reviewer", "reviewer", "security-auditor"))


def test_report_counters(curator):
    report = curator.build_report()
    assert report["counters"]["external_cases"] == 20
    assert report["counters"]["catalog_cards"] >= 100
    assert report["counters"]["matched"] + len(report["unmatched"]) == 20
    assert report["license"] == "MIT"
    assert "timestamp_utc" in report


def test_report_is_markdown_and_json_sane(curator):
    json_report = curator.build_report()
    md_report = curator.render_markdown(json_report)
    assert md_report.startswith("# Paisagem de agentes")
    assert "500-AI-Agents-Projects" in md_report
    assert "não constitui certificação externa" in md_report.lower()


def test_no_third_party_code_copied(curator):
    """Sanidade: relatório e manifest não carregam código fonte externo."""
    report_json = json.dumps(curator.build_report(), ensure_ascii=False).lower()
    assert "import openai" not in report_json
    assert "def " not in report_json
    assert "api_key" not in report_json.lower()


def test_anti_overclaim_terms_absent(curator):
    report = json.dumps(curator.build_report(), ensure_ascii=False).lower()
    for word in ("superhuman", "qualis a1", "verificado", "superação"):
        assert word not in report


def test_write_report_files(curator, tmp_path):
    out = tmp_path / "landscape_report.md"
    out.write_text(curator.render_markdown(curator.build_report()),
                   encoding="utf-8")
    assert out.stat().st_size > 500