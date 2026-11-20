"""Offline tests for the conditional, isolated OpenReverseLab installation."""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PIN = "c42da86aadcbea4f2dd20822653f83da5f6aba54"
LOCK_BLOB = "30c5bbb363442264d3b0581e33455a791944196b"
FIXTURES = {
    "LICENSE": b"Apache License\nVersion 2.0, January 2004\n",
    "DISCLAIMER.md": b"upstream disclaimer fixture\n",
    "tools/skills/mcp/ReverseLabToolsMCP/pyproject.toml": (
        b'[project]\nname = "reverselab-tools-mcp"\nversion = "0.1.0"\n'
        b'license = "GPL-3.0-only"\nrequires-python = ">=3.10"\n'
    ),
    "tools/skills/mcp/ReverseLabToolsMCP/reverse_lab_tools_mcp.py": (
        b'raise RuntimeError("upstream MCP must never be started by installer")\n'
    ),
    "tools/skills/mcp/ReverseLabToolsMCP/uv.lock": b"version = 1\n# locked test fixture\n",
}


def _adapter():
    module_path = ROOT / "integrations" / "open_reverselab.py"
    assert module_path.is_file()
    sys.modules.pop("integrations.open_reverselab", None)
    return importlib.import_module("integrations.open_reverselab")


def _git_blob(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def _write_checkout(root: Path) -> None:
    (root / ".git").mkdir(parents=True)
    for relative, content in FIXTURES.items():
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)


def _command_runner(monkeypatch, root_reference: dict[str, Path], calls: list):
    """Model only fixed Git metadata operations and uv sync; never run upstream."""

    def runner(argv, **kwargs):
        argv = list(argv)
        calls.append((argv, kwargs))
        assert kwargs["shell"] is False
        assert kwargs["timeout"] <= 600

        if "clone" in argv:
            destination = Path(argv[-1])
            destination.mkdir(parents=True)
            (destination / ".git").mkdir()
            root_reference["checkout"] = destination
            return subprocess.CompletedProcess(argv, 0, "cloned", "")

        if "checkout" in argv and "--detach" in argv:
            assert argv[-1] == PIN
            checkout = root_reference["checkout"]
            for relative, content in FIXTURES.items():
                destination = checkout / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(content)
            return subprocess.CompletedProcess(argv, 0, "", "")

        if argv[:1] and Path(argv[0]).name == "git":
            root = Path(argv[argv.index("-C") + 1]) if "-C" in argv else root_reference["checkout"]
            if argv[-2:] == ["rev-parse", "--show-toplevel"]:
                stdout = str(root)
            elif argv[-2:] == ["rev-parse", "HEAD"]:
                stdout = PIN
            elif argv[-2:] == ["--porcelain=v1", "--untracked-files=all"]:
                stdout = ""
            elif len(argv) >= 2 and argv[-2] == "rev-parse" and argv[-1].startswith("HEAD:"):
                relative = argv[-1][len("HEAD:"):]
                stdout = _git_blob(FIXTURES[relative])
            else:
                raise AssertionError(f"unexpected Git argv: {argv!r}")
            return subprocess.CompletedProcess(argv, 0, stdout, "")

        if Path(argv[0]).name == "uv" and "sync" in argv:
            environment = kwargs["env"]
            venv = Path(environment["UV_PROJECT_ENVIRONMENT"])
            python = venv / "bin" / "python"
            python.parent.mkdir(parents=True, exist_ok=True)
            python.write_bytes(b"fixture python executable placeholder; never invoked")
            python.chmod(0o700)
            return subprocess.CompletedProcess(argv, 0, "sync complete", "")

        raise AssertionError(f"installer attempted an unapproved command: {argv!r}")

    return runner


def _receipt_for(adapter, checkout: Path) -> dict:
    paths = adapter.installation_paths(checkout)
    return adapter.create_install_receipt(paths, installed_at="2026-11-20T12:00:00Z")


