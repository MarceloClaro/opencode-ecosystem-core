"""R942: contrato read-only do especialista de matrizes e normas educacionais."""

import json
from pathlib import Path

from agents.lifecycle import AgentLifecycleService, _metadata


ROOT = Path(__file__).resolve().parents[1]
AGENT_ID = "caed-spaece-educacao-ceara"


def _profile_and_prompt():
    path = ROOT / "agents/catalog" / f"{AGENT_ID}.md"
    report = AgentLifecycleService(ROOT).validate(AGENT_ID)
    meta, prompt = _metadata(path.read_bytes())
    return report, meta, prompt.casefold()


def test_profile_is_managed_and_read_only():
    report, meta, _ = _profile_and_prompt()
    assert report["definition_validated"] is True
    assert report["mode"] == "managed-v1"
    assert report["executed"] is False
    assert meta["parent"] == "marceloclaro"
    assert meta["spec_file"] == "specs/SPEC-935-R942-caed-spaece-legislacao-ceara.md"
    assert meta["test_file"] == "tests/test_r942_caed_spaece_educacao_ceara.py"
    assert meta["allow_edit"] is False
    assert {
        "caed_matrix_inventory",
        "spaece_edition_analysis",
        "education_law_versioning",
        "ceara_education_plan",
        "bncc_matrix_crosswalk",
    }.issubset(meta["tags"])
    assert meta["permission"]["edit"] == "deny"
    assert meta["permission"]["webfetch"] == "deny"
    assert meta["permission"]["task"] == "deny"
    assert meta["permission"]["bash"]["*"] == "deny"
    assert meta["tools"]["edit"] is False
    assert meta["tools"]["write"] is False
    assert meta["output_contract"]["required_fields"] == [
        "status", "findings", "evidence", "limitations"
    ]


def test_matrix_scope_requires_full_coverage_inventory_and_gap_reporting():
    _, _, prompt = _profile_and_prompt()
    for phrase in (
        "caed",
        "spaece",
        "todas as edições",
        "anos/séries",
        "componentes",
        "matriz de cobertura",
        "não localizadas",
        "data de corte",
        "bncc",
        "não invente",
        "não declare cobertura integral",
    ):
        assert phrase in prompt, f"regra de cobertura ausente: {phrase}"


def test_legal_scope_versions_sources_and_does_not_assume_current_validity():
    _, _, prompt = _profile_and_prompt()
    for phrase in (
        "lei nº 8.069/1990",
        "lei nº 9.394/1996",
        "lei nº 13.146/2015",
        "lei nº 13.005/2014",
        "lei nº 16.025/2016",
        "2016–2024",
        "fonte oficial",
        "vigência",
        "norma sucessora",
        "vigência não verificada",
        "não substitui orientação jurídica",
    ):
        assert phrase in prompt, f"regra jurídico-documental ausente: {phrase}"


def test_opencode_registers_agent_and_preserves_existing_customization():
    config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    agent = config["agent"][AGENT_ID]
    assert agent["mode"] == "subagent"
    assert agent["prompt"] == "{file:./agents/catalog/caed-spaece-educacao-ceara.md}"
    assert agent["permission"]["edit"] == "deny"
    assert agent["permission"]["webfetch"] == "deny"
    assert agent["permission"]["bash"]["*"] == "deny"
    assert "biblioteca" in config["command"]
