"""TDD contracts for SPEC-935-R1232; external tools are always mocked here."""

from __future__ import annotations

import json
import base64
import hashlib
from copy import deepcopy
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
    assert all(item.get("license_status") for item in manifest["repositories"])
    assert all(item.get("integration_status") for item in manifest["repositories"])


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
    assert Path(plan["argv"][0]).name == "npm"
    assert plan["argv"][1] == "pack"
    assert "--ignore-scripts" in plan["argv"]
    assert "--global" not in plan["argv"] and "-g" not in plan["argv"]
    assert "rust-anything@2.1.0" in plan["argv"]
    assert plan["integrity"].startswith("sha512-")
    assert plan["unpacked_bytes"] == 126965553
    assert str(tmp_path.resolve()) in " ".join(plan["argv"])
    assert "<verified-tarball>" in plan["install_argv_template"]
    assert plan["integrity_verification"]["before_install"] is True
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
    assert "--tool-dir" not in plan["argv"] and "--bin-dir" not in plan["argv"]
    assert plan["environment"]["UV_TOOL_DIR"] == str((tmp_path / "universal-os" / "tools").resolve())
    assert plan["environment"]["UV_TOOL_BIN_DIR"] == str((tmp_path / "universal-os" / "bin").resolve())
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
    assert environment["npm_config_registry"] == "https://registry.npmjs.org/"
    assert environment["npm_config_userconfig"].startswith(environment["CAVEMAN_HOME"])
    assert environment["npm_config_ignore_scripts"] == "true"


def test_caveman_runner_rejects_setup_login_and_agent_install_commands(tmp_path):
    for args in (["setup"], ["login"], ["claude"], ["install", "hooks"], ["providers", "cloud", "on"]):
        with pytest.raises(ext.UnsafeInvocationError):
            ext.run_safe("caveman", list(args), tmp_path, runner=lambda *a, **k: None)


def test_only_selected_anthropic_skills_are_imported_with_license_and_hashes():
    root = ROOT / ".opencode" / "skills"
    manifest_entries = _entries()
    for slug in ("mcp-builder", "skill-creator"):
        directory = root / slug
        assert (directory / "SKILL.md").is_file()
        assert (directory / "LICENSE.txt").is_file()
        source = json.loads((directory / "source.json").read_text(encoding="utf-8"))
        assert source["repository"] == "anthropics/skills"
        assert source["commit"] == "e4bb5d960d87126ff3b3a8af1a104b7db67560ba"
        assert source["license"] == "Apache-2.0"
        assert source["sha256"]
        entry = manifest_entries[f"anthropic-{slug}"]["source"]
        assert source["sha256"] == entry["imported_skill_sha256"]
        assert hashlib.sha256((directory / "source.json").read_bytes()).hexdigest() == entry["source_manifest_sha256"]
        assert len(source["files"]) == entry["imported_file_count"]
        assert source["resources_imported"].startswith("all regular files")
        for relative, record in source["files"].items():
            file_path = directory / relative
            assert file_path.is_file()
            assert hashlib.sha256(file_path.read_bytes()).hexdigest() == record["imported_sha256"]
            assert record["imported_mode"] == "100644"
            assert not (file_path.stat().st_mode & 0o111)
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


def test_status_is_read_only_local_inventory(monkeypatch):
    def should_not_run(*args, **kwargs):
        raise AssertionError("status must not launch an external process")

    monkeypatch.setattr(ext.subprocess, "run", should_not_run)
    result = ext.status()
    assert result["verification"] == "local_inventory_only"
    assert {item["id"] for item in result["repositories"]} >= {"rust-anything", "universal-os", "caveman"}


def test_install_without_confirmation_is_plan_only(tmp_path):
    def should_not_run(*args, **kwargs):
        raise AssertionError("external installer must not run without explicit confirmation")

    result = ext.install_tool("rust-anything", root=tmp_path, runner=should_not_run)
    assert result["dry_run"] is True
    assert result["argv"][1] == "pack"
    assert not (tmp_path / "rust-anything").exists()


