"""Contratos de segurança fail-closed para os instaladores R448."""

import re
import shlex
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALLER_FILES = (
    "installer/common/install_clis.sh",
    "installer/linux/install.sh",
    "installer/macos/install.sh",
    "installer/windows/provision.sh",
    "installer/windows/Install-OpenCodeEcosystem.ps1",
)

SHELL_INSTALLERS = (
    "installer/linux/install.sh",
    "installer/macos/install.sh",
    "installer/windows/provision.sh",
)


def _content(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_installers_never_persist_unrestricted_sudo_or_disable_host_protections():
    """O instalador não deve criar sudoers irrestrito nem abrir o host à força."""
    combined = "\n".join(_content(path) for path in INSTALLER_FILES)

    assert "NOPASSWD:ALL" not in combined
    assert "Add-MpPreference" not in combined
    assert "New-NetFirewallRule" not in combined
    assert "SEE_MASK_NOZONECHECKS" not in combined


def test_installers_do_not_pipe_network_content_to_an_interpreter():
    """Toda execução remota precisa passar por download e verificação local."""
    combined = "\n".join(_content(path) for path in INSTALLER_FILES)

    assert not re.search(r"(?:curl|irm|Invoke-WebRequest)[^\n|]*\|\s*(?:bash|sh|iex)", combined, re.IGNORECASE)
    assert "/main/" not in combined
    assert "/latest/" not in combined


def test_automatic_installs_require_version_and_sha256_verification():
    """Bootstrap automático só ocorre a partir de artefato HTTPS versionado e hashado."""
    shared = _content("installer/common/install_clis.sh")
    powershell = _content("installer/windows/Install-OpenCodeEcosystem.ps1")

    assert "require_verified_https_artifact" in shared
    assert "sha256sum" in shared
    assert "ARTIFACT_VERSION" in shared
    assert "Get-VerifiedArtifact" in powershell
    assert "Get-FileHash" in powershell
    assert "ProvisionSha256" in powershell
    assert "CommonInstallerSha256" in powershell
    assert "installer/common/install_clis.sh" in powershell


def test_shell_installers_fail_before_aliases_or_launchers_when_smoke_tests_fail():
    """Smoke test inválido não pode persistir integração nem anunciar êxito."""
    launch_markers = {
        "installer/linux/install.sh": 'DESKTOP_FILE_DIR="$HOME/.local/share/applications"',
        "installer/macos/install.sh": 'LAUNCHER="$DESKTOP_DIR/Ecosystem (marceloclaro).command"',
        "installer/windows/provision.sh": '"$VENV_PYTHON" -m marceloclaro.cli shortcuts',
    }

    for path in SHELL_INSTALLERS:
        content = _content(path)
        failure_guard = 'if [ "$FAIL" -ne 0 ]; then'

        assert failure_guard in content
        assert 'err "Smoke tests falharam; integração e atalhos não serão criados."' in content
        assert "exit 1" in content[content.index(failure_guard):]
        assert content.index(failure_guard) < content.index('add_line "alias ecosystem=')
        assert content.index(failure_guard) < content.index(launch_markers[path])
        assert "concluída com pendências" not in content


def test_ecosystem_runtime_commands_and_shortcuts_use_the_created_virtualenv():
    """Não se deve alternar para o Python global após a criação da virtualenv."""
    for path in SHELL_INSTALLERS:
        content = _content(path)

        assert 'VENV_PYTHON="$ECO_DIR/.venv/bin/python"' in content
        assert '"$VENV_PYTHON" -c "from marceloclaro.orchestrator import MarceloClaroOrchestrator"' in content
        assert '"$VENV_PYTHON" -m marceloclaro.cli' in content
        assert "python3 -m marceloclaro.cli" not in content

    windows = _content("installer/windows/Install-OpenCodeEcosystem.ps1")
    shortcut_script = _content("installer/windows/Create-Shortcuts.ps1")
    assert ".venv/bin/python -m marceloclaro.cli" in windows
    assert ".venv/bin/python -m marceloclaro.cli" in shortcut_script


def test_windows_requires_manual_reentry_instead_of_oversized_runonce_command():
    """Reboot não deve depender de um comando RunOnce que pode ser truncado."""
    powershell = _content("installer/windows/Install-OpenCodeEcosystem.ps1")

    assert "RunOnce" not in powershell
    assert "Set-ItemProperty" not in powershell
    assert "function Assert-InstallationInputs" in powershell
    assert "retomada manual" in powershell.lower()
    assert powershell.index("Assert-InstallationInputs") < powershell.index(
        "& $WslExe --install -d $Distro"
    )
    assert "ExecutionPolicy Bypass" not in powershell


def test_windows_wrapper_exits_before_shortcuts_when_wsl_provisioning_fails():
    """O wrapper não trata erro do provisionador como aviso recuperável."""
    powershell = _content("installer/windows/Install-OpenCodeEcosystem.ps1")
    error = 'Write-Err "Provisionamento falhou; atalhos não serão criados.'
    shortcuts = 'Write-Step "Etapa 4/5: Criando atalhos na Area de Trabalho"'

    assert error in powershell
    assert shortcuts in powershell
    error_position = powershell.index(error)
    assert "exit 1" in powershell[error_position:powershell.index(shortcuts)]
    assert error_position < powershell.index(shortcuts)
    assert powershell.index('Write-Ok "Provisionamento concluido."') < powershell.index(shortcuts)


def test_wsl_executes_normalized_bytes_that_are_verified_again_after_copy():
    """A conversão CRLF ocorre antes do hash e o destino WSL é revalidado."""
    powershell = _content("installer/windows/Install-OpenCodeEcosystem.ps1")

    assert "function Convert-CrlfToLf" in powershell
    assert "function Test-WslArtifactHashes" in powershell
    assert "sha256sum" in powershell
    assert "PathSafetySha256" in powershell
    assert "Test-VerifiedFile -Path $tempPathSafety -ExpectedSha256 $PathSafetySha256" in powershell
    assert "-PathSafetyHash $PathSafetySha256" in powershell
    assert "tr -d '\\r'" not in powershell
    assert powershell.index("Convert-CrlfToLf -Path $tempProvision") < powershell.index(
        "Test-VerifiedFile -Path $tempProvision"
    )
    assert powershell.index("Test-WslArtifactHashes -WslRoot") < powershell.index(
        '/bin/bash --noprofile --norc -c "exec $quotedWslProvision"'
    )
    assert "*.sh text eol=lf" in _content(".gitattributes")


def test_verified_downloads_bind_version_cache_and_https_redirect_policy():
    """Caches são revalidados e downloads não podem seguir downgrade de HTTPS."""
    shared = _content("installer/common/install_clis.sh")
    powershell = _content("installer/windows/Install-OpenCodeEcosystem.ps1")

    assert "is_immutable_version" in shared
    assert "artifact_cache_path" in shared
    assert "--proto-redir '=https'" in shared
    assert "--max-redirs 3" in shared
    assert "verify_cached_artifact" in shared
    assert "npm pack" in shared and "--ignore-scripts" in shared
    assert "npm install --global --prefix \"$HOME/.local\" --ignore-scripts --offline \"$tarball\"" in shared

    assert "Test-ImmutableVersion" in powershell
    assert "Get-ArtifactCacheRoot" in powershell
    assert "Test-SecureHttpsUri" in powershell
    assert "-MaximumRedirection 0" in powershell


def test_common_artifact_validation_rejects_mutable_or_unbound_provenance():
    """As validações Bash falham antes de qualquer download de rede."""
    common = shlex.quote(str(REPO_ROOT / "installer/common/install_clis.sh"))
    validation = f"""
source {common}
is_immutable_version 'v1.2.3'
! is_immutable_version 'latest'
! is_immutable_version '../../escape'
is_https_artifact_url 'https://downloads.example.invalid/releases/v1.2.3/installer.sh' 'v1.2.3'
! is_https_artifact_url 'http://downloads.example.invalid/releases/v1.2.3/installer.sh' 'v1.2.3'
! is_https_artifact_url 'https://downloads.example.invalid/main/v1.2.3/installer.sh' 'v1.2.3'
! is_https_artifact_url 'https://downloads.example.invalid/releases/installer.sh' 'v1.2.3'
! is_https_artifact_url 'https://user@example.invalid/releases/v1.2.3/installer.sh' 'v1.2.3'
"""

    result = subprocess.run(["bash", "-c", validation], capture_output=True, text=True)

    assert result.returncode == 0, result.stderr
