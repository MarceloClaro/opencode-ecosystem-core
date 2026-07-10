# ============================================================================
# OpenCode Ecosystem Core - Desinstalador para Windows
# ----------------------------------------------------------------------------
# Por padrao, remove APENAS o que o instalador criou e que e seguro reverter:
#   - Os 4 atalhos na Area de Trabalho (OpenCode Ecosystem, Antigravity CLI,
#     Claude Code (Ecosystem), Ecosystem (marceloclaro))
#   - As regras de Firewall criadas pelo instalador
#   - As exclusoes do Windows Defender criadas pelo instalador
#
# NAO remove, por padrao: o WSL, a distro Ubuntu, os arquivos do repositorio
# dentro dela, nem as CLIs (OpenCode/Antigravity/Claude Code/Ollama) — essas
# acoes sao destrutivas e exigem flags explicitas + confirmacao.
#
# Uso:
#   .\Uninstall-OpenCodeEcosystem.ps1                    # remove so os atalhos/regras (seguro)
#   .\Uninstall-OpenCodeEcosystem.ps1 -RemoveWSLDistro    # tambem apaga a distro Ubuntu inteira (destrutivo)
#   .\Uninstall-OpenCodeEcosystem.ps1 -RemoveWSLFeature   # tambem desativa o WSL do Windows inteiro (afeta TODAS as distros)
#   .\Uninstall-OpenCodeEcosystem.ps1 -RemoveWSLDistro -Force   # pula a confirmacao interativa (uso em script)
# ============================================================================

#Requires -Version 5.1

param(
    [switch]$RemoveWSLDistro,
    [switch]$RemoveWSLFeature,
    [switch]$Force
)

$ErrorActionPreference = 'Continue'
$Distro = 'Ubuntu'

function Write-Step($msg)  { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Ok($msg)    { Write-Host "[OK] $msg"      -ForegroundColor Green }
function Write-Warn2($msg) { Write-Host "[AVISO] $msg"   -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "[ERRO] $msg"    -ForegroundColor Red }

function Confirm-Destructive([string]$question) {
    if ($Force) { return $true }
    Write-Host ""
    Write-Warn2 $question
    $answer = Read-Host "Digite CONFIRMO para prosseguir (qualquer outra coisa cancela)"
    return ($answer -eq 'CONFIRMO')
}

Write-Host @"
===================================================================
  OpenCode Ecosystem Core - Desinstalador Windows
===================================================================
"@ -ForegroundColor Magenta

# ----------------------------------------------------------------------------
# 1. Remover atalhos da Area de Trabalho
# ----------------------------------------------------------------------------
Write-Step "Etapa 1/3: Removendo atalhos da Area de Trabalho"
$Desktop = [Environment]::GetFolderPath('Desktop')
$shortcuts = @(
    'OpenCode Ecosystem.lnk',
    'Antigravity CLI.lnk',
    'Claude Code (Ecosystem).lnk',
    'Ecosystem (marceloclaro).lnk'
)
foreach ($name in $shortcuts) {
    $path = Join-Path $Desktop $name
    if (Test-Path $path) {
        Remove-Item $path -Force -ErrorAction SilentlyContinue
        Write-Ok "Removido: $name"
    } else {
        Write-Host "Nao encontrado (ja removido?): $name"
    }
}

# ----------------------------------------------------------------------------
# 2. Remover regras de Firewall e exclusoes do Defender
# ----------------------------------------------------------------------------
Write-Step "Etapa 2/3: Removendo regras de Firewall e exclusoes do Defender"
try {
    Remove-NetFirewallRule -DisplayName "OpenCode Ecosystem (WSL In)" -ErrorAction SilentlyContinue
    Remove-NetFirewallRule -DisplayName "OpenCode Ecosystem (WSL Out)" -ErrorAction SilentlyContinue
    Remove-NetFirewallRule -DisplayName "OpenCode Ecosystem (Ports)" -ErrorAction SilentlyContinue
    Write-Ok "Regras de Firewall removidas."
} catch {
    Write-Warn2 "Nao foi possivel remover as regras de Firewall (talvez ja removidas, ou requer administrador)."
}

try {
    Remove-MpPreference -ExclusionProcess "wsl.exe" -ErrorAction SilentlyContinue
    Remove-MpPreference -ExclusionProcess "wslhost.exe" -ErrorAction SilentlyContinue
    Remove-MpPreference -ExclusionPath "\\wsl.localhost\Ubuntu" -ErrorAction SilentlyContinue
    Remove-MpPreference -ExclusionPath "\\wsl`$\Ubuntu" -ErrorAction SilentlyContinue
    Write-Ok "Exclusoes do Defender removidas."
} catch {
    Write-Warn2 "Nao foi possivel remover as exclusoes do Defender."
}

# ----------------------------------------------------------------------------
# 3. Acoes destrutivas (opt-in, com confirmacao)
# ----------------------------------------------------------------------------
Write-Step "Etapa 3/3: Acoes destrutivas (opcionais)"

if ($RemoveWSLDistro) {
    $ok = Confirm-Destructive "Isso vai APAGAR PERMANENTEMENTE a distro '$Distro' inteira do WSL, incluindo TODOS os arquivos dentro dela (nao so o ecossistema). Esta acao NAO pode ser desfeita."
    if ($ok) {
        wsl.exe --unregister $Distro
        if ($LASTEXITCODE -eq 0) {
            Write-Ok "Distro '$Distro' removida do WSL."
        } else {
            Write-Err "Falha ao remover a distro '$Distro' (ja removida, ou nome incorreto?)."
        }
    } else {
        Write-Warn2 "Remocao da distro cancelada pelo usuario."
    }
} else {
    Write-Host "Distro '$Distro' NAO removida (use -RemoveWSLDistro para remover)."
}

if ($RemoveWSLFeature) {
    $ok = Confirm-Destructive "Isso vai DESATIVAR o WSL (Windows Subsystem for Linux) no Windows inteiro, afetando TODAS as distros instaladas, nao so o ecossistema. Pode exigir reiniciar o computador."
    if ($ok) {
        dism.exe /online /disable-feature /featurename:Microsoft-Windows-Subsystem-Linux /norestart | Out-Null
        dism.exe /online /disable-feature /featurename:VirtualMachinePlatform /norestart | Out-Null
        Write-Ok "Recursos do WSL desativados (reinicie o computador para concluir)."
    } else {
        Write-Warn2 "Desativacao do WSL cancelada pelo usuario."
    }
} else {
    Write-Host "WSL (recurso do Windows) NAO desativado (use -RemoveWSLFeature para desativar; afeta TODAS as distros)."
}

Write-Host @"

===================================================================
  DESINSTALACAO CONCLUIDA
===================================================================
  Removido: atalhos da Area de Trabalho, regras de Firewall, exclusoes do Defender.
  Nao removido (a menos que solicitado via flags): distro WSL, CLIs instaladas dentro dela.
  Para remover as CLIs (opencode/agy/claude/ollama) e o repositorio clonado,
  rode dentro do Ubuntu:  bash installer/linux/uninstall.sh --remove-clis
===================================================================
"@ -ForegroundColor Green
