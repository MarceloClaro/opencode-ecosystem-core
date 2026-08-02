from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"
REPORT_DIR = PROJECT / "relatorios"
JSON_DOSSIER = REPORT_DIR / "molambudos_critical_dossier_R271.json"
MD_DOSSIER = REPORT_DIR / "molambudos_critical_dossier_R271.md"


EXPECTED_LENSES = {
    "narratologia",
    "estilo_voz",
    "personagens",
    "simbologia",
    "etica_trauma",
    "inovacao_editorial",
    "pesquisa_literaria",
}


def test_r271_dossier_files_exist_and_are_non_empty():
    assert JSON_DOSSIER.exists(), "Dossiê JSON R271 não foi gerado."
    assert MD_DOSSIER.exists(), "Dossiê Markdown R271 não foi gerado."
    assert JSON_DOSSIER.stat().st_size > 6_000
    assert MD_DOSSIER.stat().st_size > 5_000


def test_r271_json_contract_and_corpus_inheritance():
    data = json.loads(JSON_DOSSIER.read_text(encoding="utf-8"))
    assert data["spec_id"] == "SPEC-935-R271"
    assert data["source_scan_spec_id"] == "SPEC-935-R270"
    assert data["corpus"]["fragment_units_total"] == 73
    assert data["corpus"]["words"] == 45601
    assert data["corpus"]["characters"] == 272314
    assert "anti-overclaim" in data["anti_overclaim_guard"].lower()
    assert "heurístic" in data["score_interpretation"].lower()


def test_r271_lenses_have_required_fields():
    data = json.loads(JSON_DOSSIER.read_text(encoding="utf-8"))
    lenses = data["critical_lenses"]
    assert set(lenses) >= EXPECTED_LENSES
    for lens_id in EXPECTED_LENSES:
        lens = lenses[lens_id]
        for key in ("title", "strengths", "risks", "recommendations", "safe_claim"):
            assert key in lens, f"Campo ausente em {lens_id}: {key}"
        assert len(lens["strengths"]) >= 2
        assert len(lens["risks"]) >= 1
        assert len(lens["recommendations"]) >= 1
        assert "não" in lens["safe_claim"].lower() or "heurístic" in lens["safe_claim"].lower()


def test_r271_markdown_sections_and_safe_language():
    text = MD_DOSSIER.read_text(encoding="utf-8")
    required = [
        "Síntese executiva",
        "Leitura segura dos scores",
        "Narratologia",
        "Estilo e voz",
        "Personagens",
        "Simbologia",
        "Ética e trauma",
        "Inovação editorial",
        "Pesquisa literária",
        "Convergências",
        "Tensões críticas",
        "Próximos passos editoriais",
        "Guarda anti-overclaim",
    ]
    for item in required:
        assert item in text
    unsafe_phrases = ["obra-prima comprovada", "validada internacionalmente", "excelência objetiva"]
    for phrase in unsafe_phrases:
        assert phrase not in text.lower()
