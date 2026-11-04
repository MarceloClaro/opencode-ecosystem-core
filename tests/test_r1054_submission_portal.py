"""R1054 — submissão automática fail-closed com backend explícito."""
from __future__ import annotations

import json
from pathlib import Path

from scientific_lab import submission_portal
from scientific_lab.native.common import dump, sha256_file


def make_package(tmp_path: Path, *, pending=False) -> tuple[Path, dict]:
    out = tmp_path / "projeto"
    manuscript = out / "06_manuscript/manuscript.md"
    manuscript.parent.mkdir(parents=True)
    manuscript.write_text("# Manuscrito\n\n## Resumo\n\nTexto.\n", encoding="utf-8")
    sub = out / "10_submission"
    sub.mkdir()
    (sub / "manuscript.md").write_text("# Manuscrito\n", encoding="utf-8")
    (sub / "manuscript.pdf").write_bytes(b"%PDF-1.4 fake")
    (sub / "cover-letter.md").write_text("Carta.\n", encoding="utf-8")
    dump(sub / "submission-manifest.json", {"status": "completed"})
    dump(sub / "journal-checklist.json", {
        "status": "pending_human" if pending else "pass",
        "items": [{"id": "title", "status": "pending_human" if pending else "pass"}],
    })
    dump(sub / "declarations.json", {
        "status": "pending_human" if pending else "provided",
        "fields": {
            "ethics": {"status": "pending_human" if pending else "provided", "value": "ok"},
        },
    })
    authorization = {
        "human_confirmation": True,
        "author_name": "Autor Teste",
        "authorized_at": "2026-11-04T12:00:00Z",
        "manuscript_sha256": sha256_file(manuscript),
    }
    return out, authorization


def test_preflight_blocks_pending_declarations(tmp_path):
    out, _ = make_package(tmp_path, pending=True)
    result = submission_portal.preflight(out)
    assert result["status"] == "blocked"
    assert "declarations_pending" in result["reasons"]
    assert "checklist_pending" in result["reasons"]


def test_submit_requires_confirmation_authorization_and_backend(tmp_path):
    out, authorization = make_package(tmp_path)

    result = submission_portal.submit(out, confirm=False, authorization=authorization)
    assert result["attempt_status"] == "blocked"
    assert result["reason"] == "explicit_confirmation_required"
    assert result["submission_performed"] is False

    result = submission_portal.submit(out, confirm=True, authorization=None)
    assert result["reason"] == "authorization_required"

    result = submission_portal.submit(out, confirm=True, authorization=authorization)
    assert result["reason"] == "no_submission_backend_configured"
    assert result["submission_performed"] is False

    bad = dict(authorization)
    bad["manuscript_sha256"] = "a" * 64
    result = submission_portal.submit(out, confirm=True, authorization=bad)
    assert result["reason"] == "authorization_hash_mismatch"


def test_submit_with_fake_backend_records_attempt(tmp_path):
    out, authorization = make_package(tmp_path)
    calls = []

    def backend(package: Path, metadata: dict) -> dict:
        calls.append((package, metadata))
        return {"status": "submitted", "submission_id": "SUB-123"}

    result = submission_portal.submit(
        out, confirm=True, authorization=authorization, backend=backend,
    )
    assert result["status"] == "submitted"
    assert result["submission_performed"] is True
    assert result["backend"]["submission_id"] == "SUB-123"
    assert calls and calls[0][0] == out / "10_submission"
    attempt = json.loads(
        (out / "10_submission/submission-attempt.json").read_text(encoding="utf-8")
    )
    assert attempt["status"] == "submitted"
    assert attempt["truth_claim"] is False
    assert attempt["external_validation"] is False
