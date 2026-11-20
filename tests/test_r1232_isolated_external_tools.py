"""TDD contracts for SPEC-935-R1232; external tools are always mocked here."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from integrations import isolated_external_tools as ext


ROOT = Path(__file__).resolve().parents[1]


def _entries():
    return {item["id"]: item for item in ext.load_manifest()["repositories"]}


def test_manifest_pins_sources_licenses_and_isolation_states():
    manifest = ext.load_manifest()
    assert manifest["schema_version"] == "r1232.v1"
    assert ext.validate_manifest(manifest) == []
    entries = {item["id"]: item for item in manifest["repositories"]}
    assert {
        "rust-anything", "awesome-reverse-engineer-anything", "open-reverselab",
        "universal-os", "anthropic-mcp-builder", "anthropic-skill-creator",
        "caveman", "cc-switch", "prompts-chat", "rea",
    } <= entries.keys()
    assert entries["rust-anything"]["source"]["version"] == "2.1.0"
    assert entries["universal-os"]["source"]["commit"] == "661f15fc1afbbe1158ac5d14673e188238f29c0c"
    assert entries["caveman"]["source"]["version"] == "4.1.0"
    assert entries["rea"]["adoption"] == "existing_reuse"


def test_reference_only_and_blocked_entries_have_no_install_or_execution_claim():
    entries = _entries()
    for repo_id in ("awesome-reverse-engineer-anything", "cc-switch", "prompts-chat"):
        item = entries[repo_id]
        assert item["adoption"] == "reference_only"
        assert item["runtime"]["installed"] is False
        assert item["runtime"]["executed"] is False
        assert item["runtime"]["enabled"] is False
    blocked = entries["open-reverselab"]
    assert blocked["adoption"] == "blocked_legal_review"
    assert blocked["runtime"]["installed"] is False
    assert blocked["runtime"]["executed"] is False


def test_prompts_chat_is_catalog_only_with_dual_license_boundary():
    item = _entries()["prompts-chat"]
    assert item["license"]["application"] == "MIT"
    assert item["license"]["prompt_data"] == "CC0-1.0"
    assert item["adoption"] == "reference_only"
    assert item["runtime"]["enabled"] is False


def test_rust_anything_install_plan_isolated_and_integrity_pinned(tmp_path):
    plan = ext.install_plan("rust-anything", tmp_path)
    assert plan["tool_id"] == "rust-anything"
    assert plan["argv"][0].endswith("npm") or plan["argv"][0] == "npm"
    assert "--ignore-scripts" in plan["argv"]
    assert "--global" not in plan["argv"] and "-g" not in plan["argv"]
    assert "rust-anything@2.1.0" in plan["argv"]
    assert plan["integrity"].startswith("sha512-")
    assert str(tmp_path.resolve()) in " ".join(plan["argv"])
    assert plan["dry_run"] is True


def test_rust_anything_runner_never_uses_shell_or_global_install(tmp_path, monkeypatch):
    binary = tmp_path / "rust-anything" / "node_modules" / ".bin" / "rust-anything"
    binary.parent.mkdir(parents=True)
    binary.write_text("", encoding="utf-8")
    calls = []

    def fake_run(argv, **kwargs):
        calls.append((argv, kwargs))
        return ext.CompletedResult(returncode=0, stdout="rust-anything 2.1.0\n", stderr="")

    result = ext.run_safe("rust-anything", ["--version"], tmp_path, runner=fake_run)
    assert result["ok"] is True
    argv, kwargs = calls[0]
    assert argv[0] == str(binary.resolve())
    assert argv[1:] == ["--version"]
    assert kwargs["shell"] is False
    assert kwargs["timeout"] <= 30


def test_universal_os_isolated_and_mcp_disabled_by_default(tmp_path):
    plan = ext.install_plan("universal-os", tmp_path)
    assert plan["tool_id"] == "universal-os"
    assert plan["dry_run"] is True
    assert plan["mcp_enabled"] is False
    environment = ext.isolated_environment("universal-os", tmp_path, base_env={"HOME": "/home/real"})
    assert environment["UOS_HOME"] == str((tmp_path / "universal-os" / "home").resolve())
    assert environment["HOME"] != "/home/real"


def test_universal_os_never_accepts_iso_or_vm_execution_in_this_scope(tmp_path):
    for args in (["analyze", "--iso", "/tmp/target.iso"], ["boot", "--image", "x.iso"], ["qemu"]):
        with pytest.raises(ext.UnsafeInvocationError):
            ext.run_safe("universal-os", list(args), tmp_path, runner=lambda *a, **k: None)


def test_caveman_environment_disables_telemetry_cloud_and_global_state(tmp_path):
    environment = ext.isolated_environment(
        "caveman", tmp_path,
        base_env={"HOME": "/home/real", "CAVE_TOKEN": "must-not-leak", "DO_NOT_TRACK": "0",
                  "CAVEMAN_TELEMETRY": "1", "CAVEMAN_OFFLINE": "0"},
    )
    assert environment["DO_NOT_TRACK"] == "1"
    assert environment["CAVEMAN_TELEMETRY"] == "0"
    assert environment["CAVEMAN_OFFLINE"] == "1"
    assert environment["CAVEMAN_HOME"] == str((tmp_path / "caveman" / "home").resolve())
    assert environment["HOME"] != "/home/real"
    assert "CAVE_TOKEN" not in environment


def test_caveman_runner_rejects_setup_login_and_agent_install_commands(tmp_path):
    for args in (["setup"], ["login"], ["claude"], ["install", "hooks"], ["providers", "cloud", "on"]):
        with pytest.raises(ext.UnsafeInvocationError):
            ext.run_safe("caveman", list(args), tmp_path, runner=lambda *a, **k: None)


def test_only_selected_anthropic_skills_are_imported_with_license_and_hashes():
    root = ROOT / ".opencode" / "skills"
    for slug in ("mcp-builder", "skill-creator"):
        directory = root / slug
        assert (directory / "SKILL.md").is_file()
        assert (directory / "LICENSE.txt").is_file()
        source = json.loads((directory / "source.json").read_text(encoding="utf-8"))
        assert source["repository"] == "anthropics/skills"
        assert source["commit"] == "e4bb5d960d87126ff3b3a8af1a104b7db67560ba"
        assert source["license"] == "Apache-2.0"
        assert source["sha256"]
    assert not (root / "anthropic-skills").exists()


def test_imported_skills_are_not_implicitly_activated():
    for slug in ("mcp-builder", "skill-creator"):
        frontmatter = (ROOT / ".opencode" / "skills" / slug / "SKILL.md").read_text(encoding="utf-8")[:1500]
        assert "allow_implicit_invocation: false" in frontmatter or "disable-model-invocation: true" in frontmatter
        metadata = json.loads((ROOT / ".opencode" / "skills" / slug / "source.json").read_text(encoding="utf-8"))
        assert metadata["activation"] == "explicit_only"


def test_existing_rea_install_is_reused_without_upgrade_or_duplicate():
    item = _entries()["rea"]
    assert item["adoption"] == "existing_reuse"
    assert item["source"]["version"] == "6.8.0"
    assert item["runtime"]["installed"] is True
    assert item["runtime"]["upgrade_performed"] is False
    assert item["runtime"]["duplicate_install"] is False


def test_catalog_does_not_expose_unapproved_mcp_servers():
    entries = ext.load_manifest()["repositories"]
    assert all(item["runtime"]["mcp_enabled"] is False for item in entries if item["id"] != "rea")
    assert all(item.get("mcp_config") is None for item in entries)
