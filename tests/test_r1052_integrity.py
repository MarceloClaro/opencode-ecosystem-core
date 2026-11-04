"""R1052 — integridade de literatura via Crossref, com falha explícita."""
from __future__ import annotations

import json
from pathlib import Path

from scientific_lab import integrity
from scientific_lab.native.common import dump


def message(relation=None, type_="journal-article"):
    return {
        "message": {
            "DOI": "10.1000/a",
            "type": type_,
            "title": ["Estudo A"],
            "relation": relation or {},
        }
    }


def test_crossref_classifies_retraction_and_correction():
    import hashlib

    retract = message({"is-retracted-by": [{"id": "10.1000/notice", "id-type": "doi"}]})
    raw = json.dumps(retract).encode()
    result = integrity.check_crossref(
        "10.1000/a",
        opener=lambda url, timeout: (200, raw),
    )
    assert result["status"] == "retracted"
    assert result["response_sha256"] == hashlib.sha256(raw).hexdigest()

    correction = message({"is-corrected-by": [{"id": "10.1000/corr"}]})
    result = integrity.check_crossref(
        "10.1000/a",
        opener=lambda url, timeout: (200, json.dumps(correction).encode()),
    )
    assert result["status"] == "correction"

    clean = message()
    result = integrity.check_crossref(
        "10.1000/a",
        opener=lambda url, timeout: (200, json.dumps(clean).encode()),
    )
    assert result["status"] == "no_update_found"


def test_check_many_handles_missing_doi_budget_and_error():
    studies = [
        {"study_id": "S1", "identifiers": {"doi": "10.1000/a"}},
        {"study_id": "S2", "identifiers": {}},
        {"study_id": "S3", "identifiers": {"doi": "10.1000/c"}},
        {"study_id": "S4", "identifiers": {"doi": "10.1000/d"}},
    ]

    def checker(doi):
        if doi == "10.1000/a":
            return {"status": "retracted", "updates": [], "checked_at": "2026-11-04"}
        if doi == "10.1000/c":
            raise RuntimeError("crossref offline")
        return {"status": "no_update_found", "updates": [], "checked_at": "2026-11-04"}

    result = integrity.check_many(studies, checker=checker, max_checks=2)
    assert result["checked"] == 2
    statuses = {item["study_id"]: item["status"] for item in result["checks"]}
    assert statuses["S1"] == "retracted"
    assert statuses["S2"] == "unchecked"
    assert statuses["S3"] == "error"
    assert statuses["S4"] == "unchecked"
    assert result["truth_claim"] is False
    assert result["policy"] == "absence_of_update_is_not_proof_of_integrity"


def test_apply_to_studies_updates_integrity_status(tmp_path):
    studies = tmp_path / "01_sources/systematic_review/studies"
    studies.mkdir(parents=True)
    study = {
        "study_id": "STUDY-ABCDEF12",
        "canonical_title": "Estudo A",
        "integrity_status": "unchecked",
    }
    dump(studies / "STUDY-ABCDEF12.json", study)
    result = integrity.check_many(
        [{"study_id": "STUDY-ABCDEF12", "identifiers": {"doi": "10.1000/a"}}],
        checker=lambda doi: {"status": "retracted", "updates": [], "checked_at": "2026-11-04"},
    )
    out = integrity.apply_to_studies(tmp_path, result)
    assert out["count"] == 1
    updated = json.loads((studies / "STUDY-ABCDEF12.json").read_text())
    assert updated["integrity_status"] == "retracted"
    assert (tmp_path / "03_evidence/study-integrity.json").exists()
