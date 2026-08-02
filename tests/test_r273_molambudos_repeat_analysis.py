from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"
REPORT_DIR = PROJECT / "relatorios"
JSON_REPORT = REPORT_DIR / "molambudos_repeat_analysis_R273.json"
MD_REPORT = REPORT_DIR / "molambudos_repeat_analysis_R273.md"

EXPECTED_LENSES = {
    "narratologia",
    "estilo_voz",
    "personagens",
    "simbologia",
    "etica_trauma",
    "inovacao_editorial",
    "pesquisa_literaria",
}


def test_r273_reports_exist_and_are_non_empty():
    assert JSON_REPORT.exists(), "Relatório JSON R273 não foi gerado."
    assert MD_REPORT.exists(), "Relatório Markdown R273 não foi gerado."
    assert JSON_REPORT.stat().st_size > 7_000
    assert MD_REPORT.stat().st_size > 6_000


def test_r273_json_contract_and_corpus_inheritance():
    data = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
    assert data["spec_id"] == "SPEC-935-R273"
    assert data["source_specs"] == ["SPEC-935-R270", "SPEC-935-R271", "SPEC-935-R272"]
    assert data["corpus"]["fragment_units_total"] == 73
    assert data["corpus"]["words"] == 45601
    assert data["corpus"]["characters"] == 272314
    assert "anti-overclaim" in data["anti_overclaim_guard"].lower()
    assert "heurístic" in data["score_interpretation"].lower()


def test_r273_agent_runtime_status_is_explicit():
    data = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
    status = data["agent_runtime_status"]
    assert "current_session" in status
    assert "literary_agents_returned_content" in status
    assert "fallback_used" in status
    if status["fallback_used"]:
        assert "não é parecer multiagente independente" in status["disclaimer"].lower()


def test_r273_lenses_have_required_contract_fields():
    data = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
    lenses = data["repeat_analysis_lenses"]
    assert set(lenses) >= EXPECTED_LENSES
    for lens_id in EXPECTED_LENSES:
        lens = lenses[lens_id]
        for key in ("veredito", "strengths", "risks", "recommendations", "safe_claim", "limites"):
            assert key in lens, f"Campo ausente em {lens_id}: {key}"
        assert len(lens["strengths"]) >= 2
        assert len(lens["risks"]) >= 1
        assert len(lens["recommendations"]) >= 1
        assert "não" in lens["safe_claim"].lower() or "heurístic" in lens["safe_claim"].lower()


def test_r273_markdown_sections_and_safe_language():
    text = MD_REPORT.read_text(encoding="utf-8")
    required = [
        "Síntese reavaliada",
        "Status dos agentes literários",
        "Leitura segura dos scores",
        "Narratologia",
        "Estilo e voz",
        "Personagens",
        "Simbologia",
        "Ética e trauma",
        "Inovação editorial",
        "Pesquisa literária",
        "Prioridades editoriais",
        "Guarda anti-overclaim",
    ]
    for item in required:
        assert item in text
    for unsafe in ["obra-prima comprovada", "validada internacionalmente", "excelência objetiva"]:
        assert unsafe not in text.lower()
