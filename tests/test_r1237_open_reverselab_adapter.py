"""Offline contract tests for the optional OpenReverseLab adapter."""

from __future__ import annotations

from copy import deepcopy
import importlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PIN = "c42da86aadcbea4f2dd20822653f83da5f6aba54"
DISCLAIMER_BLOB = "025efb705062b5782b826d317388674bfe88a5ff"


def _adapter():
    module_path = ROOT / "integrations" / "open_reverselab.py"
    assert module_path.is_file(), "OpenReverseLab Core adapter has not been implemented"
    sys.modules.pop("integrations.open_reverselab", None)
    return importlib.import_module("integrations.open_reverselab")


def _checkout(tmp_path: Path) -> Path:
    root = tmp_path / "open-reverselab"
    mcp = root / "tools" / "skills" / "mcp" / "ReverseLabToolsMCP"
    mcp.mkdir(parents=True)
    (root / ".git").mkdir()
    (root / "LICENSE").write_text("Apache License\nVersion 2.0, January 2004\n", encoding="utf-8")
    (root / "DISCLAIMER.md").write_text("upstream disclaimer fixture\n", encoding="utf-8")
    (mcp / "pyproject.toml").write_text(
        '[project]\nname = "reverselab-tools-mcp"\nversion = "0.1.0"\n'
        'license = "GPL-3.0-only"\nrequires-python = ">=3.10"\n',
        encoding="utf-8",
    )
    # Deliberately not executable Python: the adapter must inspect, never import/run it.
    (mcp / "reverse_lab_tools_mcp.py").write_text(
        'raise RuntimeError("upstream entrypoint must not be executed")\n', encoding="utf-8"
    )
    return root


def _git_runner(root: Path, *, commit: str = PIN, dirty: str = "", calls: list | None = None):
    observed_calls = calls if calls is not None else []

    def runner(argv, **kwargs):
        observed_calls.append((list(argv), kwargs))
        if argv[-2:] == ["rev-parse", "--show-toplevel"]:
            stdout = str(root)
        elif argv[-2:] == ["rev-parse", "HEAD"]:
            stdout = commit
        elif argv[-2:] == ["--porcelain=v1", "--untracked-files=all"]:
            stdout = dirty
        else:
            raise AssertionError(f"unexpected subprocess argv: {argv!r}")
        return subprocess.CompletedProcess(argv, 0, stdout, "")

    return runner


def test_manifest_pins_source_and_preserves_license_boundary_and_authorization_scope():
    adapter = _adapter()
    manifest = adapter.load_manifest()
    assert adapter.validate_manifest(manifest) == []
    assert manifest["source"]["commit"] == PIN
    assert manifest["source"]["root_license"]["declared"] == "Apache-2.0"
    assert manifest["source"]["nested_mcp"]["declared"] == "GPL-3.0-only"
    assert manifest["source"]["nested_mcp"]["version"] == "0.1.0"
    assert manifest["source"]["disclaimer"]["github_blob"] == DISCLAIMER_BLOB
    assert manifest["authorization"]["scope"] == "core_adapter_only"
    assert manifest["authorization"]["legal_review"] == "not_performed"
    assert manifest["runtime"] == {
        "installed": False,
        "executed": False,
        "enabled": False,
        "mcp_enabled": False,
        "content_imported": False,
    }
    assert manifest["default_config"]["disabled"] is True
    assert manifest["license_status"] != "approved"


def test_manifest_validation_fails_closed_on_license_or_runtime_drift():
    adapter = _adapter()
    manifest = adapter.load_manifest()
    broken = deepcopy(manifest)
    broken["source"]["nested_mcp"]["declared"] = "Apache-2.0"
    assert any("nested_mcp" in error for error in adapter.validate_manifest(broken))

    broken = deepcopy(manifest)
    broken["runtime"]["mcp_enabled"] = True
    assert any("mcp_enabled" in error for error in adapter.validate_manifest(broken))

    broken = deepcopy(manifest)
    broken["authorization"]["legal_review"] = "approved"
    assert any("legal_review" in error for error in adapter.validate_manifest(broken))


def test_historical_r1232_block_remains_unchanged():
    adapter = _adapter()
    historical = json.loads((ROOT / "federation" / "repository-curation-r1232.json").read_text(encoding="utf-8"))
    current = {item["id"]: item for item in historical["repositories"]}
    entry = current["open-reverselab"]
    assert entry["integration_status"] == "blocked_legal_review"
    assert entry["license_status"] == "human_review_required"
    assert all(value is False for value in entry["runtime"].values())


def test_inspection_accepts_only_exact_clean_local_checkout_without_running_project_code(tmp_path):
    adapter = _adapter()
    root = _checkout(tmp_path)
    calls = []
    result = adapter.inspect_checkout(root, runner=_git_runner(root, calls=calls))
    assert result["status"] == "ready"
    assert result["commit"] == PIN
    assert result["license"] == "GPL-3.0-only"
    assert result["project_version"] == "0.1.0"
    assert len(calls) == 3
    assert all(kwargs["shell"] is False for _, kwargs in calls)
    assert all(kwargs["timeout"] <= 10 for _, kwargs in calls)
    assert all(argv[0] == "git" for argv, _ in calls)


