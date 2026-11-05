"""R1072: schema do catálogo do hub literário."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "reports/r1072/catalogo.json"
GENERATOR = ROOT / "scripts/build_literary_hub.py"


def load_catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def test_catalog_schema_and_uniqueness():
    data = load_catalog()
    assert data["schema_version"] == 1
    works = data["works"]
    assert data["count"] == len(works) == 45
    ids = [work["id"] for work in works]
    assert len(ids) == len(set(ids))
    assert {"livro", "template", "academico", "template-academico"} >= {
        work["category"] for work in works
    }
    assert {work["scope"] for work in works} <= {"literario", "academico"}
    for work in works:
        assert isinstance(work["title"], str) and work["title"].strip()
        assert isinstance(work["status"], str) and work["status"].strip()
        assert isinstance(work["links"], list)


def test_catalog_marks_the_expected_canonical_works():
    data = load_catalog()
    canonical = {work["id"] for work in data["works"] if work.get("canonical")}
    assert canonical == {
        "molambudos-victoria-regia",
        "livro-opencode",
        "livro-volume2",
        "livro-gemeos-odontologia",
    }


def test_catalog_has_unique_link_paths():
    data = load_catalog()
    paths = [link["path"] for work in data["works"] for link in work["links"]]
    assert len(paths) == len(set(paths))


def test_generator_is_versioned():
    assert GENERATOR.is_file()
    text = GENERATOR.read_text(encoding="utf-8")
    assert "projetos/literarios" in text
    assert "catalogo.json" in text