def test_npm_integrity_mismatch_stops_before_install(tmp_path):
    calls = []

    def fake_runner(argv, **kwargs):
        calls.append((argv, kwargs))
        if argv[1] == "pack":
            destination = Path(argv[argv.index("--pack-destination") + 1])
            destination.mkdir(parents=True, exist_ok=True)
            (destination / "wrong.tgz").write_bytes(b"not-the-pinned-package")
            return ext.CompletedResult(0, json.dumps([{"integrity": "sha512-wrong", "filename": "wrong.tgz"}]), "")
        raise AssertionError("install must not run for a mismatched package integrity")

    result = ext.install_tool("rust-anything", root=tmp_path, yes=True, runner=fake_runner)
    assert result["status"] == "integrity_mismatch"
    assert result["expected_integrity"].startswith("sha512-")
    assert len(calls) == 1
    assert not (tmp_path / "rust-anything" / "node_modules").exists()


def test_npm_install_uses_only_tarball_verified_against_pinned_integrity(tmp_path, monkeypatch):
    calls = []
    tarball_bytes = b"verified-by-npm-integrity-field"
    expected = "sha512-" + base64.b64encode(hashlib.sha512(tarball_bytes).digest()).decode("ascii")
    original_entry = ext._entry

    def entry_with_test_integrity(tool_id):
        item = original_entry(tool_id)
        if tool_id == "rust-anything":
            item = deepcopy(item)
            item["source"]["integrity"] = expected
        return item

    monkeypatch.setattr(ext, "_entry", entry_with_test_integrity)

    def fake_runner(argv, **kwargs):
        calls.append((argv, kwargs))
        assert kwargs["shell"] is False
        assert "--ignore-scripts" in argv
        if argv[1] == "pack":
            destination = Path(argv[argv.index("--pack-destination") + 1])
            destination.mkdir(parents=True, exist_ok=True)
            (destination / "rust-anything-2.1.0.tgz").write_bytes(tarball_bytes)
            return ext.CompletedResult(
                0,
                json.dumps([{"integrity": expected, "filename": "rust-anything-2.1.0.tgz"}]),
                "",
            )
        assert argv[1] == "install"
        assert argv[-1].endswith("rust-anything-2.1.0.tgz")
        assert str((tmp_path / "rust-anything").resolve()) in argv
        assert kwargs["env"]["HOME"] == str((tmp_path / "rust-anything" / "home").resolve())
        return ext.CompletedResult(0, "ok", "")

    result = ext.install_tool("rust-anything", root=tmp_path, yes=True, runner=fake_runner)
    assert result["status"] == "installed"
    assert result["integrity_verified"] is True
    assert [call[0][1] for call in calls] == ["pack", "install"]


def test_manifest_records_license_and_adoption_states_without_collapsing_them():
    entries = _entries()
    assert entries["open-reverselab"]["license_status"] == "human_review_required"
    assert entries["open-reverselab"]["integration_status"] == "blocked_legal_review"
    assert entries["prompts-chat"]["license_status"] == "source_declared_unreviewed"
    assert entries["prompts-chat"]["integration_status"] == "reference_only"
    assert entries["anthropic-mcp-builder"]["integration_status"] == "imported_explicit_only"
    assert entries["rust-anything"]["integration_status"] == "planned_isolated"


def test_manifest_policy_validation_fails_closed_for_contradictory_states():
    manifest = ext.load_manifest()
    broken = deepcopy(manifest)
    open_reverselab = next(item for item in broken["repositories"] if item["id"] == "open-reverselab")
    open_reverselab["runtime"]["installed"] = True
    assert any("open-reverselab" in error for error in ext.validate_manifest(broken))

    broken = deepcopy(manifest)
    prompts = next(item for item in broken["repositories"] if item["id"] == "prompts-chat")
    prompts["license_status"] = "approved"
    assert any("prompts-chat: license_status" in error for error in ext.validate_manifest(broken))
