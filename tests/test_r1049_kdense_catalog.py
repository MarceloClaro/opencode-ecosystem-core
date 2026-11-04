"""R1049: catálogo completo K-Dense, 177 instruções, 11 categorias, sem execução."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from integrations import kdense_catalog

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "external/kdense-scientific-agent-skills/CATALOG.json"


def test_catalog_has_177_unique_skills_and_11_categories():
    data = kdense_catalog.load_catalog()
    assert data["count"] == 177
    counts = kdense_catalog.category_counts(data)
    assert len(counts) == 11
    assert sum(counts.values()) == 177
    assert counts["bioinformatica-genomica"] >= 30
    assert counts["literatura-citacao-editorial"] >= 15
    assert len({row["skill"] for row in data["skills"]}) == 177


def test_every_entry_is_instruction_only_and_local():
    data = kdense_catalog.load_catalog()
    root = CATALOG.parent
    for row in data["skills"]:
        assert row["instruction_only"] is True
        assert row["scripts_vendored"] is False
        assert row["autoload"] is False
        assert len(row["source_commit"]) == 40
        if row["license_class"] == "permissive":
            assert row["mirrored"] is True
            path = (root / row["local_skill_md"]).resolve()
            assert path.is_file() and path.is_relative_to(root)
            assert path.stat().st_size > 0
            normalized = row.get("license_normalized", row["license"]).lower()
            assert any(k in normalized for k in ("mit", "bsd", "apache", "biopython", "cc-by-4.0"))
        else:
            assert row["license_class"] == "hold"
            assert row["mirrored"] is False
            assert row["local_skill_md"] is None
            assert "license_hold" in row["status"]
            adapter = (ROOT / row["original_adapter_md"]).resolve()
            assert adapter.is_file() and adapter.is_relative_to(ROOT)
            assert adapter.stat().st_size > 0


def test_no_scripts_assets_or_binaries_are_mirrored():
    root = ROOT / "external/kdense-scientific-agent-skills"
    assert not list(root.rglob("*.py"))
    assert not list(root.rglob("*.sh"))
    assert not list(root.rglob("*.pth"))
    assert not list(root.rglob("*.onnx"))
    assert not list(root.rglob("*.ipynb"))


def test_search_and_category_filter():
    data = kdense_catalog.load_catalog()
    rows = kdense_catalog.search(data, "literature review")
    assert rows and rows[0]["skill"] in {"literature-review", "research-lookup",
                                         "paper-lookup", "citation-management"}
    clinical = kdense_catalog.search(data, "clinical", category="clinica-saude")
    assert clinical and all(row["category"] == "clinica-saude" for row in clinical)
    with pytest.raises(ValueError):
        kdense_catalog.search(data, "x", category="nao-existe")


def test_get_skill_is_confined_and_returns_text():
    data = kdense_catalog.load_catalog()
    row = kdense_catalog.get_skill(data, "literature-review")
    assert row["category"] == "literatura-citacao-editorial"
    assert "Literature Review" in row["text"]
    assert row["path"].endswith("literature-review/SKILL.md")
    adapter = kdense_catalog.get_skill(data, "cobrapy")
    assert adapter["adapter"] is True
    assert adapter["mirrored"] is False
    assert "Modelos metabólicos" in adapter["text"]
    for bad in ("../etc/passwd", "/etc/passwd", "Literature Review", ""):
        with pytest.raises(ValueError):
            kdense_catalog.get_skill(data, bad)


def test_stats_and_cli():
    data = kdense_catalog.load_catalog()
    summary = kdense_catalog.stats(data)
    assert summary["count"] == 177
    assert summary["permissive_count"] == 168
    assert summary["license_hold_count"] == 9
    assert summary["original_adapter_count"] == 9
    assert summary["scripts_vendored"] == 0
    assert summary["autoload"] == 0
    assert summary["risk_flags"]["dual-use-review"] >= 1
    proc = subprocess.run([sys.executable, "-m", "integrations.kdense_catalog", "stats"],
                          cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    parsed = json.loads(proc.stdout)
    assert parsed["count"] == 177
    assert parsed["instruction_only"] == 177
