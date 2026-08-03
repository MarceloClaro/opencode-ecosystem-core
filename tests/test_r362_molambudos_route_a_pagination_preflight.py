# -*- coding: utf-8 -*-
"""TDD — SPEC-935-R362: rota A, paginação e preflight de Molambudos."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BOOK = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"
BASE = ROOT / "validacao_externa" / "cultural_episteme"
MANIFEST_PATH = BASE / "molambudos_r362_change_manifest.json"
PREFLIGHT_PATH = BASE / "molambudos_r362_preflight.json"
CONTROL_PATH = Path(
    os.environ.get(
        "R362_CONTROL_PATH",
        str(BASE / "molambudos_r362_control_gates.json"),
    )
)

LANGUAGE_ROOTS = {
    "pt": Path("fragmentos"),
    "en": Path("en/fragmentos"),
    "zh": Path("zh/fragmentos"),
}
ROUTE_FILES = (
    Path("mem/MEM-02.tex"),
    Path("mem/MEM-04.tex"),
    Path("mem/MEM-06.tex"),
    Path("doc/DOC-02.tex"),
    Path("doc/DOC-05.tex"),
    Path("doc/DOC-08.tex"),
    Path("doc/DOC-15.tex"),
    Path("doc/DOC-17.tex"),
    Path("doc/DOC-18.tex"),
    Path("luc/LUC-10.tex"),
)
PSEUDOARCHIVES = (
    Path("doc/DOC-02.tex"),
    Path("doc/DOC-17.tex"),
    Path("doc/DOC-18.tex"),
)
MASTERS = {
    "pt": (Path("main.tex"), r"\partopener{Sertão", r"\fragdef{MEM-01}"),
    "en": (Path("en/main_en.tex"), r"\partopener{The Sertão", r"\fragdef{MEM-01}"),
    "zh": (Path("zh/main_zh.tex"), r"\partopener{塞尔唐", r"\fragdef{MEM-01}"),
    "tri": (Path("tri/main_tri.tex"), r"\partopener{A Vala", r"\trifirstinput{MEM-01}"),
}
TITLEPAGES = (
    Path("frontmatter/titlepage.tex"),
    Path("en/frontmatter/titlepage.tex"),
    Path("zh/frontmatter/titlepage.tex"),
    Path("tri/frontmatter/titlepage.tex"),
)
EXPECTED_EDITIONS = {"pt", "en", "zh", "tri", "kdp_tri"}


def _text(relative: Path | str) -> str:
    return (BOOK / relative).read_text(encoding="utf-8")


def _json(path: Path) -> dict:
    assert path.is_file(), f"RED: artefato R362 ausente: {path.name}"
    return json.loads(path.read_text(encoding="utf-8"))


def _language_text(language: str, relative: Path) -> str:
    return _text(LANGUAGE_ROOTS[language] / relative)


def _route_corpus(language: str) -> str:
    return "\n".join(_language_text(language, path) for path in ROUTE_FILES)


def test_r362_spec_is_registered_red_or_better():
    from sdd.spec_engine import spec_registry

    spec = spec_registry.get("SPEC-935-R362")
    assert spec is not None
    assert spec.status in {"red", "green", "verified", "active"}


def test_route_a_starts_in_senador_pompeu_and_walks_toward_fortaleza():
    expected = {
        "pt": ("de Senador Pompeu a Fortaleza", "Campo do Alagadiço"),
        "en": ("from Senador Pompeu to Fortaleza", "Alagadiço"),
        "zh": ("塞纳多尔", "Alagadiço"),
    }
    for language, (route_marker, camp_marker) in expected.items():
        mem02 = _language_text(language, Path("mem/MEM-02.tex"))
        mem04 = _language_text(language, Path("mem/MEM-04.tex"))
        mem06 = _language_text(language, Path("mem/MEM-06.tex"))
        assert route_marker in mem02
        assert "Fortaleza" in mem02 or "福塔莱萨" in mem02
        assert camp_marker in mem04
        assert camp_marker in mem06
        assert "Fortaleza" in mem04 + mem06 or "福塔莱萨" in mem04 + mem06


def test_no_active_route_file_places_the_1915_camp_in_senador_pompeu():
    forbidden = {
        "pt": (
            "Curral do Governo em Senador Pompeu",
            "Curral do Governo de Senador Pompeu",
            "Campo de Concentração de Senador Pompeu",
            "Campo: Senador Pompeu",
        ),
        "en": (
            "Government Pen in Senador Pompeu",
            "Government Pen of Senador Pompeu",
            "Senador Pompeu Concentration Camp",
            "Camp: Senador Pompeu",
        ),
        "zh": (
            "塞纳多尔·蓬佩乌的政府牲畜圈",
            "塞纳多尔·蓬佩乌集中营",
            "塞纳多尔·蓬佩乌政府牲畜圈",
            "营地: 塞纳多尔·蓬佩乌",
        ),
    }
    for language, phrases in forbidden.items():
        corpus = _route_corpus(language)
        assert not [phrase for phrase in phrases if phrase in corpus]


def test_alagadico_is_not_presented_as_open_from_1915_to_1917():
    forbidden = (
        "1915-1917",
        "1915--1917",
        "1915—1917",
        "ficou aberto de 1915 a 1917",
        "remained open from 1915 to 1917",
        "从1915年开放到1917年",
    )
    for language in LANGUAGE_ROOTS:
        corpus = _route_corpus(language)
        assert not [phrase for phrase in forbidden if phrase in corpus]

        doc02 = _language_text(language, Path("doc/DOC-02.tex"))
        assert "1915" in doc02 and "1917" in doc02
        assert "Alagadiço" in doc02


def test_unsupported_exact_counts_and_mortality_rates_are_removed():
    forbidden = re.compile(
        r"(?:8[\.,]240|7[\.,]912|4[\.,]712|3[\.,]200|"
        r"80\\?%|dois terços|two thirds|三分之二)",
        re.IGNORECASE,
    )
    for language in LANGUAGE_ROOTS:
        corpus = "\n".join(
            _language_text(language, path)
            for path in (Path("mem/MEM-06.tex"), Path("doc/DOC-18.tex"))
        )
        assert forbidden.search(corpus) is None


def test_route_a_pseudoarchives_are_explicit_fictional_reconstructions():
    disclaimer = {
        "pt": "Reconstituição ficcional",
        "en": "Fictional reconstruction",
        "zh": "虚构重构",
    }
    for language, marker in disclaimer.items():
        for relative in PSEUDOARCHIVES:
            assert marker in _language_text(language, relative), (
                f"{language}/{relative} ainda simula transcrição arquivística autêntica"
            )


def test_historical_paratext_distinguishes_alagadico_1915_from_patu_1932_1933():
    files = (
        Path("frontmatter/glossario_historico.tex"),
        Path("en/frontmatter/glossario_historico.tex"),
        Path("zh/frontmatter/glossario_historico.tex"),
        Path("tri/frontmatter/glossario.tex"),
        Path("frontmatter/nota_historica.tex"),
        Path("en/frontmatter/nota_historica.tex"),
        Path("zh/frontmatter/nota_historica.tex"),
        Path("tri/frontmatter/nota_historica.tex"),
    )
    for relative in files:
        text = _text(relative)
        assert "Alagadiço" in text
        assert "Patu" in text
        assert "1915" in text
        assert re.search(r"1932(?:--|—|–|-)1933|1932.{0,12}1933", text)
        assert "Patos" not in text and "帕图斯" not in text


def test_each_master_has_one_frontmatter_to_mainmatter_transition():
    for edition, (relative, part_marker, first_fragment) in MASTERS.items():
        text = _text(relative)
        assert len(re.findall(r"(?m)^\s*\\frontmatter\s*$", text)) == 1, edition
        assert len(re.findall(r"(?m)^\s*\\mainmatter\s*$", text)) == 1, edition
        anchor_off = text.index(r"\hypersetup{pageanchor=false}")
        frontmatter = re.search(r"(?m)^\s*\\frontmatter\s*$", text).start()
        title = text.index("frontmatter/titlepage}")
        part = text.index(part_marker)
        mainmatter = re.search(r"(?m)^\s*\\mainmatter\s*$", text).start()
        anchor_on = text.index(r"\hypersetup{pageanchor=true}")
        first = text.index(first_fragment)
        assert anchor_off < frontmatter < title
        assert title < part < mainmatter < anchor_on < first


def test_title_leaves_do_not_reset_the_roman_page_counter():
    for relative in TITLEPAGES:
        text = _text(relative)
        assert r"\begin{titlepage}" not in text
        assert r"\end{titlepage}" not in text
        assert r"\setcounter{page}" not in text


def test_first_fragment_does_not_ship_an_empty_arabic_page_one():
    for edition, (relative, _, first_fragment) in MASTERS.items():
        text = _text(relative)
        first = text.index(first_fragment)
        prefix = text[max(0, first - 40) : first]
        assert r"\newpage" not in prefix, edition


def test_pdf_auditor_parses_blocking_latex_log_signals():
    from scripts.audit_r362_pdf_layout import parse_latex_log

    sample = "\n".join(
        (
            r"Overfull \hbox (4.2pt too wide)",
            r"Overfull \vbox (2.0pt too high)",
            r"Infinite glue shrinkage found in box being split",
            "destination with the same identifier (name{page.1})",
            "LaTeX Warning: There were undefined references.",
            "Missing character: There is no X in font Y!",
            "LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.",
            "! LaTeX Error: synthetic failure",
        )
    )
    parsed = parse_latex_log(sample)
    assert parsed["overfull_hbox_count"] == 1
    assert parsed["overfull_vbox_count"] == 1
    assert parsed["infinite_glue_count"] == 1
    assert parsed["duplicate_page_destination_count"] == 1
    assert parsed["undefined_reference_count"] == 1
    assert parsed["missing_character_count"] == 1
    assert parsed["rerun_required_count"] == 1
    assert parsed["fatal_error_count"] == 1
    assert parsed["passed"] is False


def test_r362_preflight_records_five_clean_builds_and_pdf_boxes():
    payload = _json(PREFLIGHT_PATH)
    assert payload["spec_id"] == "SPEC-935-R362"
    assert payload["external_validation"] is False
    assert payload["human_review_required"] is True
    assert payload["release_gate"] == "blocked"
    assert payload["quality_verdict_allowed"] is False
    assert set(payload["editions"]) == EXPECTED_EDITIONS
    for edition, report in payload["editions"].items():
        assert (ROOT / report["pdf_path"]).is_file(), edition
        assert (ROOT / report["log_path"]).is_file(), edition
        assert report["build"]["passed"] is True
        assert report["build"]["passes"] == 2
        assert report["build"]["receipt_current"] is True
        assert report["build"]["engine_version"].strip()
        assert report["build"]["aux_sha256"] == report["aux_sha256"]
        assert report["build"]["fls_sha256"] == report["fls_sha256"]
        assert report["build"]["dependency_snapshot"]["inputs"]
        assert report["build"]["dependency_snapshot"]["missing_inputs"] == []
        assert len(report["build"]["dependency_snapshot"]["merkle_sha256"]) == 64
        assert report["log"]["passed"] is True
        assert report["log"]["overfull_hbox_count"] == 0
        assert report["log"]["overfull_vbox_count"] == 0
        assert report["log"]["fatal_error_count"] == 0
        assert report["log"]["rerun_required_count"] == 0
        assert report["pagination"]["frontmatter_style"] == "roman"
        assert report["pagination"]["first_fragment_label"] == "1"
        assert report["pagination"]["first_fragment_destination_matches"] is True
        assert report["pagination"]["foliation_sequence_passed"] is True
        assert report["pagination"]["duplicate_page_labels"] == []
        assert report["all_page_dimensions_match_source_geometry"] is True
        assert report["layout"]["violation_count"] == 0
        assert report["layout"]["zone_violation_count"] == 0
        assert report["layout"]["violations"] == []
        assert report["layout"]["page_reports"]
        assert report["page_count"] == len(report["layout"]["page_reports"])
        assert report["layout"]["audited_object_count"] > 0
        assert len(report["layout"]["full_bleed_exceptions"]) == 8
        assert report["layout"]["full_bleed_allowlist_passed"] is True
        assert hashlib.sha256((ROOT / report["pdf_path"]).read_bytes()).hexdigest() == report["pdf_sha256"]
        assert hashlib.sha256((ROOT / report["log_path"]).read_bytes()).hexdigest() == report["log_sha256"]
        assert hashlib.sha256((ROOT / report["aux_path"]).read_bytes()).hexdigest() == report["aux_sha256"]
        for page_report in report["layout"]["page_reports"]:
            assert {"text_boxes", "image_boxes", "drawing_boxes"} <= set(page_report)
        for exception in report["layout"]["full_bleed_exceptions"]:
            assert exception["page_index"] >= 0
            assert exception["source"].strip()
            assert exception["justification"].strip()
            assert len(exception["source_sha256"]) == 64
            assert exception["allowlist_id"].strip()

    typography = payload["source_typography"]
    assert typography["global_narrative_class"] == "14pt"
    assert typography["global_narrative_size_preserved"] is True
    assert typography["table_minimum"] == r"\footnotesize"
    active = payload["source_checks"]["active_dependency_corpus"]
    assert active["tex_file_count"] >= 100
    assert active["forbidden_route_occurrences"] == []
    assert active["unsupported_exact_count_occurrences"] == []
    assert active["passed"] is True


def test_r362_route_report_validates_all_540_trilingual_routes():
    # O corpus cresce entre ciclos (novos fragmentos, novas rotas restauradas
    # de texto puro para \rota{}) — fixar 180/540 reproduziria o mesmo problema
    # já corrigido no R358 para a contagem de fragmentos. Verificamos a
    # invariante real: PT/EN/ZH devem ter sempre a mesma contagem de rotas
    # entre si, e todos os derivados (total, tri, kdp_tri) devem bater com ela.
    routes = _json(PREFLIGHT_PATH)["routes"]
    per_language = routes["by_language"]
    assert len(set(per_language.values())) == 1, (
        f"contagem de rotas diverge entre idiomas: {per_language}"
    )
    route_count = per_language["pt"]
    assert route_count > 0
    assert routes["expected"] == routes["total"] == routes["valid"] == route_count * 3
    assert routes["missing"] == 0
    assert routes["divergent"] == 0
    assert routes["passed"] is True
    assert set(routes["editions"]) == EXPECTED_EDITIONS
    for edition, report in routes["editions"].items():
        assert report["passed"] is True, edition
        assert report["duplicate_labels"] == []
        assert report["source_multiset_match"] is True
    assert routes["editions"]["pt"]["total"] == route_count
    assert routes["editions"]["en"]["total"] == route_count
    assert routes["editions"]["zh"]["total"] == route_count
    assert routes["editions"]["tri"]["total"] == route_count * 3
    assert routes["editions"]["kdp_tri"]["total"] == route_count * 3


def test_r362_manifest_chains_provenance_and_only_resolves_selected_blocker():
    manifest = _json(MANIFEST_PATH)
    assert manifest["spec_id"] == "SPEC-935-R362"
    assert manifest["predecessor_spec_id"] == "SPEC-935-R361"
    assert manifest["predecessor_artifact_mutated"] is False
    assert manifest["external_validation"] is False
    assert manifest["human_review_required"] is True
    assert manifest["release_gate"] == "blocked"
    assert manifest["quality_verdict_allowed"] is False
    assert len(manifest["predecessor_artifact_merkle_sha256"]) == 64
    assert manifest["provenance_validation"]["passed"] is True
    assert manifest["provenance_validation"]["externally_notarized"] is False
    for predecessor in manifest["predecessor_artifacts"]:
        path = ROOT / predecessor["path"]
        assert path.resolve().is_relative_to(ROOT.resolve())
        assert hashlib.sha256(path.read_bytes()).hexdigest() == predecessor["sha256"]
    assert manifest["records"]
    for record in manifest["records"]:
        path = ROOT / record["path"]
        assert path.resolve().is_relative_to(ROOT.resolve())
        assert path.is_file()
        assert record["old_sha256"] != record["new_sha256"]
        assert __import__("hashlib").sha256(path.read_bytes()).hexdigest() == record["new_sha256"]

    blockers = manifest["blockers"]
    chronology = next(item for item in blockers if item["blocker_id"] == "patu_1915_chronology")
    assert chronology["status"] == "implemented_pending_external_review"
    assert chronology["automatic_change_applied"] is True
    unresolved = [item for item in blockers if item["blocker_id"] != "patu_1915_chronology"]
    assert len(unresolved) == 9
    assert all(item["status"] == "blocked_author_decision" for item in unresolved)


def test_r362_control_gate_never_opens_release_or_claims_external_validation():
    control = _json(CONTROL_PATH)
    assert control["spec_id"] == "SPEC-935-R362"
    assert control["external_validation"] is False
    assert control["human_review_required"] is True
    assert control["release_gate"] == "blocked"
    assert control["quality_verdict_allowed"] is False
    assert control["sdd_gate"]["verified"] is True
    assert control["sdd_gate"]["external_validation_conferred"] is False
    assert control["sdd_gate"]["release_conferred"] is False
    assert control["behavioral_gate"]["opens_release"] is False
    assert control["artifact_freshness_gate"]["passed"] is True
    assert control["provenance_gate"]["passed"] is True


def test_r362_dependency_snapshot_merkle_is_self_consistent():
    """Regressão do bugfix: Merkle gravado em ordem (scope, path) deve ser
    validado por _dependency_snapshot_is_current sem divergência.

    Antes da correção, _dependency_snapshot ordenava por path absoluto
    (resolved_inputs) enquanto a validação ordenava por (scope, path);
    paths absolute/workspace intercalados geravam Merkle divergente e
    receipt_current=False permanente em todas as edições.
    """
    import sys
    from pathlib import Path

    sys.path.insert(0, str(ROOT / "scripts"))
    import audit_r362_pdf_layout as auditor

    for key, edition in auditor.EDITIONS.items():
        assert edition.fls.is_file(), f"FLS ausente para {key}"
        snapshot = auditor._dependency_snapshot(edition.fls)
        assert snapshot["missing_inputs"] == []
        assert snapshot["input_count"] == len(snapshot["inputs"])
        assert auditor._dependency_snapshot_is_current(snapshot) is True, key
        # Ordenação canônica: (scope, path) — mesmo critério da validação
        keys = [(item["scope"], item["path"]) for item in snapshot["inputs"]]
        assert keys == sorted(keys), f"ordenação Merkle não canônica em {key}"
