"""R1052 — leitura de decisões humanas e PRISMA com pendências."""
from __future__ import annotations

import json

from scientific_lab import screening
from scientific_lab.native import review
from scientific_lab.native.common import dump


def make_study(tmp_path, study_id, title, doi):
    studies = tmp_path / "01_sources/systematic_review/studies"
    studies.mkdir(parents=True, exist_ok=True)
    study = {
        "study_id": study_id,
        "canonical_title": title,
        "identifiers": {"doi": doi},
        "source_records": [],
        "screening_status": "pending",
        "included_in_synthesis": False,
    }
    dump(studies / f"{study_id}.json", study)
    return study


def test_summarize_pending_conflict_and_human_verified(tmp_path):
    make_study(tmp_path, "STUDY-AAAAAAAA", "Estudo A", "10.1000/a")
    make_study(tmp_path, "STUDY-BBBBBBBB", "Estudo B", "10.1000/b")
    make_study(tmp_path, "STUDY-CCCCCCCC", "Estudo C", "10.1000/c")

    review.screen(tmp_path, "SRP-T", "STUDY-AAAAAAAA", "title_abstract", "R1", "include", "ok", human=True)
    review.screen(tmp_path, "SRP-T", "STUDY-AAAAAAAA", "title_abstract", "R2", "include", "ok", human=True)
    review.screen(tmp_path, "SRP-T", "STUDY-AAAAAAAA", "full_text", "R1", "include", "ok", human=True)
    review.screen(tmp_path, "SRP-T", "STUDY-AAAAAAAA", "full_text", "R2", "include", "ok", human=True)

    review.screen(tmp_path, "SRP-T", "STUDY-BBBBBBBB", "title_abstract", "R1", "exclude", "fora", human=True)
    review.screen(tmp_path, "SRP-T", "STUDY-BBBBBBBB", "title_abstract", "R2", "exclude", "fora", human=True)
    review.screen(tmp_path, "SRP-T", "STUDY-BBBBBBBB", "full_text", "R1", "exclude", "fora", human=True)
    review.screen(tmp_path, "SRP-T", "STUDY-BBBBBBBB", "full_text", "R2", "exclude", "fora", human=True)

    review.screen(tmp_path, "SRP-T", "STUDY-CCCCCCCC", "title_abstract", "R1", "include", "ok", human=True)
    review.screen(tmp_path, "SRP-T", "STUDY-CCCCCCCC", "title_abstract", "R2", "exclude", "não", human=True)

    studies = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((tmp_path / "01_sources/systematic_review/studies").glob("*.json"))
    ]
    decisions = screening.load_decisions(tmp_path)
    summary = screening.summarize(studies, decisions)
    assert summary["summary"]["total"] == 3
    assert summary["summary"]["included"] == 1
    assert summary["summary"]["excluded"] == 1
    assert summary["summary"]["pending"] == 1
    assert summary["summary"]["conflicts"] == 1
    assert summary["human_verified"] is False
    assert summary["status"] == "human_partial"

    path = screening.write_summary(tmp_path, summary)
    assert path.exists()
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["policy"] == "decision_is_human_only"
    assert stored["truth_claim"] is False


def test_merge_into_triage_preserves_human_fields(tmp_path):
    make_study(tmp_path, "STUDY-AAAAAAAA", "Estudo A", "10.1000/a")
    review.screen(tmp_path, "SRP-T", "STUDY-AAAAAAAA", "title_abstract", "R1", "include", "ok", human=True)
    review.screen(tmp_path, "SRP-T", "STUDY-AAAAAAAA", "title_abstract", "R2", "include", "ok", human=True)
    review.screen(tmp_path, "SRP-T", "STUDY-AAAAAAAA", "full_text", "R1", "include", "ok", human=True)
    review.screen(tmp_path, "SRP-T", "STUDY-AAAAAAAA", "full_text", "R2", "include", "ok", human=True)
    studies = [json.loads(p.read_text(encoding="utf-8")) for p in (tmp_path / "01_sources/systematic_review/studies").glob("*.json")]
    summary = screening.summarize(studies, screening.load_decisions(tmp_path))
    triage = {
        "studies": [{
            "study_id": "STUDY-AAAAAAAA",
            "screening_status": "pending",
            "included_in_synthesis": False,
        }],
    }
    merged = screening.merge_into_triage(triage, summary)
    item = merged["studies"][0]
    assert item["human_screening_status"] == "included_full_text"
    assert item["human_reviewers"] == ["R1", "R2"]
    assert item["human_conflict"] is False
    assert merged["human_verified"] is True


def test_ingest_dedupes_same_title_with_different_dois(tmp_path):
    manifest = {
        "results": [
            {
                "article_id": "ART-0001",
                "title": "The open access citation advantage: a systematic review",
                "doi": "10.1000/a",
                "authors": [],
                "year": 2021,
                "venue": "J",
                "source": "openalex",
                "record_url": "https://example.org/a",
            },
            {
                "article_id": "ART-0002",
                "title": "The open access citation advantage: a systematic review",
                "doi": "10.1000/b",
                "authors": [],
                "year": 2021,
                "venue": "J",
                "source": "crossref",
                "record_url": "https://example.org/b",
            },
        ]
    }
    path = tmp_path / "manifest.json"
    dump(path, manifest)
    out = review.ingest(tmp_path, path)
    assert out["records_identified"] == 2
    assert out["unique_studies"] == 1
    assert out["duplicates_removed"] == 1


def test_summarize_pending_when_no_decisions():
    summary = screening.summarize(
        [{"study_id": "STUDY-AAAAAAAA", "canonical_title": "A"}],
        [],
    )
    assert summary["status"] == "pending_human"
    assert summary["summary"]["pending"] == 1
    assert summary["human_verified"] is False
