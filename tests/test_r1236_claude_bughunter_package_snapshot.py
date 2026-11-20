"""Contratos offline do snapshot inerte Claude-BugHunter (R1236)."""

from __future__ import annotations

import hashlib
import json
import re
import stat
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "federation/claude-bughunter-package-r1236.json"
SNAPSHOT_ROOT = ROOT / "external/claude-bughunter-snapshot"
REPOSITORY = "elementalsouls/Claude-BugHunter"
COMMIT = "0e70a021e59d6875004e7a563f8511aca2ba3bc1"


def _manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_manifest_pins_snapshot_commit_and_separates_license_scopes():
    manifest = _manifest()
    source = manifest["source"]
    snapshot = manifest["snapshot"]
    assert manifest["schema_version"] == "r1236.v1"
    assert manifest["repository"] == REPOSITORY
    assert source["commit"] == COMMIT
    assert source["archive_url"].endswith(f"/zip/{COMMIT}")
    assert re.fullmatch(r"[0-9a-f]{64}", source["archive_sha256"])
    assert source["signature_status"] == "not_observed"
    assert source["branch_head_status"] == "not_verified"
    assert manifest["license"] == {
        "code": "MIT",
        "content": "CC-BY-4.0",
        "third_party_material": "independent_unreviewed",
        "legal_review": "not_performed",
    }
    assert snapshot["root"] == "external/claude-bughunter-snapshot"
    assert snapshot["file_count"] > 0
    assert snapshot["skills_count"] > 0
    assert snapshot["commands_count"] > 0


def test_inventory_hashes_match_the_vendored_snapshot():
    manifest = _manifest()
    snapshot = manifest["snapshot"]
    entries = snapshot["files"]
    assert isinstance(entries, list) and entries
    paths = [row["path"] for row in entries]
    assert paths == sorted(paths)
    assert len(paths) == len(set(paths)) == snapshot["file_count"]

    actual_paths = set()
    for path in SNAPSHOT_ROOT.rglob("*"):
        assert not path.is_symlink()
        if path.is_file():
            relative = path.relative_to(SNAPSHOT_ROOT).as_posix()
            actual_paths.add(relative)
            assert not (path.stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
    assert actual_paths == set(paths)

    for row in entries:
        relative = Path(row["path"])
        assert not relative.is_absolute()
        assert ".." not in relative.parts
        path = SNAPSHOT_ROOT / relative
        content = path.read_bytes()
        assert len(content) == row["bytes"]
        assert hashlib.sha256(content).hexdigest() == row["sha256"]

    assert {"README.md", "LICENSE", "LICENSE-CONTENT", "NOTICE"} <= set(paths)


def test_package_is_not_registered_executed_or_installed():
    manifest = _manifest()
    assert manifest["adoption"] == "inert_snapshot"
    assert manifest["activation"] == {
        "registered_skill_count": 0,
        "registered_command_count": 0,
        "scripts_executable": False,
        "burp_mcp_registered": False,
    }
    assert manifest["runtime"] == {
        "installed": False,
        "executed": False,
        "enabled": False,
        "mcp_enabled": False,
    }
    skill_dirs = sorted(
        path.name
        for path in (ROOT / ".opencode/skills").glob("claude-bughunter*")
        if path.is_dir()
    )
    assert skill_dirs == ["claude-bughunter-safe"]
    assert not (ROOT / ".opencode/commands/claude-bughunter").exists()


def test_burp_mcp_and_target_testing_remain_disabled():
    manifest = _manifest()
    assert manifest["activation"]["burp_mcp_registered"] is False
    assert manifest["runtime"]["mcp_enabled"] is False
    assert manifest["active_target_testing_authorized"] is False
    opencode_config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    assert "burp" not in json.dumps(opencode_config, ensure_ascii=False).casefold()

    safe_skill = (ROOT / ".opencode/skills/claude-bughunter-safe/SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "external/claude-bughunter-snapshot" in safe_skill
    assert "referência inerte" in safe_skill.casefold()
