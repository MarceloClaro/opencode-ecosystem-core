# ============================================================================
# OpenCode Ecosystem Core — Gerador de Atalhos para Área de Trabalho (Windows)
# ----------------------------------------------------------------------------
# Cria ou atualiza os 4 atalhos na Área de Trabalho do Windows:
#   1. OpenCode Ecosystem        -> wsl.exe -d Ubuntu --cd ... opencode
#   2. Antigravity CLI           -> wsl.exe -d Ubuntu --cd ... agy
#   3. Claude Code CLI           -> wsl.exe -d Ubuntu --cd ... claude
#   4. Ecosystem (marceloclaro)  -> wsl.exe -d Ubuntu --cd ... python3 -m marceloclaro.cli
# ============================================================================

#Requires -Version 5.1

$ErrorActionPreference = 'SilentlyContinue'
$Distro     = 'Ubuntu'
$Desktop    = [Environment]::GetFolderPath('Desktop')
$WShell     = New-Object -ComObject WScript.Shell

# Detecta usuário default do WSL Ubuntu
$wslUser = (wsl.exe -d $Distro -- whoami 2>$null)
if (-not $wslUser) { $wslUser = 'marceloclaro' } else { $wslUser = $wslUser.Trim() }

$EcoDir = "/home/$wslUser/opencode-ecosystem-core"

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "  Criando Atalhos do OpenCode Ecosystem Core no Windows" -ForegroundColor Cyan
Write-Host "  Distro WSL: $Distro | Usuario: $wslUser" -ForegroundColor Cyan
Write-Host "===================================================================" -ForegroundColor Cyan

# Prepara ícone personalizado
$AppDir = Join-Path $env:LOCALAPPDATA 'OpenCodeEcosystem'
if (-not (Test-Path $AppDir)) { New-Item -ItemType Directory -Path $AppDir -Force | Out-Null }
$LocalIco = Join-Path $AppDir 'icon.ico'

$wslIco = "\\wsl.localhost\$Distro\home\$wslUser\opencode-ecosystem-core\assets\icon.ico"
if (Test-Path $wslIco) {
    Copy-Item $wslIco $LocalIco -Force -ErrorAction SilentlyContinue
}
$IconTarget = if (Test-Path $LocalIco) { $LocalIco } else { "$env:SystemRoot\System32\wsl.exe,0" }

function New-EcoShortcut ($Name, $Arguments, $Description, $Icon) {
    $lnkPath = Join-Path $Desktop "$Name.lnk"
    $sc = $WShell.CreateShortcut($lnkPath)
    $sc.TargetPath  = "$env:SystemRoot\System32\wsl.exe"
    $sc.Arguments   = $Arguments
    $sc.Description = $Description
    $sc.WorkingDirectory = $env:USERPROFILE
    if ($Icon) { $sc.IconLocation = $Icon }
    $sc.Save()
    Write-Host "[OK] Atalho criado: $Name.lnk" -ForegroundColor Green
}

New-EcoShortcut 'OpenCode Ecosystem' "-d $Distro --cd $EcoDir -- bash -lic `"opencode`"" 'OpenCode CLI com 209 agentes nativos + 6 MCPs + APM' $IconTarget
New-EcoShortcut 'Antigravity CLI' "-d $Distro --cd $EcoDir -- bash -lic `"agy`"" 'Google Antigravity CLI no ecossistema' $IconTarget
New-EcoShortcut 'Claude Code CLI' "-d $Distro --cd $EcoDir -- bash -lic `"claude`"" 'Claude Code CLI no ecossistema' $IconTarget
New-EcoShortcut 'Ecosystem (marceloclaro)' "-d $Distro --cd $EcoDir -- bash -lic `"python3 -m marceloclaro.cli`"" 'CLI interativo do orquestrador marceloclaro' "$env:SystemRoot\System32\cmd.exe,0"

Write-Host "`n[SUCESSO] Os 4 atalhos foram criados na sua Area de Trabalho!" -ForegroundColor Green
