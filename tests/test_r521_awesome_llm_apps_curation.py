# -*- coding: utf-8 -*-
"""Testes da curadoria awesome-llm-apps (R521) — extensão multi-coleção.

Valida que o manifest curado dos 15 templates representativos do repositório
MarceloClaro/awesome-llm-apps (Apache-2.0) é íntegro, que o cruzamento com o
catálogo do Core é honesto (sugestão ou unmatched, nunca inventado), e que a
extensão multi-coleção do landscape-curator NÃO quebra a regressão da R482.

Hermético: sem rede, sem credenciais, sem código de terceiros.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from landscape.curator import LandscapeCurator

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST_AWESOME = ROOT / "landscape" / "manifest_awesome_llm_apps.json"


@pytest.fixture(scope="module")
def curator_awesome() -> LandscapeCurator:
    return LandscapeCurator(repo_root=str(ROOT), manifest_path=str(MANIFEST_AWESOME))


@pytest.fixture(scope="module")
def curator_default() -> LandscapeCurator:
    return LandscapeCurator(repo_root=str(ROOT))


def _manifest() -> dict:
    return json.loads(MANIFEST_AWESOME.read_text(encoding="utf-8"))


# ---------- manifest ----------

def test_manifest_has_15_curated_templates(curator_awesome):
    manifest = _manifest()
    agents = manifest["agents"]
    assert len(agents) == 15
    assert manifest["license"] == "Apache-2.0"
    assert manifest["source_repo"] == (
        "https://github.com/MarceloClaro/awesome-llm-apps"
    )
    assert manifest["upstream"] == "Shubhamsaboo/awesome-llm-apps"


def test_manifest_fields_complete(curator_awesome):
    required = {"id", "title", "category", "industry", "framework",
                "license", "reference_url", "keywords", "note"}
    for agent in _manifest()["agents"]:
        assert required <= set(agent), agent["id"]
        assert agent["license"] == "Apache-2.0"
        assert agent["reference_url"].startswith(
            "https://github.com/MarceloClaro/awesome-llm-apps/tree/main/"
        )
        assert isinstance(agent["keywords"], list) and agent["keywords"]


def test_manifest_scope_note_honest(curator_awesome):
    """Não promete '100+ integrados'; manifest cobre 15 representativos."""
    note = _manifest()["scope_note"].lower()
    assert "15" in note
    assert "100+" in note
    assert "não" in note and "integração" in note


def test_manifest_adversarial_meta_loop_flagged(curator_awesome):
    """Entrada meta-loop (modelos não validados do upstream) tem nota de risco."""
    manifest = _manifest()
    labels = [a["id"] for a in manifest["agents"]]
    assert "advisor-orchestrator-worker" in labels
    entry = next(a for a in manifest["agents"]
                 if a["id"] == "advisor-orchestrator-worker")
    note = entry["note"].lower()
    assert "não" in note and ("validad" in note or "adotar" in note)


# ---------- cruzamento ----------

def test_every_case_has_suggestions_or_is_declared_unmatched(curator_awesome):
    report = curator_awesome.build_report()
    unmatched_ids = {item["case_id"] for item in report["unmatched"]}
    for entry in report["cases"]:
        has_suggestion = len(entry["suggestions"]) > 0
        assert has_suggestion or entry["case_id"] in unmatched_ids, entry["case_id"]


def test_adversarial_has_no_suggestions_and_in_observatory(curator_awesome):
    """Meta-loop (modelos não validados) NÃO sugere agentes core; vai ao observatório."""
    report = curator_awesome.build_report()
    case = next(c for c in report["cases"]
                if c["case_id"] == "advisor-orchestrator-worker")
    assert case["suggestions"] == []
    assert case["verdict"] == "não-adotar/observar"
    obs_ids = {o["case_id"] for o in report["observatory"]}
    assert "advisor-orchestrator-worker" in obs_ids


def test_report_markdown_includes_observatory(curator_awesome):
    md_report = curator_awesome.render_markdown(curator_awesome.build_report())
    assert "Observatório" in md_report
    assert "não-adotar/observar" in md_report


def test_report_counters(curator_awesome):
    report = curator_awesome.build_report()
    assert report["collection"] == "awesome-llm-apps"
    assert report["counters"]["external_cases"] == 15
    assert report["counters"]["catalog_cards"] >= 100
    assert report["counters"]["matched"] + len(report["unmatched"]) == 15
    assert report["license"] == "Apache-2.0"
    assert "timestamp_utc" in report


def test_corrective_rag_maps_to_rag_affinity(curator_awesome):
    """O caso CRAG deve ter afinidade com agentes/skills de RAG do Core."""
    report = curator_awesome.build_report()
    case = next(c for c in report["cases"] if c["case_id"].startswith("rag-corrective"))
    names = " ".join(s["core_agent"] for s in case["suggestions"]).lower()
    assert "rag" in names


# ---------- relatório ----------

def test_report_is_markdown_and_json_sane(curator_awesome):
    json_report = curator_awesome.build_report()
    md_report = curator_awesome.render_markdown(json_report)
    assert md_report.startswith("# Paisagem de agentes")
    assert "awesome-llm-apps" in md_report
    assert "Apachev" not in md_report  # licença sem erro de digitação
    assert "Apache-2.0" in md_report
    assert "não constitui certificação externa" in md_report.lower()


def test_no_third_party_code_copied(curator_awesome):
    report_json = json.dumps(curator_awesome.build_report(), ensure_ascii=False).lower()
    assert "import openai" not in report_json
    assert "def " not in report_json
    assert "api_key" not in report_json.lower()


def test_anti_overclaim_terms_absent(curator_awesome):
    report = json.dumps(curator_awesome.build_report(), ensure_ascii=False).lower()
    for word in ("superhuman", "qualis a1", "verificado", "superação"):
        assert word not in report


# ---------- regressão R482 (multi-coleção não quebra o default) ----------

def test_default_manifest_still_20_agents(curator_default):
    """O manifest default da R482 continua íntegro (regressão)."""
    report = curator_default.build_report()
    assert report["collection"] == "500-AI-Agents-Projects"
    assert report["counters"]["external_cases"] == 20
    assert report["license"] == "MIT"


def test_default_render_title_unchanged(curator_default):
    md_report = curator_default.render_markdown(curator_default.build_report())
    assert md_report.startswith("# Paisagem de agentes")
    assert "500-AI-Agents-Projects" in md_report


def test_write_report_custom_filename(curator_awesome, tmp_path):
    out = curator_awesome.write_report(
        out_dir=str(tmp_path),
        filename="LANDSCAPE_REPORT_AWESOME_LLM_APPS.md",
    )
    assert out.exists()
    assert out.stat().st_size > 500
    text = out.read_text(encoding="utf-8")
    assert "awesome-llm-apps" in text