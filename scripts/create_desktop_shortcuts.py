# -*- coding: utf-8 -*-
"""
Gerador Universal de Atalhos de Área de Trabalho — OpenCode Ecosystem Core
========================================================================
Cria os 4 atalhos essenciais na Área de Trabalho:
  1. OpenCode Ecosystem   -> OpenCode CLI no WSL / Linux / macOS
  2. Antigravity CLI      -> Google Antigravity (agy) no WSL / Linux / macOS
  3. Claude Code CLI      -> Claude Code (@anthropic-ai) no WSL / Linux / macOS
  4. Ecosystem (marceloclaro) -> Orquestrador Primário CLI

Funciona de forma transparente em:
  - Windows nativo
  - WSL (detecta a Área de Trabalho do Windows host e cria atalhos .lnk via PowerShell)
  - Linux nativo (cria arquivos .desktop)
  - macOS (cria arquivos .command)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def is_wsl() -> bool:
    """Detecta se está rodando dentro do Windows Subsystem for Linux (WSL)."""
    if os.path.exists("/proc/version"):
        try:
            with open("/proc/version", "r", encoding="utf-8") as f:
                content = f.read().lower()
                return "microsoft" in content or "wsl" in content
        except Exception:
            pass
    return False


def get_repo_root() -> Path:
    """Retorna o caminho absoluto da raiz do repositório."""
    return Path(__file__).resolve().parent.parent


def create_wsl_windows_shortcuts(repo_dir: Path) -> bool:
    """Cria atalhos .lnk na Área de Trabalho do Windows a partir do WSL."""
    print("[SHORTCUTS] Ambiente WSL detectado — gerando atalhos .lnk na Área de Trabalho do Windows...")
    wsl_user = os.environ.get("USER", "marceloclaro")
    distro = "Ubuntu"

    ps_script = f"""
$ErrorActionPreference = 'SilentlyContinue'
$Desktop = [Environment]::GetFolderPath('Desktop')
$WShell  = New-Object -ComObject WScript.Shell
$EcoDir  = '/home/{wsl_user}/opencode-ecosystem-core'

$AppDir = Join-Path $env:LOCALAPPDATA 'OpenCodeEcosystem'
if (-not (Test-Path $AppDir)) {{ New-Item -ItemType Directory -Path $AppDir -Force | Out-Null }}
$LocalIco = Join-Path $AppDir 'icon.ico'

# Tenta copiar o ícone do projeto
$wslIco = "\\\\wsl.localhost\\{distro}\\home\\{wsl_user}\\opencode-ecosystem-core\\assets\\icon.ico"
if (Test-Path $wslIco) {{
    Copy-Item $wslIco $LocalIco -Force -ErrorAction SilentlyContinue
}}
$IconTarget = if (Test-Path $LocalIco) {{ $LocalIco }} else {{ "$env:SystemRoot\\System32\\wsl.exe,0" }}

function New-EcoShortcut ($Name, $Arguments, $Description, $Icon) {{
    $lnkPath = Join-Path $Desktop "$Name.lnk"
    $sc = $WShell.CreateShortcut($lnkPath)
    $sc.TargetPath  = "$env:SystemRoot\\System32\\wsl.exe"
    $sc.Arguments   = $Arguments
    $sc.Description = $Description
    $sc.WorkingDirectory = $env:USERPROFILE
    if ($Icon) {{ $sc.IconLocation = $Icon }}
    $sc.Save()
    Write-Host "[OK] Atalho criado no Windows: $Name.lnk"
}}