def test_install_plan_pins_commit_lock_and_separates_checkout_environment_cache(monkeypatch, tmp_path):
    adapter = _adapter()
    checkout = tmp_path / "managed" / "open-reverselab"
    monkeypatch.setattr(adapter, "default_install_root", lambda: checkout)
    monkeypatch.setenv("GITHUB_TOKEN", "must-not-leak")

    plan = adapter.install_plan()

    paths = plan["paths"]
    assert plan["source"]["commit"] == PIN
    assert plan["source"]["lockfile_git_blob"] == LOCK_BLOB
    assert paths["checkout"] == str(checkout)
    assert paths["environment"] != paths["checkout"]
    assert paths["cache"] != paths["checkout"]
    assert paths["private_home"] != str(Path.home())
    assert Path(paths["environment"]).parent == checkout.parent
    assert paths["checkout"] != str(ROOT) and str(ROOT) not in paths["checkout"]
    sync = plan["commands"]["uv_sync"]
    assert "--locked" in sync
    assert "--no-install-project" in sync
    assert "--no-build" in sync
    assert "reverse_lab_tools_mcp.py" not in " ".join(sync)
    assert plan["environment"]["UV_PROJECT_ENVIRONMENT"] == paths["environment"]
    assert plan["environment"]["UV_CACHE_DIR"] == paths["cache"]
    assert "GITHUB_TOKEN" not in plan["environment"]
    assert plan["mcp_enabled"] is False
    assert plan["dry_run"] is True


def test_install_without_yes_is_dry_run_and_creates_nothing(monkeypatch, tmp_path, capsys):
    adapter = _adapter()
    checkout = tmp_path / "managed" / "open-reverselab"
    monkeypatch.setattr(adapter, "default_install_root", lambda: checkout)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("dry-run invoked a subprocess")

    monkeypatch.setattr(adapter.subprocess, "run", forbidden)
    result = adapter.install_isolated()

    assert result["dry_run"] is True
    assert result["status"] == "dry_run"
    assert not checkout.parent.exists()
    assert adapter.main(["install"]) == 0
    cli_result = json.loads(capsys.readouterr().out)
    assert cli_result["status"] == "dry_run"
    assert not checkout.parent.exists()


def test_install_success_uses_staging_locked_wheels_and_never_starts_mcp(monkeypatch, tmp_path):
    adapter = _adapter()
    checkout = tmp_path / "managed" / "open-reverselab"
    monkeypatch.setattr(adapter, "default_install_root", lambda: checkout)
    monkeypatch.setattr(adapter, "LOCKFILE_BLOB_ID", _git_blob(FIXTURES["tools/skills/mcp/ReverseLabToolsMCP/uv.lock"]))
    calls = []
    root_reference: dict[str, Path] = {}
    runner = _command_runner(monkeypatch, root_reference, calls)
    active_config = ROOT / "opencode.json"
    before_config = active_config.read_bytes() if active_config.exists() else None

    result = adapter.install_isolated(yes=True, runner=runner)

    assert result["status"] == "installed"
    assert result["runtime"]["installed"] is True
    assert result["runtime"]["upstream_mcp_executed"] is False
    assert result["runtime"]["mcp_enabled"] is False
    assert result["runtime"]["target_analysis"] is False
    assert checkout.is_dir()
    assert Path(result["paths"]["environment"]).is_dir()
    commands = [argv for argv, _ in calls]
    assert any("clone" in argv for argv in commands)
    assert any("checkout" in argv and "--detach" in argv and PIN in argv for argv in commands)
    uv = next(argv for argv in commands if Path(argv[0]).name == "uv")
    assert uv[1] == "sync"
    assert {"--locked", "--no-install-project", "--no-build"}.issubset(set(uv))
    assert not any(
        "reverse_lab_tools_mcp.py" in part and ("python" in argv or "run" in argv)
        for argv in commands for part in argv
    )
    assert not any("opencode.json" in part for argv in commands for part in argv)
    assert all(kwargs["shell"] is False for _, kwargs in calls)
    if before_config is not None:
        assert active_config.read_bytes() == before_config

    receipt_path = Path(result["paths"]["receipt"])
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["source_commit"] == PIN
    assert receipt["source_lockfile"]["git_blob"] == adapter.LOCKFILE_BLOB_ID
    assert receipt["uv_sync"] == {
        "status": "success",
        "locked": True,
        "no_install_project": True,
        "no_build": True,
        "returncode": 0,
    }
    assert receipt["runtime"]["upstream_mcp_executed"] is False
    assert receipt["runtime"]["mcp_enabled"] is False
    assert receipt["authorization"]["legal_review"] == "not_performed"