def test_inspection_rejects_wrong_commit_dirty_tree_and_missing_mcp_files(tmp_path):
    adapter = _adapter()
    root = _checkout(tmp_path)
    relative = adapter.inspect_checkout("relative/path", runner=_git_runner(root))
    assert relative["status"] == "path_not_absolute"

    wrong = adapter.inspect_checkout(root, runner=_git_runner(root, commit="f" * 40))
    assert wrong["status"] == "commit_mismatch"

    dirty = adapter.inspect_checkout(root, runner=_git_runner(root, dirty=" M README.md\n"))
    assert dirty["status"] == "dirty_checkout"

    (root / "tools" / "skills" / "mcp" / "ReverseLabToolsMCP" / "reverse_lab_tools_mcp.py").unlink()
    missing = adapter.inspect_checkout(root, runner=_git_runner(root))
    assert missing["status"] == "required_file_missing"


def test_inspection_rejects_upstream_license_declaration_drift(tmp_path):
    adapter = _adapter()
    root = _checkout(tmp_path)
    project_file = root / "tools" / "skills" / "mcp" / "ReverseLabToolsMCP" / "pyproject.toml"
    project_file.write_text(project_file.read_text(encoding="utf-8").replace("GPL-3.0-only", "MIT"), encoding="utf-8")
    mcp_license = adapter.inspect_checkout(root, runner=_git_runner(root))
    assert mcp_license["status"] == "mcp_license_mismatch"

    (root / "LICENSE").write_text("MIT License\n", encoding="utf-8")
    root_license = adapter.inspect_checkout(root, runner=_git_runner(root))
    assert root_license["status"] == "root_license_mismatch"


def test_inspection_rejects_symlinked_root_and_mcp_components(tmp_path):
    adapter = _adapter()
    real = _checkout(tmp_path)
    root_link = tmp_path / "root-link"
    root_link.symlink_to(real, target_is_directory=True)
    linked_root = adapter.inspect_checkout(root_link, runner=_git_runner(real))
    assert linked_root["status"] == "symlink_path"

    mcp = real / "tools" / "skills" / "mcp" / "ReverseLabToolsMCP"
    moved = tmp_path / "mcp-real"
    mcp.rename(moved)
    mcp.symlink_to(moved, target_is_directory=True)
    linked_component = adapter.inspect_checkout(real, runner=_git_runner(real))
    assert linked_component["status"] == "symlink_path"


def test_generated_opencode_entry_is_disabled_and_never_mutates_active_config(tmp_path):
    adapter = _adapter()
    root = _checkout(tmp_path)
    active_config = ROOT / "opencode.json"
    before = active_config.read_bytes()
    before_checkout = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file() and not p.is_symlink()}
    candidate = adapter.mcp_config(root, runner=_git_runner(root))
    after = active_config.read_bytes()
    after_checkout = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file() and not p.is_symlink()}
    assert before == after
    assert before_checkout == after_checkout
    assert candidate["status"] == "candidate_disabled"
    assert candidate["runtime"]["mcp_enabled"] is False
    server = candidate["config"]["mcp"]["servers"]["reverse-lab-tools"]
    assert server["type"] == "local"
    assert server["disabled"] is True
    assert server["cwd"] == str(root.resolve())
    assert server["command"][:3] == ["uv", "run", "--no-sync"]
    assert str(root / "tools" / "skills" / "mcp" / "ReverseLabToolsMCP") in server["command"]
    assert str(root / "tools" / "skills" / "mcp" / "ReverseLabToolsMCP" / "reverse_lab_tools_mcp.py") in server["command"]
    assert candidate["requirements"][2] == "enabling the server requires a separate explicit user decision"
    assert candidate["requirements"][3] == "review inherited environment exposure before activation"


def test_config_refuses_invalid_or_unpinned_checkout(tmp_path):
    adapter = _adapter()
    root = _checkout(tmp_path)
    try:
        adapter.mcp_config(root, runner=_git_runner(root, commit="0" * 40))
    except adapter.CheckoutValidationError as error:
        assert error.status == "commit_mismatch"
    else:
        raise AssertionError("config generation must reject a non-pinned checkout")


def test_cli_status_and_config_are_read_only_json_operations(tmp_path, capsys):
    adapter = _adapter()
    root = _checkout(tmp_path)
    assert adapter.main(["status"]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["status"] == "metadata_only"
    assert status["runtime"]["mcp_enabled"] is False

    assert adapter.main(["config", "--path", str(root)], runner=_git_runner(root)) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["config"]["mcp"]["servers"]["reverse-lab-tools"]["disabled"] is True
    assert output["runtime"]["executed"] is False
