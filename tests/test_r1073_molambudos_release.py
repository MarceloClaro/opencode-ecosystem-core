"""R1073: gate da revisão final, release e exclusão definitiva do Molambudos."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/r1073"
MANIFEST = REPORT / "manifest_quarentena.json"
FULL_MANIFEST = REPORT / "manifest_completo_exclusao.json"
FILES = REPORT / "files_excluidos.jsonl"
CATALOG = ROOT / "reports/r1072/catalogo.json"
BOOK = ROOT / "literatura/molambudos"
RELEASE = BOOK / "release/2026-11-05"
QUARANTINE = BOOK / "_descarte/2026-11-05"
CANONICAL_SHA = "3378f438d1124432b1b67fdf29161363e28276bb4a754c2a070bf5b054d56f4b"
OLD_SHA = "77aabe2e4e055d7f53fbef17dd3857e561f50f556a94f92da0d3ff039f4ea66f"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def test_manifest_records_deleted_state():
    data = load(MANIFEST)
    assert data["schema_version"] == 1
    assert data["state"] == "deleted"
    assert data["deletion"]["status"] == "deleted"
    assert data["deletion"]["files"] == data["totals"]["files"] == 2895
    assert data["deletion"]["bytes"] == data["totals"]["bytes"] == 511_882_663
    assert data["canonical"]["sha256"] == CANONICAL_SHA
    assert data["canonical"]["pages"] == 435
    assert data["canonical"]["trim"] == "160x230mm"
    assert data["promotion"]["old_sha256"] == OLD_SHA
    assert data["promotion"]["new_sha256"] == CANONICAL_SHA

    full = load(FULL_MANIFEST)
    assert full["canonical"]["sha256"] == CANONICAL_SHA
    assert full["totals"]["files"] == 2895
    assert full["totals"]["bytes"] == 511_882_663
    lines = sum(1 for _ in FILES.open(encoding="utf-8"))
    assert lines == 2895


def test_manifest_items_have_hashes_and_reasons():
    data = load(MANIFEST)
    categories = {item["category"] for item in data["items"]}
    assert {
        "edicao_alternativa",
        "arquivo_historico",
        "pdf_superado",
        "build_antigo",
        "backup_editorial",
        "rascunho",
        "template_superado",
    } <= categories
    for item in data["items"]:
        assert item["quarantine_path"].startswith("literatura/molambudos/_descarte/2026-11-05/")
        assert item["original_path"].startswith("literatura/")
        assert item["files"] >= 1
        assert item["bytes"] >= 0
        assert len(item["tree_sha256"]) == 64
        assert item["reason"].strip()
        assert item["kind"] in {"file", "dir"}


def test_catalog_marks_alternates_as_deleted():
    data = load(CATALOG)
    by_id = {work["id"]: work for work in data["works"]}
    assert data["count"] == len(data["works"]) == 48

    canonical = by_id["molambudos-victoria-regia"]
    assert canonical["canonical"] is True
    assert canonical["pdf"] == "literatura/molambudos/Molambudos_VictoriaRegia/main_kdp_pt_160x230mm.pdf"
    assert "3378f438" in canonical["notes"]

    for work_id in ("molambudos-v2", "molambudos-diario", "molambudos-template-antigo"):
        work = by_id[work_id]
        assert work.get("deleted") is True
        assert work.get("archived") is True
        assert work.get("pdf") is None
        assert work.get("source") is None
        assert "excluído" in work["status"].lower()


def test_versioned_records_document_deletion():
    note = (REPORT / "RELEASE_NOTE.md").read_text(encoding="utf-8")
    readme = (REPORT / "README.md").read_text(encoding="utf-8")
    deletion = (REPORT / "DELETION.md").read_text(encoding="utf-8")
    review = (REPORT / "REVISAO_FINAL.md").read_text(encoding="utf-8")

    assert "exclu" in note.lower()
    assert "definitivamente" in note.lower()
    assert CANONICAL_SHA in note
    assert "EPUB" in note

    assert "exclusão definitiva" in readme.lower()
    assert "2.895" in readme

    assert "irreversível" in deletion.lower()
    assert "2.895" in deletion
    assert "511.882.663" in deletion

    assert CANONICAL_SHA in review
    assert "exclusão definitiva" in review.lower()


def test_local_release_after_deletion_if_present():
    if not BOOK.is_dir():
        pytest.skip("conteúdo literário gitignored não está presente")

    assert (BOOK / "REVISAO_FINAL.md").is_file()
    assert (BOOK / "Molambudos_VictoriaRegia/main_kdp_pt_160x230mm.pdf").is_file()
    assert sha256(BOOK / "Molambudos_VictoriaRegia/main_kdp_pt_160x230mm.pdf") == CANONICAL_SHA

    assert not QUARANTINE.exists()
    assert not (BOOK / "Molambudos_v2").exists()
    assert not (BOOK / "Molambudos_v2_Diario").exists()
    assert not (BOOK / "Molambudos_VictoriaRegia/_archive").exists()
    assert not (BOOK / "Molambudos_VictoriaRegia/build").exists()

    assert (REPORT / "DELETION.md").is_file()
    assert FULL_MANIFEST.is_file()
    assert FILES.is_file()
    assert sum(1 for _ in FILES.open(encoding="utf-8")) == 2895

    sums = (RELEASE / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
    assert len(sums) >= 8
    for line in sums:
        digest, rel = line.split("  ", 1)
        target = RELEASE / rel
        assert target.is_file(), rel
        assert sha256(target) == digest, rel

    broken = [p for p in BOOK.rglob("*") if p.is_symlink() and not p.exists()]
    assert broken == []
