# -*- coding: utf-8 -*-

from __future__ import annotations

import json
from pathlib import Path


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_required(schema: dict, payload: dict):
    for key in schema.get("required", []):
        assert key in payload, f"campo obrigatório ausente: {key}"


def test_fixture_directories_exist():
    for rel in [
        "tests/fixtures/problems",
        "tests/fixtures/oqs_candidates",
        "tests/fixtures/vsee_routes",
        "tests/fixtures/egs_cases",
        "tests/fixtures/pipeline",
    ]:
        path = Path(rel)
        assert path.exists() and path.is_dir(), rel
        assert list(path.glob("*.json")), f"sem fixtures json em {rel}"


def test_optimal_question_contract_fixture_matches_schema():
    schema = _load_json(Path("schemas/optimal_question.schema.json"))
    payload = _load_json(Path("tests/fixtures/oqs_candidates/optimal_question_result.json"))

    _assert_required(schema, payload)
    assert set(schema["properties"]["scores"]["required"]) <= set(payload["scores"].keys())
    assert 0 <= payload["scores"]["URS"] <= 1
    assert 0 <= payload["scores"]["SVS"] <= 1


def test_vector_execution_decision_fixture_matches_schema():
    schema = _load_json(Path("schemas/vector_execution_decision.schema.json"))
    payload = _load_json(Path("tests/fixtures/vsee_routes/vector_execution_decision.json"))

    _assert_required(schema, payload)
    assert payload["chosen_path"] in schema["properties"]["chosen_path"]["enum"]
    assert set(schema["properties"]["telemetry"]["required"]) <= set(payload["telemetry"].keys())


def test_ethical_assessment_fixture_matches_schema():
    schema = _load_json(Path("schemas/ethical_assessment.schema.json"))
    payload = _load_json(Path("tests/fixtures/egs_cases/ethical_assessment.json"))

    _assert_required(schema, payload)
    assert payload["decision"] in schema["properties"]["decision"]["enum"]
    assert 0 <= payload["alignment_score"] <= 1


def test_pipeline_fixture_references_core_stages():
    payload = _load_json(Path("tests/fixtures/pipeline/full_pipeline_case.json"))
    assert payload["stages"] == ["oqs", "scientific_core", "vsee", "egs"]
