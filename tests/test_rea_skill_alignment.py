# -*- coding: utf-8 -*-
"""Contrato de alinhamento da skill REA (SPEC-935-R1112)."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".opencode" / "skills" / "reverse-engineer-anything"
BACKUP_DIR = ROOT / ".opencode" / "skills" / ".archive" / "reverse-engineer-anything-v37"
INSTALLED_PACKAGE = (
    Path.home()
    / ".local"
    / "share"
    / "opencode-core"
    / "rea-6.8.0"
    / "skills"
    / "reverse-engineer-anything"
)


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, f"frontmatter ausente em {path}"
    return yaml.safe_load(match.group(1))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_frontmatter_declares_v49() -> None:
    data = _frontmatter(SKILL_DIR / "SKILL.md")
    assert data["name"] == "reverse-engineer-anything"
    assert data["metadata"]["version"] == "49"
    assert data["metadata"]["tool_count"] == 229


def test_all_cited_references_exist() -> None:
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    cited = sorted(set(re.findall(r"references/[a-z0-9-]+\.md", text)))
    assert cited, "a skill deve citar pelo menos uma referência"
    for reference in cited:
        assert (SKILL_DIR / reference).is_file(), f"referência ausente: {reference}"


def test_reference_set_matches_v49() -> None:
    references = sorted(p.name for p in (SKILL_DIR / "references").glob("*.md"))
    assert references == [
        "android-applications.md",
        "connection-and-recovery.md",
        "environments.md",
        "evidence-workflows.md",
        "javascript-applications.md",
        "native-and-artifacts.md",
        "runtime-observation.md",
    ]
    assert not (SKILL_DIR / "references" / "search-before-reconstruction.md").exists()


def test_origin_records_version_and_hash() -> None:
    origin = json.loads((SKILL_DIR / "origin.json").read_text(encoding="utf-8"))
    assert origin["package"] == "rea-agents"
    assert origin["version"] == "6.8.0"
    assert origin["skill_version"] == "49"
    assert origin["tool_count"] == 229
    assert origin["license"] == "MIT"
    assert origin["skill_sha256"] == _sha256(SKILL_DIR / "SKILL.md")
    for relative, digest in origin["files"].items():
        assert _sha256(SKILL_DIR / relative) == digest, f"hash divergente: {relative}"


def test_backup_of_v37_is_preserved() -> None:
    assert (BACKUP_DIR / "SKILL.md").is_file()
    data = _frontmatter(BACKUP_DIR / "SKILL.md")
    assert data["metadata"]["version"] == "37"
    origin = json.loads((SKILL_DIR / "origin.json").read_text(encoding="utf-8"))
    assert origin["backup"]["skill_sha256"] == _sha256(BACKUP_DIR / "SKILL.md")
    assert origin["backup"]["skill_version"] == "37"


@pytest.mark.skipif(
    not INSTALLED_PACKAGE.is_dir(), reason="pacote rea-agents 6.8.0 ausente"
)
def test_installed_skill_matches_package() -> None:
    assert _sha256(SKILL_DIR / "SKILL.md") == _sha256(
        INSTALLED_PACKAGE / "SKILL.md"
    )
