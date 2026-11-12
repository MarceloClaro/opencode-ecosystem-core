"""R1109 — testes herméticos do checkpoint automático commit+push."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
AUTOCOMMIT = ROOT / "scripts" / "autocommit_push.sh"
HOOK_INSTALLER = ROOT / "scripts" / "install_autocommit_hooks.sh"


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, text=True, capture_output=True, check=True
    )


def _make_repo(tmp_path: Path) -> tuple[Path, Path]:
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "user.email", "test@example.com")
    (repo / "scripts").mkdir()
    shutil.copy2(AUTOCOMMIT, repo / "scripts" / "autocommit_push.sh")
    shutil.copy2(HOOK_INSTALLER, repo / "scripts" / "install_autocommit_hooks.sh")
    (repo / "scripts" / "autocommit_push.sh").chmod(0o700)
    (repo / "scripts" / "install_autocommit_hooks.sh").chmod(0o700)
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    _git(repo, "add", "a.txt", "scripts")
    _git(repo, "commit", "-m", "initial")
    _git(repo, "remote", "add", "origin", str(remote))
    _git(repo, "push", "-u", "origin", "main")
    return repo, remote


def _run(repo: Path, *args: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["XDG_STATE_HOME"] = str(repo.parent / "state")
    env["OPENCODE_GITHUB_PAT_FILE"] = str(repo / ".no-token")
    env.pop("GITHUB_TOKEN", None)
    return subprocess.run(
        [str(repo / "scripts" / "autocommit_push.sh"), *args],
        cwd=repo, text=True, capture_output=True, env=env, timeout=120,
    )


def test_autocommit_commits_and_pushes_to_local_remote(tmp_path):
    repo, remote = _make_repo(tmp_path)
    (repo / "a.txt").write_text("a\nb\n", encoding="utf-8")

    result = _run(repo)

    assert result.returncode == 0, result.stderr
    assert _git(repo, "status", "--porcelain").stdout.strip() == ""
    log = _git(remote, "log", "--oneline", "main").stdout
    assert len(log.strip().splitlines()) == 2
    assert "chore(auto): checkpoint" in log


def test_autocommit_noop_does_not_create_commit(tmp_path):
    repo, _ = _make_repo(tmp_path)
    before = _git(repo, "rev-parse", "HEAD").stdout.strip()

    result = _run(repo)

    assert result.returncode == 0
    assert _git(repo, "rev-parse", "HEAD").stdout.strip() == before


def test_autocommit_rejects_file_above_50mb(tmp_path):
    repo, remote = _make_repo(tmp_path)
    big = repo / "big.bin"
    with big.open("wb") as handle:
        handle.truncate(51 * 1024 * 1024)

    result = _run(repo)

    assert result.returncode == 0
    log = _git(remote, "log", "--oneline", "main").stdout
    assert len(log.strip().splitlines()) == 1
    log_file = repo.parent / "state" / "opencode" / "autocommit-push.log"
    assert "50 MB" in log_file.read_text(encoding="utf-8")


def test_hook_installer_creates_executable_post_commit(tmp_path):
    repo, _ = _make_repo(tmp_path)

    result = subprocess.run(
        [str(repo / "scripts" / "install_autocommit_hooks.sh")],
        cwd=repo, text=True, capture_output=True, timeout=30,
    )

    assert result.returncode == 0, result.stderr
    hook = repo / ".git" / "hooks" / "post-commit"
    assert hook.is_file()
    assert os.access(hook, os.X_OK)
    assert "autocommit_push.sh" in hook.read_text(encoding="utf-8")
