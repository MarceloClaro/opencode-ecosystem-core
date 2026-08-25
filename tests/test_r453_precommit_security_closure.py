"""Contratos RED da SPEC-935-R453 para bloqueadores pré-commit."""

from __future__ import annotations

import importlib
import re
import shlex
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from sdd.spec_engine import (
    AcceptanceCriterion,
    SpecRegistry,
    SpecVerifier,
    Specification,
    _issue_trusted_test_evidence,
)
from sdd.tdd_runner import run_pytest


tdd_runner_module = importlib.import_module("sdd.tdd_runner")


ROOT = Path(__file__).resolve().parent.parent
GOOGLE_API_KEY_PATTERN = re.compile("AI" + "za" + r"[0-9A-Za-z_-]{20,}")
HIGH_CONFIDENCE_SECRET_PATTERNS = (
    GOOGLE_API_KEY_PATTERN,
    re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),
    re.compile(r"glpat-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
)
SHELL_INSTALLERS = (
    ROOT / "installer/linux/install.sh",
    ROOT / "installer/macos/install.sh",
    ROOT / "installer/windows/provision.sh",
)
WINDOWS_WRAPPER = ROOT / "installer/windows/Install-OpenCodeEcosystem.ps1"
WINDOWS_GUIDE = ROOT / "installer/windows/README.md"


