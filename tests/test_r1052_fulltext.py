"""R1052 — texto integral: indexação, casamento, citações e aprovação humana."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from research.searchers import PaperRecord


def study(**overrides):
    base = {
        "study_id": "STUDY-ABCDEF12",
        "canonical_title": "Estudo A sobre o tema",
        "identifiers": {"doi": "10.1000/a"},
        "source_records": ["ART-0001"],
        "year": 2024,
        "authors": ["Ana Silva"],
        "venue": "Revista de Teste",
        "screening_status": "pending",
        "included_in_synthesis": False,
    }
    base.update(overrides)
    return base


def record(**overrides):
    base = {
        "article_id": "ART-0001",
        "title": "Estudo A sobre o tema",
        "doi": "10.1000/a",
        "year": 2024,
        "source": "openalex",
        "abstract": "Resumo indexado do estudo.",
    }
    base.update(overrides)
    return base


def write_text(tmp_path: Path) -> Path:
    texts = tmp_path / "texts"
    texts.mkdir()
    (texts / "estudo-a.md").write_text(
        "# Estudo A\n\n"
        "DOI: 10.1000/a\n\n"
        "Este estudo descreve um experimento controlado sobre o tema e "
        "apresenta resultados descritivos sem inferência causal. "
        "A amostra incluiu participantes adultos e o desfecho foi medido "
        "no mesmo período.\n\n"
        "Os autores concluem que o resultado é exploratório e não permite "
        "generalização para outras populações.\n",
        encoding="utf-8",
    )
    return texts


def test_index_match_and_extract_candidates(tmp_path):
    from scientific_lab import fulltext

    texts = write_text(tmp_path)
    index = fulltext.index_fulltexts(texts)
    assert index["count"] == 1
    assert index["entries"][0]["format"] == "markdown"
    assert index["entries"][0]["text_chars"] > 200

    matches = fulltext.match_entries(index, [study()], [record()])
    assert matches["count"] == 1
    assert matches["matches"][0]["method"] == "doi_in_text"
    assert matches["matches"][0]["confidence"] == 1.0

    candidates = fulltext.extract_candidates(
        index, matches, [study()], [record()], keywords=["estudo", "tema"],
    )
    assert candidates["count"] >= 1
    first = candidates["candidates"][0]
    assert first["study_id"] == "STUDY-ABCDEF12"
    assert first["article_id"] == "ART-0001"
    assert first["locator"].startswith("par.")
    assert first["source_sha256"] == index["entries"][0]["sha256"]
    assert len(first["quote_sha256"]) == 64


def test_extract_candidates_skips_duplicate_file_for_same_study(tmp_path):
    from scientific_lab import fulltext

    texts = write_text(tmp_path)
    (texts / "estudo-a-copia.md").write_text(
        "# Estudo A (cópia)\n\nDOI: 10.1000/a\n\n"
        "Este estudo descreve um experimento controlado sobre o tema e "
        "apresenta resultados descritivos sem inferência causal. "
        "A amostra incluiu participantes adultos e o desfecho foi medido "
        "no mesmo período.\n",
        encoding="utf-8",
    )
    index = fulltext.index_fulltexts(texts)
    matches = fulltext.match_entries(index, [study()], [record()])
    assert matches["ambiguous"] >= 1
    candidates = fulltext.extract_candidates(index, matches, [study()], [record()])
    ids = [item["claim_id"] for item in candidates["candidates"]]
    assert len(ids) == len(set(ids))


def test_approval_requires_human_confirmation_and_known_ids(tmp_path):
    from scientific_lab import fulltext

    texts = write_text(tmp_path)
    index = fulltext.index_fulltexts(texts)
    candidates = fulltext.extract_candidates(
        index,
        fulltext.match_entries(index, [study()], [record()]),
        [study()],
        [record()],
    )
    ids = [item["claim_id"] for item in candidates["candidates"]]
    base = {
        "schema_version": "1.0",
        "project_id": "RP-TEST",
        "reviewer": "Revisor Teste",
        "reviewed_at": "2026-11-04T12:00:00Z",
        "decision": "approved",
        "human_confirmation": True,
        "approved_claim_ids": [ids[0]],
        "rejected_claim_ids": [],
        "notes": "",
    }
    path = tmp_path / "approval.json"
    path.write_text(json.dumps(base), encoding="utf-8")
    assert fulltext.validate_approval(path, ids)["reviewer"] == "Revisor Teste"

    base["human_confirmation"] = False
    path.write_text(json.dumps(base), encoding="utf-8")
    with pytest.raises(ValueError):
        fulltext.validate_approval(path, ids)

    base["human_confirmation"] = True
    base["approved_claim_ids"] = ["CLAIM-DESCONHECIDO"]
    path.write_text(json.dumps(base), encoding="utf-8")
    with pytest.raises(ValueError):
        fulltext.validate_approval(path, ids)


def test_apply_approval_writes_verified_annotation_and_claim(tmp_path):
    from scientific_lab import fulltext

    texts = write_text(tmp_path)
    index = fulltext.index_fulltexts(texts)
    matches = fulltext.match_entries(index, [study()], [record()])
    candidates = fulltext.extract_candidates(index, matches, [study()], [record()])
    candidate = candidates["candidates"][0]
    approval = {
        "schema_version": "1.0",
        "project_id": "RP-TEST",
        "reviewer": "Revisor Teste",
        "reviewed_at": "2026-11-04T12:00:00Z",
        "decision": "approved",
        "human_confirmation": True,
        "approved_claim_ids": [candidate["claim_id"]],
        "rejected_claim_ids": [],
        "notes": "",
    }
    result = fulltext.apply_approval(
        tmp_path, "RP-TEST", index, candidates["candidates"], approval, [study()],
    )
    assert result["counts"]["verified"] == 1
    annotations = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in (tmp_path / "09_provenance/evidence_annotations").glob("*.json")
    ]
    verified = [
        item for item in annotations if item["verification_status"] == "verified"
    ]
    assert len(verified) == 1
    assert len(verified[0]["source_sha256"]) == 64
    assert sum(
        item["verification_status"] == "candidate" for item in annotations
    ) == len(annotations) - 1

    claims = fulltext.fulltext_claims(
        candidates["candidates"], approval["approved_claim_ids"], [study()],
    )
    assert len(claims) == 1
    assert claims[0]["evidence"][0]["source_id"] == "ART-0001"
    assert claims[0]["evidence"][0]["literal_verified"] is True


def test_apply_approval_is_idempotent_for_same_claim(tmp_path):
    from scientific_lab import fulltext

    texts = write_text(tmp_path)
    index = fulltext.index_fulltexts(texts)
    candidates = fulltext.extract_candidates(
        index,
        fulltext.match_entries(index, [study()], [record()]),
        [study()],
        [record()],
    )
    candidate = candidates["candidates"][0]
    approval = {
        "schema_version": "1.0",
        "project_id": "RP-TEST",
        "reviewer": "Revisor Teste",
        "reviewed_at": "2026-11-04T12:00:00Z",
        "decision": "approved",
        "human_confirmation": True,
        "approved_claim_ids": [candidate["claim_id"]],
        "rejected_claim_ids": [],
        "notes": "",
    }
    fulltext.apply_approval(
        tmp_path, "RP-TEST", index, candidates["candidates"], approval, [study()],
    )
    first_count = len(list((tmp_path / "09_provenance/evidence_annotations").glob("*.json")))
    fulltext.apply_approval(
        tmp_path, "RP-TEST", index, candidates["candidates"], approval, [study()],
    )
    second_count = len(list((tmp_path / "09_provenance/evidence_annotations").glob("*.json")))
    assert first_count == second_count
    approved_annotations = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in (tmp_path / "09_provenance/evidence_annotations").glob("*.json")
        if json.loads(path.read_text(encoding="utf-8"))["claim_id"] == candidate["claim_id"]
    ]
    assert len(approved_annotations) == 1
