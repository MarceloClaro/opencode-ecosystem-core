"""R1054 — gate de validação externa, aceite editorial e autorização."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scientific_lab import external_validation as gate
from scientific_lab.native.common import dump, sha256_file


def make_project(tmp_path: Path) -> Path:
    out = tmp_path / "projeto"
    manuscript = out / "06_manuscript/manuscript.md"
    manuscript.parent.mkdir(parents=True)
    manuscript.write_text("# Manuscrito\n\n## Resumo\n\nTexto.\n", encoding="utf-8")
    return out


def test_gate_blocks_without_artifacts(tmp_path):
    out = make_project(tmp_path)
    result = gate.publication_gate(out)
    assert result["status"] == "blocked"
    assert "external_validation_missing" in result["reasons"]
    assert "editorial_acceptance_missing" in result["reasons"]
    assert "authorization_missing" in result["reasons"]
    assert result["publication_performed"] is False
    assert result["truth_claim"] is False


def test_gate_clears_only_with_valid_artifacts(tmp_path):
    out = make_project(tmp_path)
    manuscript = out / "06_manuscript/manuscript.md"
    validation = tmp_path / "validation.json"
    validation.write_text(json.dumps({
        "validation_id": "EXT-1",
        "independent": True,
        "verifier": "Auditor Externo",
        "verdict": "passed",
        "scope": "checagem de citações e cálculo",
        "signed_at": "2026-11-04T12:00:00Z",
        "artifact_sha256": sha256_file(manuscript),
        "evidence": ["relatório externo"],
    }), encoding="utf-8")
    gate.attach_external_validation(out, validation)
    assert gate.publication_gate(out)["status"] == "blocked"

    letter = tmp_path / "acceptance-letter.txt"
    letter.write_text("Aceite editorial fictício para teste.", encoding="utf-8")
    acceptance = tmp_path / "acceptance.json"
    acceptance.write_text(json.dumps({
        "acceptance_id": "ACC-1",
        "journal": "Revista de Teste",
        "decision": "accepted",
        "decision_date": "2026-11-04",
        "editor": "Editor Teste",
        "letter_path": str(letter),
        "letter_sha256": sha256_file(letter),
    }), encoding="utf-8")
    gate.attach_acceptance(out, acceptance)
    assert gate.publication_gate(out)["status"] == "blocked"

    authorization = tmp_path / "authorization.json"
    authorization.write_text(json.dumps({
        "author_name": "Autor Teste",
        "authorized_at": "2026-11-04T12:00:00Z",
        "human_confirmation": True,
        "manuscript_sha256": sha256_file(manuscript),
    }), encoding="utf-8")
    gate.attach_authorization(out, authorization)
    result = gate.publication_gate(out)
    assert result["status"] == "cleared_for_publication"
    assert result["external_validation"] is True
    assert result["publication_performed"] is False
    assert result["editorial_acceptance_artifact"]["journal"] == "Revista de Teste"


def test_gate_detects_manuscript_tampering(tmp_path):
    out = make_project(tmp_path)
    manuscript = out / "06_manuscript/manuscript.md"
    validation = tmp_path / "validation.json"
    validation.write_text(json.dumps({
        "independent": True,
        "verifier": "Auditor Externo",
        "verdict": "passed",
        "scope": "checagem",
        "signed_at": "2026-11-04T12:00:00Z",
        "artifact_sha256": sha256_file(manuscript),
    }), encoding="utf-8")
    gate.attach_external_validation(out, validation)
    manuscript.write_text("# Manuscrito alterado\n", encoding="utf-8")
    result = gate.publication_gate(out)
    assert result["status"] == "blocked"
    assert "external_validation_hash_mismatch" in result["reasons"]


def test_attach_rejects_unverified_or_wrong_hash(tmp_path):
    out = make_project(tmp_path)
    manuscript = out / "06_manuscript/manuscript.md"
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({
        "independent": False,
        "verifier": "x",
        "verdict": "passed",
        "scope": "x",
        "signed_at": "2026-11-04",
        "artifact_sha256": sha256_file(manuscript),
    }), encoding="utf-8")
    with pytest.raises(ValueError):
        gate.attach_external_validation(out, bad)

    bad.write_text(json.dumps({
        "independent": True,
        "verifier": "Auditor",
        "verdict": "passed",
        "scope": "x",
        "signed_at": "2026-11-04",
        "artifact_sha256": "a" * 64,
    }), encoding="utf-8")
    with pytest.raises(ValueError):
        gate.attach_external_validation(out, bad)
