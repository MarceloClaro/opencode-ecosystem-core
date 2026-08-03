from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"
REPORT_DIR = PROJECT / "_archive" / "relatorios"
JSON_REPORT = REPORT_DIR / "molambudos_full_literary_scan_R270.json"
MD_REPORT = REPORT_DIR / "molambudos_full_literary_scan_R270.md"
TXT_CORPUS = REPORT_DIR / "molambudos_full_corpus_R270.txt"


def test_r270_reports_exist_and_are_non_empty():
    assert JSON_REPORT.exists(), "Relatório JSON R270 não foi gerado."
    assert MD_REPORT.exists(), "Relatório Markdown R270 não foi gerado."
    assert TXT_CORPUS.exists(), "Corpus textual auditável R270 não foi gerado."
    assert JSON_REPORT.stat().st_size > 5_000
    assert MD_REPORT.stat().st_size > 2_000
    assert TXT_CORPUS.stat().st_size > 50_000


def test_r270_json_schema_and_corpus_coverage():
    data = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
    assert data["spec_id"] == "SPEC-935-R270"
    corpus = data["corpus"]
    assert corpus["source_project"].endswith("Molambudos_VictoriaRegia")
    assert corpus["characters"] > 50_000
    assert corpus["words"] > 8_000
    assert corpus["fragment_counts"] == {
        "MEM": 26,
        "DOC": 27,
        "LUC": 14,
        "CONT": 5,
        "Epilogo": 1,
    }
    assert corpus["fragment_units_total"] == 73


def test_r270_scanner_contracts_and_overclaim_guards():
    data = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
    literary = data["literary"]
    research = data["literary_research"]

    assert literary["domain"] == "literary"
    assert literary["scanner_count"] == 8
    assert isinstance(literary["literary_excellence_score"], (int, float))
    assert "não substitui" in literary["overclaim_guard"].lower()

    assert research["domain"] == "literary_research"
    assert research["scanner_count"] == 4
    assert isinstance(research["international_research_rigor_score"], (int, float))
    assert "não substitui" in research["overclaim_guard"].lower()


def test_r270_markdown_has_interpretive_sections():
    text = MD_REPORT.read_text(encoding="utf-8")
    required = [
        "Síntese executiva",
        "Tabela de scores",
        "Forças principais",
        "Lacunas e riscos",
        "Recomendações",
        "Limitações",
        "anti-overclaim",
    ]
    for item in required:
        assert item in text
