# -*- coding: utf-8 -*-
"""Contrato do roteador REAP (SPEC-935-R1115)."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".opencode" / "skills" / "reap-prompts"
PACKS_DIR = SKILL_DIR / "references" / "packs"
MANIFEST = SKILL_DIR / ".reap-manifest.json"

EXPECTED_PACKS = {
    "reap-00-install-and-verify",
    "reap-01-getting-started",
    "reap-02-feature-tracing-any-program",
    "reap-03-native-binary-exploration",
    "reap-04-software-and-feature-cloning",
    "reap-05-games",
    "reap-06-game-portability-to-wasm",
    "reap-07-firmware-and-embedded",
    "reap-08-android",
    "reap-09-kernel-analysis",
    "reap-10-vulnerability-research",
    "reap-11-electron-and-javascript",
    "reap-12-anti-cheat-and-protection-research",
    "reap-13-dma-and-hardware-assisted-cheat-research-defensive",
    "reap-14-software-cracking-research",
    "reap-15-version-comparison-and-crash-work",
    "reap-16-long-running-investigations",
    "reap-17-malware-analysis",
    "reap-18-advanced-binary-exploration-and-deobfuscation",
    "reap-19-kernel-and-driver-exploitation-research",
    "reap-20-advanced-software-cloning-and-feature-reconstruction",
    "reap-21-protector-and-obfuscator-research",
    "reap-22-go-and-rust-binary-source-recovery",
    "reap-prompts",
    "reap-wildcard",
    "reap-prompt-writing-tips",
}

HIGH_RISK = {
    "reap-09-kernel-analysis",
    "reap-10-vulnerability-research",
    "reap-12-anti-cheat-and-protection-research",
    "reap-13-dma-and-hardware-assisted-cheat-research-defensive",
    "reap-14-software-cracking-research",
    "reap-17-malware-analysis",
    "reap-18-advanced-binary-exploration-and-deobfuscation",
    "reap-19-kernel-and-driver-exploitation-research",
    "reap-21-protector-and-obfuscator-research",
}


def _frontmatter() -> dict:
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match
    return yaml.safe_load(match.group(1))


def _rows() -> dict[str, str]:
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\|\s*`(reap-[a-z0-9-]+)`\s*\|\s*(.+?)\s*\|\s*(baixo|médio|alto)\s*\|$", text, re.MULTILINE)
    return {name: tier for name, _theme, tier in rows}


def test_frontmatter() -> None:
    data = _frontmatter()
    assert data["name"] == "reap-prompts"
    assert data["metadata"]["packs"] == 26
    assert data["metadata"]["license"] == "MIT"
    assert "Joas Antonio dos Santos" in (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")


def test_table_covers_all_packs() -> None:
    rows = _rows()
    assert set(rows) == EXPECTED_PACKS
    assert len(rows) == 26


def test_all_reference_files_exist() -> None:
    files = {path.stem for path in PACKS_DIR.glob("*.md")}
    assert files == EXPECTED_PACKS


def test_high_risk_packs_are_marked() -> None:
    rows = _rows()
    for pack in HIGH_RISK:
        assert rows[pack] == "alto", f"{pack} deveria ser risco alto"


def test_manifest_hashes_match() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["schema"] == "reap.manifest.v1"
    assert manifest["source_commit"] == "9756618f25af1920c8965f8969820eed22247936"
    assert len(manifest["entries"]) == 26
    for entry in manifest["entries"]:
        destination = SKILL_DIR / entry["destination"]
        digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        assert digest == entry["sha256"], f"hash divergente: {destination}"


def test_only_one_top_level_reap_skill() -> None:
    skills_root = ROOT / ".opencode" / "skills"
    reap_dirs = sorted(
        path.name
        for path in skills_root.iterdir()
        if path.is_dir() and path.name.startswith("reap-")
    )
    assert reap_dirs == ["reap-prompts"]