def test_install_lockfile_must_match_pinned_git_blob(monkeypatch, tmp_path):
    adapter = _adapter()
    checkout = tmp_path / "checkout"
    _write_checkout(checkout)
    pinned_fixture_blob = _git_blob(FIXTURES["tools/skills/mcp/ReverseLabToolsMCP/uv.lock"])
    monkeypatch.setattr(adapter, "LOCKFILE_BLOB_ID", pinned_fixture_blob)
    calls = []

    def git_runner(argv, **kwargs):
        calls.append((list(argv), kwargs))
        relative = argv[-1][len("HEAD:"):]
        return subprocess.CompletedProcess(argv, 0, pinned_fixture_blob, "")

    accepted = adapter.verify_pinned_lockfile(checkout, runner=git_runner)
    assert accepted["valid"] is True
    lockfile = checkout / "tools/skills/mcp/ReverseLabToolsMCP/uv.lock"
    lockfile.write_bytes(b"tampered lockfile\n")
    rejected = adapter.verify_pinned_lockfile(checkout, runner=git_runner)
    assert rejected["valid"] is False
    assert rejected["status"] == "lockfile_blob_mismatch"
    assert calls and all(kwargs["shell"] is False for _, kwargs in calls)


def test_valid_managed_install_is_idempotent_without_subprocesses(monkeypatch, tmp_path):
    adapter = _adapter()
    checkout = tmp_path / "managed" / "open-reverselab"
    monkeypatch.setattr(adapter, "default_install_root", lambda: checkout)
    monkeypatch.setattr(adapter, "LOCKFILE_BLOB_ID", _git_blob(FIXTURES["tools/skills/mcp/ReverseLabToolsMCP/uv.lock"]))
    _write_checkout(checkout)
    paths = adapter.installation_paths(checkout)
    python = Path(paths["environment"]) / "bin" / "python"
    python.parent.mkdir(parents=True)
    python.write_bytes(b"placeholder")
    python.chmod(0o700)
    Path(paths["receipt"]).write_text(json.dumps(_receipt_for(adapter, checkout)), encoding="utf-8")

    def forbidden(*_args, **_kwargs):
        raise AssertionError("idempotent install attempted network or subprocess work")

    result = adapter.install_isolated(yes=True, runner=forbidden)
    assert result["status"] == "already_installed"
    assert result["runtime"]["installed"] is True
    assert result["runtime"]["mcp_enabled"] is False


def test_existing_or_partial_destination_fails_closed_without_overwrite(monkeypatch, tmp_path):
    adapter = _adapter()
    checkout = tmp_path / "managed" / "open-reverselab"
    monkeypatch.setattr(adapter, "default_install_root", lambda: checkout)
    checkout.mkdir(parents=True)
    marker = checkout / "operator-data.txt"
    marker.write_text("preserve", encoding="utf-8")

    def forbidden(*_args, **_kwargs):
        raise AssertionError("conflicting destination reached subprocess")

    result = adapter.install_isolated(yes=True, runner=forbidden)
    assert result["status"] == "target_conflict"
    assert marker.read_text(encoding="utf-8") == "preserve"

    shutil_env = Path(adapter.installation_paths(checkout)["environment"])
    shutil_env.mkdir()
    checkout.rename(tmp_path / "preserved-checkout")
    partial = adapter.install_isolated(yes=True, runner=forbidden)
    assert partial["status"] == "partial_installation"
    assert shutil_env.is_dir()


