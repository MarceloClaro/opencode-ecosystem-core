"""R1078: gate do landscape GitHub e da proposta Book Studio Universal."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/r1078"
MANIFEST = REPORT / "github_landscape.json"
README = REPORT / "README.md"
SPEC = ROOT / "specs/SPEC-935-R1078-book-studio-universal.md"

VALID_PRIORITIES = {"P0", "P1", "P2"}
VALID_INTEGRATIONS = {"core-native", "adapter", "library", "reference", "avoid"}
REQUIRED_KEYS = {
    "repo", "url", "stars", "license", "license_verified", "language",
    "pushed_at", "layer", "gaps", "integration", "priority", "note",
}


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def is_strong_copyleft(license_name: str) -> bool:
    upper = license_name.upper()
    if "AGPL" in upper:
        return True
    return "GPL" in upper and "LGPL" not in upper


def test_manifest_schema_and_coverage():
    data = load_manifest()
    assert data["schema_version"] == 1
    assert data["status"] == "research_completed_no_integration"
    assert set(data["gaps"]) == {f"G{i}" for i in range(1, 16)}
    assert len(data["repos"]) >= 100

    seen = set()
    for repo in data["repos"]:
        assert REQUIRED_KEYS <= set(repo), repo.get("repo")
        assert repo["repo"] not in seen, f"duplicado: {repo['repo']}"
        seen.add(repo["repo"])
        assert repo["url"].startswith("https://github.com/")
        assert isinstance(repo["stars"], int) and repo["stars"] >= 0
        assert repo["license"].strip()
        assert repo["priority"] in VALID_PRIORITIES
        assert repo["integration"] in VALID_INTEGRATIONS
        assert repo["gaps"], repo["repo"]
        assert set(repo["gaps"]) <= set(data["gaps"]), repo["repo"]


def test_every_gap_has_multiple_candidates():
    data = load_manifest()
    for gap in data["gaps"]:
        count = sum(1 for repo in data["repos"] if gap in repo["gaps"])
        assert count >= 3, f"{gap} tem apenas {count} candidatos"


def test_license_gate_blocks_copyleft_libraries():
    data = load_manifest()
    for repo in data["repos"]:
        if is_strong_copyleft(repo["license"]):
            assert repo["integration"] != "library", (
                f"{repo['repo']} ({repo['license']}) não pode ser library"
            )
        if repo["priority"] == "P0":
            assert repo["integration"] != "avoid", repo["repo"]


def test_readme_documents_gaps_and_limits():
    text = re.sub(r"\s+", " ", README.read_text(encoding="utf-8").lower())
    for i in range(1, 16):
        assert f"g{i}" in text, f"gap G{i} ausente no relatório"
    for term in (
        "300 dpi", "pdf/ua", "onix", "isbn", "epub", "tac",
        "nenhum dos 109 repositórios", "10/10",
    ):
        assert term in text, term


def test_spec_declares_status_and_requirements():
    text = SPEC.read_text(encoding="utf-8")
    assert "Status:** fase 0 implementada" in text
    assert "não objetivos" in text.lower()
    for i in range(1, 13):
        assert re.search(rf"\|\s*R{i}\s*\|", text), f"requisito R{i} ausente"
    assert "fase 0" in text.lower()