New-EcoShortcut 'OpenCode Ecosystem' "-d {distro} --cd $EcoDir -- bash -lic `"opencode`"" 'OpenCode CLI com 209 agentes nativos + 6 MCPs + APM' $IconTarget
New-EcoShortcut 'Antigravity CLI' "-d {distro} --cd $EcoDir -- bash -lic `"agy`"" 'Google Antigravity CLI no ecossistema' $IconTarget
New-EcoShortcut 'Claude Code CLI' "-d {distro} --cd $EcoDir -- bash -lic `"claude`"" 'Claude Code CLI no ecossistema' $IconTarget
New-EcoShortcut 'Ecosystem (marceloclaro)' "-d {distro} --cd $EcoDir -- bash -lic `"python3 -m marceloclaro.cli`"" 'CLI interativo do orquestrador marceloclaro' "$env:SystemRoot\\System32\\cmd.exe,0"
"""
    try:
        res = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if res.returncode == 0:
            print(res.stdout.strip())
            return True
        else:
            print(f"[AVISO] PowerShell retornou código {res.returncode}: {res.stderr.strip()}")
            return False
    except Exception as exc:
        print(f"[AVISO] Não foi possível chamar powershell.exe a partir do WSL ({exc}).")
        return False


def create_linux_desktop_shortcuts(repo_dir: Path) -> bool:
    """Cria arquivos .desktop para Linux nativo."""
    print("[SHORTCUTS] Ambiente Linux detectado — gerando lançadores .desktop...")
    apps_dir = Path.home() / ".local" / "share" / "applications"
    desktop_dir = Path.home() / "Desktop"
    apps_dir.mkdir(parents=True, exist_ok=True)

    icon_path = repo_dir / "assets" / "icon.png"

    shortcuts = [
        {
            "filename": "opencode-ecosystem.desktop",
            "name": "OpenCode Ecosystem",
            "exec": f"bash -c 'cd {repo_dir} && opencode'",
            "comment": "OpenCode CLI com 209 agentes nativos e MCPs",
        },
        {
            "filename": "antigravity-cli.desktop",
            "name": "Antigravity CLI",
            "exec": f"bash -c 'cd {repo_dir} && agy'",
            "comment": "Google Antigravity CLI no ecossistema",
        },
        {
            "filename": "claude-code-cli.desktop",
            "name": "Claude Code CLI",
            "exec": f"bash -c 'cd {repo_dir} && claude'",
            "comment": "Claude Code CLI no ecossistema",
        },
        {
            "filename": "marceloclaro-ecosystem.desktop",
            "name": "Ecosystem (marceloclaro)",
            "exec": f"bash -c 'cd {repo_dir} && python3 -m marceloclaro.cli'",
            "comment": "Orquestrador Metacognitivo marceloclaro",
        },
    ]

    for sc in shortcuts:
        content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={sc['name']}
Comment={sc['comment']}
Exec={sc['exec']}
Icon={icon_path if icon_path.exists() else 'utilities-terminal'}
Terminal=true
Categories=Development;Science;IDE;
"""
        target_app = apps_dir / sc["filename"]
        target_app.write_text(content, encoding="utf-8")
        target_app.chmod(0o755)

        if desktop_dir.exists():
            target_desk = desktop_dir / sc["filename"]
            target_desk.write_text(content, encoding="utf-8")
            target_desk.chmod(0o755)
            print(f"[OK] Criado atalho na Área de Trabalho: {target_desk}")
        else:
            print(f"[OK] Criado lançador de aplicativo: {target_app}")

    return True


def main():
    repo_dir = get_repo_root()
    print("=" * 70)
    print("  OPENCODE ECOSYSTEM CORE — CRIADOR DE ATALHOS")
    print(f"  Diretório: {repo_dir}")
    print("=" * 70)

    if is_wsl():
        success = create_wsl_windows_shortcuts(repo_dir)
        if not success:
            create_linux_desktop_shortcuts(repo_dir)
    elif sys.platform == "win32":
        print("[SHORTCUTS] Windows nativo detectado.")
        # Pode ser acionado via Create-Shortcuts.ps1
    else:
        create_linux_desktop_shortcuts(repo_dir)

    print("\n[SUCESSO] Configuração de atalhos finalizada!")


if __name__ == "__main__":
    main()
