"""Contratos RED da SPEC-935-R450 para fronteiras de segurança."""

from __future__ import annotations

import os
import shutil
import shlex
import stat
import subprocess
from pathlib import Path

import pytest

import integrations.deepmind.formal_verifier as formal_verifier_module
from integrations.deepmind.formal_verifier import FormalProofVerifier


ROOT = Path(__file__).resolve().parent.parent
COMMON_PATH_SAFETY = ROOT / "installer/common/path_safety.sh"
COMMON_CLI_INSTALLER = ROOT / "installer/common/install_clis.sh"
SHELL_INSTALLERS = (
    ROOT / "installer/linux/install.sh",
    ROOT / "installer/macos/install.sh",
    ROOT / "installer/windows/provision.sh",
)
WINDOWS_WRAPPER = ROOT / "installer/windows/Install-OpenCodeEcosystem.ps1"
INSTALLER_GUIDE = ROOT / "installer/README.md"
WINDOWS_GUIDE = ROOT / "installer/windows/README.md"


def _run_bash(script: str, *, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", script],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.skipif(not formal_verifier_module.SYMPY_AVAILABLE, reason="SymPy indisponível")
def test_formal_text_is_restricted_before_any_sympify_call(monkeypatch: pytest.MonkeyPatch) -> None:
    verifier = FormalProofVerifier()
    valid, _ = verifier.verify_algebraic_identity(
        "sin(x)**2 + cos(x)**2", "1"
    )
    assert valid is True

    calls: list[tuple[object, ...]] = []

    def forbidden_sympify(*args: object, **kwargs: object) -> object:
        calls.append(args)
        raise AssertionError("texto externo não pode alcançar sympify")

    monkeypatch.setattr(formal_verifier_module, "sympify", forbidden_sympify, raising=False)
    for unsafe in (
        "__import__('os')",
        "open('arquivo')",
        "x.__class__",
        "x[0]",
        "(lambda: 0)()",
        "_private_symbol",
        "x + " * 300,
    ):
        verified, message = verifier.verify_algebraic_identity(unsafe, "0")
        assert verified is False
        assert "recusada" in message
        assert verifier.search_counterexamples(unsafe, ["x"]) == []

    assert calls == []
    source = (ROOT / "integrations/deepmind/formal_verifier.py").read_text(encoding="utf-8")
    assert "sympify(" not in source


def test_ecosystem_directory_helper_rejects_shell_and_launcher_metacharacters(
    tmp_path: Path,
) -> None:
    home = tmp_path / "home"
    home.mkdir()
    safe_path = home / "ecosystem-1.0"
    invalid_paths = (
        "relative",
        str(home / "with space"),
        str(home / "bad$(touch pwned)"),
        str(home / "bad`id`"),
        str(home / "bad;echo"),
        str(home / "bad'quote"),
        str(home / "bad\rreturn"),
        str(home / "bad\nnewline"),
        "/outside/home/ecosystem",
    )
    commands = [
        f"source {shlex.quote(str(COMMON_PATH_SAFETY))}",
        f"validate_ecosystem_dir {shlex.quote(str(safe_path))}",
    ]
    commands.extend(
        f"! validate_ecosystem_dir {shlex.quote(path)}" for path in invalid_paths
    )
    env = {**os.environ, "HOME": str(home)}
    result = _run_bash("\n".join(commands), env=env)
    assert result.returncode == 0, result.stderr

    outside = tmp_path / "outside"
    outside.mkdir()
    linked_path = home / "linked"
    linked_path.symlink_to(outside, target_is_directory=True)
    parent_before_clone = _run_bash(
        "\n".join(
            (
                f"source {shlex.quote(str(COMMON_PATH_SAFETY))}",
                "type validate_ecosystem_dir_no_symlink_prefix >/dev/null || exit 1",
                'if validate_ecosystem_dir_no_symlink_prefix "$HOME/linked/new-checkout"; then exit 1; fi',
            )
        ),
        env=env,
    )
    assert parent_before_clone.returncode == 0, parent_before_clone.stderr
    canonicalization = _run_bash(
        "\n".join(
            (
                f"source {shlex.quote(str(COMMON_PATH_SAFETY))}",
                'if canonicalize_ecosystem_dir "$HOME/linked"; then exit 1; fi',
            )
        ),
        env=env,
    )
    assert canonicalization.returncode == 0, canonicalization.stderr

    for installer in SHELL_INSTALLERS:
        content = installer.read_text(encoding="utf-8")
        assert "path_safety.sh" in content
        assert 'validate_ecosystem_dir "$ECO_DIR"' in content
        assert 'canonicalize_ecosystem_dir "$ECO_DIR"' in content
        assert 'validate_ecosystem_dir_no_symlink_prefix "$ECO_DIR"' in content
        assert content.index('validate_ecosystem_dir_no_symlink_prefix "$ECO_DIR"') < content.index(
            "git clone"
        )
        assert content.index('validate_ecosystem_dir "$ECO_DIR"') < content.index(
            'add_line "alias ecosystem='
        )
        assert 'cd -- "$ECO_DIR"' in content


def test_artifact_cache_rejects_override_and_symlinked_parent_without_permission_changes(
    tmp_path: Path,
) -> None:
    home = tmp_path / "home"
    home.mkdir()
    sentinel = tmp_path / "sentinel"
    sentinel.mkdir(mode=0o755)
    sentinel_mode = stat.S_IMODE(sentinel.stat().st_mode)
    common = shlex.quote(str(COMMON_CLI_INSTALLER))

    rejected_override = _run_bash(
        "\n".join(
            (
                f"source {common}",
                "if ensure_private_artifact_cache; then exit 1; fi",
            )
        ),
        env={
            **os.environ,
            "HOME": str(home),
            "ECOSYSTEM_ARTIFACT_CACHE": str(sentinel),
        },
    )
    assert rejected_override.returncode == 0, rejected_override.stderr
    assert stat.S_IMODE(sentinel.stat().st_mode) == sentinel_mode

    default_cache = _run_bash(
        "\n".join(
            (
                f"source {common}",
                "unset ECOSYSTEM_ARTIFACT_CACHE",
                "ensure_private_artifact_cache",
                'cache="$(artifact_cache_dir)"',
                'test -d "$cache" && test ! -L "$cache"',
                'test "$(stat -c %a "$cache")" = 700',
            )
        ),
        env={**os.environ, "HOME": str(home)},
    )
    assert default_cache.returncode == 0, default_cache.stderr

    symlink_home = tmp_path / "symlink-home"
    symlink_home.mkdir()
    (symlink_home / ".cache").mkdir()
    symlink_target = tmp_path / "symlink-target"
    symlink_target.mkdir()
    (symlink_home / ".cache" / "opencode-ecosystem").symlink_to(symlink_target)
    rejected_symlink = _run_bash(
        "\n".join(
            (
                f"source {common}",
                "unset ECOSYSTEM_ARTIFACT_CACHE",
                "if ensure_private_artifact_cache; then exit 1; fi",
            )
        ),
        env={**os.environ, "HOME": str(symlink_home)},
    )
    assert rejected_symlink.returncode == 0, rejected_symlink.stderr
    assert not (symlink_target / "artifacts").exists()

    stale_home = tmp_path / "stale-home"
    stale_cache = stale_home / ".cache" / "opencode-ecosystem" / "artifacts"
    stale_cache.mkdir(parents=True)
    stale_cache.chmod(0o755)
    rejected_legacy_mode = _run_bash(
        "\n".join(
            (
                f"source {common}",
                "unset ECOSYSTEM_ARTIFACT_CACHE",
                "if ensure_private_artifact_cache; then exit 1; fi",
            )
        ),
        env={**os.environ, "HOME": str(stale_home)},
    )
    assert rejected_legacy_mode.returncode == 0, rejected_legacy_mode.stderr
    assert stat.S_IMODE(stale_cache.stat().st_mode) == 0o755
    common_source = COMMON_CLI_INSTALLER.read_text(encoding="utf-8")
    assert 'chmod 0700 "$cache_root"' not in common_source


def test_windows_wrapper_requires_manual_reentry_after_reboot() -> None:
    content = WINDOWS_WRAPPER.read_text(encoding="utf-8")

    assert "RunOnce" not in content
    assert "Set-ItemProperty" not in content
    assert "Assert-InstallationInputs" in content
    assert "retomada manual" in content.lower()
    assert "PathSafetySha256" in content
    assert "Test-VerifiedFile -Path $tempPathSafety -ExpectedSha256 $PathSafetySha256" in content
    assert "-PathSafetyHash $PathSafetySha256" in content
    assert "mktemp -d" in content
    assert 'rm -rf "`$root"' not in content
    assert "Select-Object -Last 1" in content
    assert content.index("Assert-InstallationInputs") < content.index(
        "& $WslExe --install -d $Distro"
    )

    pwsh = shutil.which("pwsh")
    if pwsh is not None:
        result = subprocess.run(
            [
                pwsh,
                "-NoProfile",
                "-Command",
                f"[void][System.Management.Automation.Language.Parser]::ParseFile({str(WINDOWS_WRAPPER)!r}, [ref]$null, [ref]$null)",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr


def test_installer_guides_describe_the_new_fail_closed_boundaries() -> None:
    installer_guide = INSTALLER_GUIDE.read_text(encoding="utf-8")
    windows_guide = WINDOWS_GUIDE.read_text(encoding="utf-8")

    assert "PathSafetySha256" in installer_guide
    assert "sob `HOME`" in installer_guide
    assert "ECOSYSTEM_ARTIFACT_CACHE" in installer_guide
    assert "retomada manual" in windows_guide.lower()
    assert "PathSafetySha256" in windows_guide
