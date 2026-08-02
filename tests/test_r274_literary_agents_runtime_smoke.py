from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia" / "relatorios"
JSON_REPORT = REPORT_DIR / "literary_agents_runtime_smoke_R274.json"
MD_REPORT = REPORT_DIR / "literary_agents_runtime_smoke_R274.md"

EXPECTED_AGENTS = {
    "literary-orchestrator-phd",
    "literary-narratology-architect-phd",
    "literary-style-voice-phd",
    "literary-character-psychology-phd",
    "literary-symbolic-imagery-phd",
    "literary-ethics-trauma-phd",
    "literary-innovation-editorial-phd",
    "literary-research-scholar-phd",
}


def test_r274_reports_exist_and_are_non_empty():
    assert JSON_REPORT.exists(), "Relatório JSON R274 não foi gerado."
    assert MD_REPORT.exists(), "Relatório Markdown R274 não foi gerado."
    assert JSON_REPORT.stat().st_size > 3_000
    assert MD_REPORT.stat().st_size > 2_000


def test_r274_json_contract():
    data = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
    assert data["spec_id"] == "SPEC-935-R274"
    assert set(data["agent_results"]) == EXPECTED_AGENTS
    assert "anti-overclaim" in data["anti_overclaim_guard"].lower()
    for agent_id, result in data["agent_results"].items():
        assert isinstance(result["returned_content"], bool), agent_id
        assert isinstance(result["content_length"], int), agent_id
        assert isinstance(result["has_required_contract_fields"], bool), agent_id
        assert "summary" in result


def test_r274_resolution_status_explicit():
    data = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
    assert "resolved_after_restart" in data
    assert "non_empty_count" in data
    assert "empty_agents" in data
    assert data["non_empty_count"] + len(data["empty_agents"]) == 8
    if data["resolved_after_restart"]:
        assert data["non_empty_count"] == 8
    else:
        assert len(data["empty_agents"]) >= 1
        assert data["recommended_remediation"]


def test_r274_markdown_safe_language():
    text = MD_REPORT.read_text(encoding="utf-8")
    for section in ["Resultado pós-reinício", "Tabela de smoke tests", "Guarda anti-overclaim"]:
        assert section in text
    for unsafe in ["obra-prima comprovada", "validada internacionalmente", "excelência objetiva"]:
        assert unsafe not in text.lower()