def test_install_receipt_records_provenance_and_forbids_activation(monkeypatch, tmp_path):
    adapter = _adapter()
    checkout = tmp_path / "managed" / "open-reverselab"
    monkeypatch.setattr(adapter, "default_install_root", lambda: checkout)
    receipt = _receipt_for(adapter, checkout)

    assert receipt["schema_version"] == "open-reverselab-install.r1238.v1"
    assert receipt["spec_id"] == "SPEC-935-R1238"
    assert receipt["source_commit"] == PIN
    assert receipt["source_lockfile"]["path"] == "tools/skills/mcp/ReverseLabToolsMCP/uv.lock"
    assert receipt["source_lockfile"]["git_blob"] == LOCK_BLOB
    assert receipt["runtime"]["installed"] is True
    assert receipt["runtime"]["upstream_mcp_executed"] is False
    assert receipt["runtime"]["mcp_enabled"] is False
    assert receipt["runtime"]["target_analysis"] is False
    assert receipt["authorization"]["legal_review"] == "not_performed"
    assert receipt["checkout"] == str(checkout)
    assert receipt["environment"] != receipt["checkout"]

    _write_checkout(checkout)
    environment_python = Path(receipt["environment"]) / "bin" / "python"
    environment_python.parent.mkdir(parents=True)
    environment_python.write_bytes(b"placeholder")
    environment_python.chmod(0o700)
    Path(adapter.installation_paths(checkout)["receipt"]).write_text(json.dumps(receipt), encoding="utf-8")
    observed = adapter.status()
    assert observed["installation"]["status"] == "installed"
    assert observed["runtime"]["installed"] is True
    assert observed["runtime"]["mcp_enabled"] is False


def test_managed_config_uses_isolated_interpreter_but_remains_disabled(monkeypatch, tmp_path):
    adapter = _adapter()
    checkout = tmp_path / "managed" / "open-reverselab"
    monkeypatch.setattr(adapter, "default_install_root", lambda: checkout)
    monkeypatch.setattr(adapter, "LOCKFILE_BLOB_ID", _git_blob(FIXTURES["tools/skills/mcp/ReverseLabToolsMCP/uv.lock"]))
    _write_checkout(checkout)
    paths = adapter.installation_paths(checkout)
    python = Path(paths["environment"]) / "bin" / "python"
    python.parent.mkdir(parents=True)
    python.write_bytes(b"placeholder")
    python.chmod(0o700)
    Path(paths["receipt"]).write_text(json.dumps(_receipt_for(adapter, checkout)), encoding="utf-8")

    def git_runner(argv, **kwargs):
        if argv[-2:] == ["rev-parse", "--show-toplevel"]:
            stdout = str(checkout)
        elif argv[-2:] == ["rev-parse", "HEAD"]:
            stdout = PIN
        elif argv[-2:] == ["--porcelain=v1", "--untracked-files=all"]:
            stdout = ""
        elif argv[-2] == "rev-parse" and argv[-1].startswith("HEAD:"):
            relative = argv[-1][len("HEAD:"):]
            stdout = _git_blob(FIXTURES[relative])
        else:
            raise AssertionError(f"unexpected Git argv: {argv!r}")
        return subprocess.CompletedProcess(argv, 0, stdout, "")

    candidate = adapter.mcp_config(checkout, runner=git_runner)
    server = candidate["config"]["mcp"]["servers"]["reverse-lab-tools"]
    assert server["disabled"] is True
    assert server["command"][0] == str(python)
    assert server["command"][1] == str(checkout / "tools/skills/mcp/ReverseLabToolsMCP/reverse_lab_tools_mcp.py")
    assert candidate["runtime"]["installed"] is True
    assert candidate["runtime"]["executed"] is False
    assert candidate["runtime"]["mcp_enabled"] is False