def _tracked_text_blobs(root: Path = ROOT) -> list[tuple[str, bytes]]:
    index = subprocess.run(
        ["git", "ls-files", "-s", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    entries: list[tuple[str, bytes]] = []
    for item in index.stdout.split(b"\0"):
        if not item:
            continue
        metadata, path_bytes = item.split(b"\t", 1)
        _mode, object_id, stage = metadata.split()
        if stage == b"0":
            entries.append((path_bytes.decode("utf-8"), object_id))

    batch = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=root,
        check=True,
        input=b"\n".join(object_id for _path, object_id in entries) + b"\n",
        capture_output=True,
    ).stdout
    offset = 0
    blobs = []
    for path, _object_id in entries:
        header_end = batch.index(b"\n", offset)
        header = batch[offset:header_end].split()
        assert len(header) == 3 and header[1] == b"blob", f"Blob Git inválido para {path}"
        size = int(header[2])
        content_start = header_end + 1
        blob = batch[content_start:content_start + size]
        offset = content_start + size
        assert batch[offset:offset + 1] == b"\n", f"Separador ausente no blob Git de {path}"
        offset += 1
        if b"\0" not in blob:
            blobs.append((path, blob))
    return blobs


def test_tracked_index_contains_no_high_confidence_secret_pattern() -> None:
    offenders = [
        path
        for path, blob in _tracked_text_blobs()
        if any(
            pattern.search(blob.decode("utf-8", errors="ignore"))
            for pattern in HIGH_CONFIDENCE_SECRET_PATTERNS
        )
    ]

    assert offenders == [], f"Possível chave Google/Gemini rastreada em: {offenders}"


def test_secret_scan_reads_the_index_instead_of_a_divergent_worktree(tmp_path: Path) -> None:
    repository = tmp_path / "index-repository"
    repository.mkdir()
    tracked = repository / "fixture.txt"
    staged_secret = "AI" + "za" + "x" * 24
    subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
    tracked.write_text(staged_secret, encoding="utf-8")
    subprocess.run(["git", "add", "fixture.txt"], cwd=repository, check=True)
    tracked.write_text("working tree sem segredo\n", encoding="utf-8")

    blobs = dict(_tracked_text_blobs(repository))

    assert blobs["fixture.txt"] == staged_secret.encode("utf-8")
    assert tracked.read_text(encoding="utf-8") != staged_secret


def test_runtime_evidence_never_promotes_an_absent_delivery() -> None:
    registry = SpecRegistry()
    original_specs = dict(registry.specs)
    spec_id = "SPEC-TEST-R453-DELIVERY"
    spec = Specification(spec_id, "spec temporária", "teste", test_file="tests")
    spec.criteria.append(
        AcceptanceCriterion("runtime_gate", "prova runtime", requires_trusted_test_evidence=True)
    )
    registry.specs = {spec_id: spec}
    evidence = _issue_trusted_test_evidence(
        spec_id,
        "tests",
        executed=True,
        passed=True,
        returncode=0,
        summary="suíte verde",
    )
    try:
        verifier = SpecVerifier(registry)
        absent = verifier.verify(spec_id, None, trusted_test_evidence=evidence)
        present = verifier.verify(spec_id, {"delivery": "presente"}, trusted_test_evidence=evidence)
    finally:
        registry.specs = original_specs

    assert absent["verified"] is False
    assert absent["status"] == "red"
    assert present["verified"] is True


def test_pytest_runner_rejects_option_like_target_and_uses_option_terminator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invoked: list[list[str]] = []

    def fake_run(command: list[str], **_kwargs: object) -> SimpleNamespace:
        invoked.append(command)
        return SimpleNamespace(returncode=0, stdout="1 passed\n", stderr="")

    monkeypatch.setattr(tdd_runner_module.subprocess, "run", fake_run)

    rejected = run_pytest("--collect-only")
    accepted = run_pytest("tests/test_r453_precommit_security_closure.py")

    assert rejected["all_passed"] is False
    assert rejected["error"] == "invalid_test_target"
    assert invoked == [
        [
            tdd_runner_module.sys.executable,
            "-m",
            "pytest",
            "-q",
            "--tb=no",
            "--",
            "tests/test_r453_precommit_security_closure.py",
        ]
    ]
    assert accepted["all_passed"] is True


def test_shell_installers_preflight_before_privilege_or_cli_installation() -> None:
    for installer in SHELL_INSTALLERS:
        content = installer.read_text(encoding="utf-8")
        preflight_call = content.rindex("preflight_immutable_checkout")

        for side_effect in ("sudo -v", "brew install", "apt-get update", "install_all_clis"):
            if side_effect in content:
                assert preflight_call < content.index(side_effect), (
                    f"{installer.name} executa {side_effect} antes do preflight"
                )


def test_shell_preflight_requires_clean_checkouts_and_rejects_repository_userinfo() -> None:
    for installer in SHELL_INSTALLERS:
        content = installer.read_text(encoding="utf-8")

        assert "checkout_worktree_is_clean" in content
        assert content.count("checkout_worktree_is_clean") >= 3
        assert "authority" in content
        assert '"$authority" != *"@"*' in content
        assert "?" in content and "#" in content


def test_external_artifact_preflight_occurs_before_privilege_and_windows_install() -> None:
    for installer in SHELL_INSTALLERS:
        content = installer.read_text(encoding="utf-8")
        artifact_preflight = content.rindex("preflight_external_artifacts")
        for side_effect in ("sudo -v", "brew install", "apt-get update"):
            if side_effect in content:
                assert artifact_preflight < content.index(side_effect)

    wrapper = WINDOWS_WRAPPER.read_text(encoding="utf-8")
    assert "Assert-ExternalArtifactProvenance" in wrapper
    assert wrapper.rindex("Assert-ExternalArtifactProvenance") < wrapper.index("--install -d $Distro")


def test_privileged_launchers_use_absolute_system_binaries_and_direct_bash() -> None:
    for installer in SHELL_INSTALLERS:
        content = installer.read_text(encoding="utf-8")
        assert content.startswith("#!/bin/bash")

    wrapper = WINDOWS_WRAPPER.read_text(encoding="utf-8")
    assert "$WslExe = Join-Path $env:SystemRoot 'System32\\wsl.exe'" in wrapper
    assert "$DismExe = Join-Path $env:SystemRoot 'System32\\dism.exe'" in wrapper
    assert "& $WslExe" in wrapper
    assert "& $DismExe" in wrapper
    assert "/bin/bash" in wrapper
    assert "-FilePath 'wsl.exe'" not in wrapper
    assert not re.search(r"(?m)^\s*wsl\.exe\s", wrapper)
    assert not re.search(r"(?m)^\s*dism\.exe\s", wrapper)


def test_cli_installation_drops_sudo_ticket_and_does_not_execute_found_cli_versions() -> None:
    common = (ROOT / "installer/common/install_clis.sh").read_text(encoding="utf-8")

    assert "$(opencode --version" not in common
    assert "$(claude --version" not in common
    assert "$(node --version" not in "\n".join(
        installer.read_text(encoding="utf-8") for installer in SHELL_INSTALLERS
    )
    for installer in (ROOT / "installer/linux/install.sh", ROOT / "installer/windows/provision.sh"):
        content = installer.read_text(encoding="utf-8")
        cli_install = content.index("install_all_clis")
        ticket_drop = content.rfind("sudo -k", 0, cli_install)
        assert ticket_drop >= 0, f"{installer.name} mantém ticket sudo antes das CLIs"


def test_installer_path_is_fixed_before_preflight_and_ollama_never_executes_an_unattested_binary() -> None:
    for installer in SHELL_INSTALLERS:
        content = installer.read_text(encoding="utf-8")
        safe_path = content.index("INSTALLER_SAFE_PATH=")
        preflight_call = content.rindex("preflight_immutable_checkout")
        assert safe_path < preflight_call
        assert 'PATH="$INSTALLER_SAFE_PATH"' in content

    common = (ROOT / "installer/common/install_clis.sh").read_text(encoding="utf-8")
    ollama_start = common.index("install_ollama_cli()")
    ollama_end = common.index("install_all_clis()")
    ollama = common[ollama_start:ollama_end]
    assert 'require_verified_https_artifact "Ollama"' in ollama
    assert '"$ollama_bin" serve' in ollama
    assert "command -v ollama" not in ollama
    assert "systemctl" not in ollama
    assert "sudo" not in ollama


def test_windows_wrapper_forwards_all_external_artifact_inputs_to_wsl() -> None:
    wrapper = WINDOWS_WRAPPER.read_text(encoding="utf-8")
    guide = WINDOWS_GUIDE.read_text(encoding="utf-8")
    required_names = (
        "OPENCODE_INSTALLER_URL",
        "OPENCODE_INSTALLER_SHA256",
        "OPENCODE_ARTIFACT_VERSION",
        "OPENCODE_NPM_VERSION",
        "OPENCODE_NPM_SHA256",
        "ANTIGRAVITY_INSTALLER_URL",
        "ANTIGRAVITY_INSTALLER_SHA256",
        "ANTIGRAVITY_ARTIFACT_VERSION",
        "CLAUDE_CODE_VERSION",
        "CLAUDE_CODE_NPM_SHA256",
        "OLLAMA_BINARY_URL",
        "OLLAMA_BINARY_SHA256",
        "OLLAMA_ARTIFACT_VERSION",
    )

    assert "$wslEnvironment" in wrapper
    for name in required_names:
        assert name in wrapper
        assert name in guide


def test_external_artifact_preflight_is_pure_and_rejects_query_strings(tmp_path: Path) -> None:
    common = ROOT / "installer/common/install_clis.sh"
    home = tmp_path / "home"
    home.mkdir()
    script = f"""
source {shlex.quote(str(common))}
export OPENCODE_INSTALLER_URL=''
export OPENCODE_INSTALLER_SHA256=''
export OPENCODE_ARTIFACT_VERSION=''
export OPENCODE_NPM_VERSION='v1.2.3'
export OPENCODE_NPM_SHA256='{'0' * 64}'
export ANTIGRAVITY_INSTALLER_URL='https://downloads.example.invalid/releases/v2.3.4/agy.sh'
export ANTIGRAVITY_INSTALLER_SHA256='{'1' * 64}'
export ANTIGRAVITY_ARTIFACT_VERSION='v2.3.4'
export CLAUDE_CODE_VERSION='v3.4.5'
export CLAUDE_CODE_NPM_SHA256='{'2' * 64}'
export OLLAMA_BINARY_URL='https://downloads.example.invalid/releases/v4.5.6/ollama'
export OLLAMA_BINARY_SHA256='{'3' * 64}'
export OLLAMA_ARTIFACT_VERSION='v4.5.6'
preflight_external_artifacts
export OLLAMA_BINARY_URL='https://downloads.example.invalid/releases/v4.5.6/ollama?unexpected=query'
if preflight_external_artifacts; then
    exit 1
fi
"""

    result = subprocess.run(
        ["/bin/bash", "-c", script],
        cwd=ROOT,
        env={"HOME": str(home), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert not (home / ".cache").exists()


def test_cli_steps_keep_a_system_path_and_abort_on_first_integrity_error(tmp_path: Path) -> None:
    common = ROOT / "installer/common/install_clis.sh"
    home = tmp_path / "home"
    marker = tmp_path / "later-cli-ran"
    home.mkdir()
    script = "\n".join(
        (
            f"source {shlex.quote(str(common))}",
            "preflight_external_artifacts() { :; }",
            "export INSTALLER_SAFE_PATH='/user-controlled/path'",
            "expected_path=\"$(installer_system_path)\"",
            f"export MARKER={shlex.quote(str(marker))}",
            "install_opencode_cli() { [ \"$PATH\" = \"$expected_path\" ] || return 11; export PATH=\"$HOME/.local/bin:$PATH\"; }",
            "install_antigravity_cli() { [ \"$PATH\" = \"$expected_path\" ] || return 12; export PATH=\"$HOME/.opencode/bin:$PATH\"; }",
            "install_claude_code_cli() { [ \"$PATH\" = \"$expected_path\" ] || return 13; return 23; }",
            "install_ollama_cli() { : > \"$MARKER\"; }",
            "if install_all_clis; then exit 1; fi",
            "[ ! -e \"$MARKER\" ]",
        )
    )

    result = subprocess.run(
        ["/bin/bash", "-c", script],
        cwd=ROOT,
        env={"HOME": str(home), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert not marker.exists()


def test_installer_sources_are_bound_to_verified_trees_before_libraries() -> None:
    for installer in (ROOT / "installer/linux/install.sh", ROOT / "installer/macos/install.sh"):
        content = installer.read_text(encoding="utf-8")
        assert "SCRIPT_ROOT=" in content
        assert "ECOSYSTEM_SOURCE_DIR não pode divergir" in content
        assert content.index("if ! preflight_immutable_checkout") < content.index('source "$PATH_SAFETY_LIB"')

    provision = (ROOT / "installer/windows/provision.sh").read_text(encoding="utf-8")
    assert "verify_staged_installer_attestation" in provision
    assert provision.index("verify_staged_installer_attestation") < provision.index('source "$PATH_SAFETY_LIB"')

    wrapper = WINDOWS_WRAPPER.read_text(encoding="utf-8")
    assert "ECOSYSTEM_PROVISION_SHA256" in wrapper
    assert "ECOSYSTEM_COMMON_INSTALLER_SHA256" in wrapper
    assert "ECOSYSTEM_PATH_SAFETY_SHA256" in wrapper


def test_windows_validates_bytes_and_sanitizes_bash_before_wsl_installation() -> None:
    wrapper = WINDOWS_WRAPPER.read_text(encoding="utf-8")
    wsl_install = wrapper.index("& $WslExe --install -d $Distro")

    assert wrapper.index("Test-VerifiedFile -Path $tempProvision") < wsl_install
    assert wrapper.index("Test-VerifiedFile -Path $tempCommon") < wsl_install
    assert wrapper.index("Test-VerifiedFile -Path $tempPathSafety") < wsl_install
    assert "/usr/bin/env -i $wslRuntimeEnvironment /bin/bash --noprofile --norc -c" in wrapper
    assert "BASH_ENV=" in wrapper
    assert 'bash -lc "exec $quotedWslProvision"' not in wrapper


def test_sdd_documentation_does_not_misrepresent_same_process_evidence() -> None:
    source = (ROOT / "sdd/spec_engine.py").read_text(encoding="utf-8")

    assert "não é uma fronteira de segurança contra código arbitrário no mesmo processo" in source


def test_sdd_runtime_timeout_exceeds_the_observed_full_suite_duration() -> None:
    assert run_pytest.__defaults__ is not None
    assert run_pytest.__defaults__[1] >= 1200
    quality_report = (ROOT / "scripts/quality_report.py").read_text(encoding="utf-8")
    assert "PYTEST_TIMEOUT_SECONDS = 1200" in quality_report


def test_installer_docs_keep_explicit_non_guarantees() -> None:
    installer_guide = (ROOT / "installer/README.md").read_text(encoding="utf-8").lower()
    windows_guide = WINDOWS_GUIDE.read_text(encoding="utf-8").lower()
    validation = (ROOT / "VALIDATION_R453.md").read_text(encoding="utf-8").lower()

    for content in (installer_guide, windows_guide):
        assert "toctou" in content
        assert "integridade transitiva" in content
    assert "e2e windows" in validation
    assert "toctou" in validation
    assert "integridade transitiva" in validation
