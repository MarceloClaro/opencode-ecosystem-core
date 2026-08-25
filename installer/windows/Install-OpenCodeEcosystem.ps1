# ============================================================================
# OpenCode Ecosystem Core - Instalador Automático para Windows
# ----------------------------------------------------------------------------
# O que este script faz:
#   1. Instala o WSL2 + Ubuntu (se ausente), com retomada manual pós-reboot
#   2. Provisiona o Ubuntu: OpenCode CLI, Antigravity CLI, Ollama CLI
#   3. Instala o opencode-ecosystem-core (nativo no OpenCode CLI)
#   4. Cria atalhos na Área de Trabalho (1 clique):
#        - "OpenCode Ecosystem"       -> abre o OpenCode CLI dentro do ecossistema
#        - "Antigravity CLI"          -> abre o agy dentro do ecossistema
#        - "Ecosystem (marceloclaro)" -> abre o CLI nativo do orquestrador
#
# Como executar (PowerShell COMO ADMINISTRADOR):
#   1. Baixe/clone uma revisão imutável do repositório por canal confiável.
#   2. Confira o SHA-256 de provision.sh publicado para essa revisão.
#   3. Rode este arquivo local com -ProvisionVersion e -ProvisionSha256.
# O instalador recusa bootstrap por pipe de rede e não reduz proteções do host.
# ============================================================================

#Requires -Version 5.1

param(
    [string]$ProvisionUri = $env:ECOSYSTEM_PROVISION_URL,
    [string]$ProvisionVersion = $env:ECOSYSTEM_PROVISION_VERSION,
    [string]$ProvisionSha256 = $env:ECOSYSTEM_PROVISION_SHA256,
    [string]$CommonInstallerSha256 = $env:ECOSYSTEM_COMMON_INSTALLER_SHA256,
    [string]$PathSafetySha256 = $env:ECOSYSTEM_PATH_SAFETY_SHA256,
    [string]$EcosystemRef = $env:ECOSYSTEM_REF,
    [object]$OPENCODE_INSTALLER_URL = $env:OPENCODE_INSTALLER_URL,
    [object]$OPENCODE_INSTALLER_SHA256 = $env:OPENCODE_INSTALLER_SHA256,
    [object]$OPENCODE_ARTIFACT_VERSION = $env:OPENCODE_ARTIFACT_VERSION,
    [object]$OPENCODE_NPM_VERSION = $env:OPENCODE_NPM_VERSION,
    [object]$OPENCODE_NPM_SHA256 = $env:OPENCODE_NPM_SHA256,
    [object]$ANTIGRAVITY_INSTALLER_URL = $env:ANTIGRAVITY_INSTALLER_URL,
    [object]$ANTIGRAVITY_INSTALLER_SHA256 = $env:ANTIGRAVITY_INSTALLER_SHA256,
    [object]$ANTIGRAVITY_ARTIFACT_VERSION = $env:ANTIGRAVITY_ARTIFACT_VERSION,
    [object]$CLAUDE_CODE_VERSION = $env:CLAUDE_CODE_VERSION,
    [object]$CLAUDE_CODE_NPM_SHA256 = $env:CLAUDE_CODE_NPM_SHA256,
    [object]$OLLAMA_BINARY_URL = $env:OLLAMA_BINARY_URL,
    [object]$OLLAMA_BINARY_SHA256 = $env:OLLAMA_BINARY_SHA256,
    [object]$OLLAMA_ARTIFACT_VERSION = $env:OLLAMA_ARTIFACT_VERSION
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($env:SystemRoot)) {
    throw 'SYSTEMROOT ausente; não é seguro localizar os binários do sistema.'
}
$WslExe = Join-Path $env:SystemRoot 'System32\wsl.exe'
$DismExe = Join-Path $env:SystemRoot 'System32\dism.exe'
if (-not (Test-Path -LiteralPath $WslExe -PathType Leaf) -or -not (Test-Path -LiteralPath $DismExe -PathType Leaf)) {
    throw 'Binários WSL/DISM do sistema não foram encontrados nos caminhos absolutos esperados.'
}
$Distro     = 'Ubuntu'
$ScriptSelf = $MyInvocation.MyCommand.Path
$ScriptDirectory = if ($ScriptSelf) { Split-Path -Parent $ScriptSelf } else { $null }
$provisionLocal = if ($ScriptDirectory) { Join-Path $ScriptDirectory 'provision.sh' } else { $null }
$commonLocal = if ($ScriptDirectory) {
    Join-Path (Split-Path $ScriptDirectory -Parent) 'common/install_clis.sh'
} else { $null }
$pathSafetyLocal = if ($ScriptDirectory) {
    Join-Path (Split-Path $ScriptDirectory -Parent) 'common/path_safety.sh'
} else { $null }

function Write-Step($msg)  { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Ok($msg)    { Write-Host "[OK] $msg"      -ForegroundColor Green }
function Write-Warn2($msg) { Write-Host "[AVISO] $msg"   -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "[ERRO] $msg"    -ForegroundColor Red }

function Test-Sha256Value([string]$Value) {
    return $Value -match '^[a-fA-F0-9]{64}$'
}

function Test-ImmutableVersion([string]$Value) {
    if ([string]::IsNullOrWhiteSpace($Value)) { return $false }
    if ($Value -notmatch '^[A-Za-z0-9][A-Za-z0-9._+-]{0,127}$') { return $false }
    return $Value -notmatch '^(?i:main|latest)$'
}

function Test-SecureHttpsUri([string]$Value, [string]$Version) {
    if ([string]::IsNullOrWhiteSpace($Value) -or [string]::IsNullOrWhiteSpace($Version)) { return $false }
    if ($Value -match '[\s\\]' -or $Value.Contains('?') -or $Value.Contains('#')) { return $false }
    $parsed = $null
    if (-not [System.Uri]::TryCreate($Value, [System.UriKind]::Absolute, [ref]$parsed)) { return $false }
    if ($parsed.Scheme -ine 'https' -or -not [string]::IsNullOrEmpty($parsed.UserInfo) -or -not [string]::IsNullOrEmpty($parsed.Query) -or -not [string]::IsNullOrEmpty($parsed.Fragment)) { return $false }
    if ($Value -match '(?i)(?:^|[/?&=])(main|latest)(?:$|[/?&=])') { return $false }
    return $Value.IndexOf($Version, [System.StringComparison]::Ordinal) -ge 0
}

function Convert-CrlfToLf([string]$Path) {
    # O hash publicado refere-se aos bytes canônicos LF que serão executados.
    [byte[]]$source = [System.IO.File]::ReadAllBytes($Path)
    $normalized = New-Object System.IO.MemoryStream
    try {
        for ($index = 0; $index -lt $source.Length; $index++) {
            if ($source[$index] -eq 13 -and ($index + 1) -lt $source.Length -and $source[$index + 1] -eq 10) {
                continue
            }
            [void]$normalized.WriteByte($source[$index])
        }
        [System.IO.File]::WriteAllBytes($Path, $normalized.ToArray())
    } finally {
        $normalized.Dispose()
    }
}

function Test-VerifiedFile([string]$Path, [string]$ExpectedSha256, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Label não encontrado: $Path"
    }
    if (-not (Test-Sha256Value $ExpectedSha256)) {
        throw "$Label requer SHA-256 explícito de 64 dígitos."
    }
    $actual = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
    if (-not [string]::Equals($actual, $ExpectedSha256, [System.StringComparison]::OrdinalIgnoreCase)) {
        Remove-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
        throw "SHA-256 divergente para $Label; artefato descartado."
    }
}

function Get-ArtifactCacheRoot([string]$Version, [string]$ProvisionHash, [string]$CommonHash, [string]$PathSafetyHash) {
    $temporaryRoot = if ($env:TEMP) { $env:TEMP } else { [System.IO.Path]::GetTempPath() }
    $cacheKey = '{0}-{1}-{2}-{3}' -f $Version, $ProvisionHash.ToLowerInvariant(), $CommonHash.ToLowerInvariant(), $PathSafetyHash.ToLowerInvariant()
    return Join-Path (Join-Path $temporaryRoot 'OpenCodeEcosystemInstaller') $cacheKey
}

function Get-VerifiedArtifact([string]$Uri, [string]$Version, [string]$ExpectedSha256, [string]$Destination, [string]$Label, [switch]$NormalizeLineEndings) {
    if (-not (Test-ImmutableVersion $Version)) {
        throw "$Label requer versão explícita e imutável."
    }
    if (-not (Test-SecureHttpsUri $Uri $Version)) {
        throw "$Label requer URL HTTPS versionada, sem credenciais, fragmentos ou referências móveis."
    }
    if (-not (Test-Sha256Value $ExpectedSha256)) {
        throw "$Label requer SHA-256 explícito de 64 dígitos."
    }
    if (Test-Path -LiteralPath $Destination -PathType Container) {
        throw "$Label possui destino de cache inválido (diretório)."
    }
    New-Item -ItemType Directory -Path (Split-Path -Parent $Destination) -Force | Out-Null
    if (Test-Path -LiteralPath $Destination) {
        try {
            Test-VerifiedFile -Path $Destination -ExpectedSha256 $ExpectedSha256 -Label "$Label em cache"
            Write-Ok "$Label reutilizado de cache revalidado por SHA-256."
            return
        } catch {
            # Test-VerifiedFile já descarta bytes inválidos antes do download.
        }
    }
    $temporary = "$Destination.download"
    Remove-Item -LiteralPath $temporary -Force -ErrorAction SilentlyContinue
    try {
        # Redirecionamentos são recusados, em vez de seguir um possível downgrade.
        Invoke-WebRequest -Uri $Uri -OutFile $temporary -UseBasicParsing -MaximumRedirection 0
        if ($NormalizeLineEndings) { Convert-CrlfToLf -Path $temporary }
        Test-VerifiedFile -Path $temporary -ExpectedSha256 $ExpectedSha256 -Label $Label
        Move-Item -LiteralPath $temporary -Destination $Destination -Force
    } catch {
        Remove-Item -LiteralPath $temporary -Force -ErrorAction SilentlyContinue
        throw
    }
}

function Assert-InstallationInputs([bool]$HasLocalProvision, [bool]$HasLocalCommon, [bool]$HasLocalPathSafety) {
    if (-not (Test-ImmutableVersion $ProvisionVersion)) {
        throw 'Informe -ProvisionVersion com uma versão imutável de provision.sh.'
    }
    if (-not (Test-Sha256Value $ProvisionSha256)) {
        throw 'Informe -ProvisionSha256 com o hash SHA-256 publicado para provision.sh.'
    }
    if (-not (Test-Sha256Value $CommonInstallerSha256)) {
        throw 'Informe -CommonInstallerSha256 para installer/common/install_clis.sh.'
    }
    if (-not (Test-Sha256Value $PathSafetySha256)) {
        throw 'Informe -PathSafetySha256 para installer/common/path_safety.sh.'
    }
    if ($EcosystemRef -notmatch '^[a-fA-F0-9]{40}$') {
        throw 'Informe ECOSYSTEM_REF (ou -EcosystemRef) como hash completo de commit Git.'
    }
    if (-not [string]::IsNullOrWhiteSpace($ProvisionUri) -and -not (Test-SecureHttpsUri $ProvisionUri $ProvisionVersion)) {
        throw 'ProvisionUri deve ser HTTPS, conter a versão e não usar referências móveis.'
    }
    if (-not $HasLocalProvision -and -not (Test-SecureHttpsUri $ProvisionUri $ProvisionVersion)) {
        throw 'provision.sh local ausente: informe ProvisionUri HTTPS versionada e verificável.'
    }
    if (-not $HasLocalCommon) {
        throw 'installer/common/install_clis.sh deve estar presente no checkout local.'
    }
    if (-not $HasLocalPathSafety) {
        throw 'installer/common/path_safety.sh deve estar presente no checkout local.'
    }
}

function ConvertTo-BashSingleQuoted([string]$Value) {
    $quote = [string][char]39
    return $quote + $Value.Replace($quote, $quote + '"' + $quote + '"' + $quote) + $quote
}

function New-WslEnvironmentEntry([string]$Name, [AllowNull()][object]$Value) {
    # URLs, versões e hashes são validados pelo provisionador. Aqui só
    # protegemos o transporte argv para não permitir quebra de linha/injeção.
    if ($Name -notmatch '^[A-Z][A-Z0-9_]*$') {
        throw "Nome de variável WSL inválido: $Name"
    }
    if ($null -eq $Value) {
        $Value = ''
    }
    if ($Value -isnot [string]) {
        throw "$Name deve ser uma string para ser encaminhada ao WSL."
    }
    if ($Value.Contains("`r") -or $Value.Contains("`n")) {
        throw "$Name não pode conter CR ou LF."
    }
    return ('{0}={1}' -f $Name, $Value)
}

function Convert-WindowsPathToWslPath([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path)) {
        throw 'Caminho Windows ausente para o checkout-fonte local.'
    }
    $resolved = (Resolve-Path -LiteralPath $Path -ErrorAction Stop).Path
    if ($resolved -notmatch '^[A-Za-z]:\\') {
        throw "Checkout-fonte deve estar em unidade local montável pelo WSL: $resolved"
    }
    $drive = $resolved.Substring(0, 1).ToLowerInvariant()
    $rest = $resolved.Substring(2) -replace '\\', '/'
    return "/mnt/$drive$rest"
}

$externalArtifactInputs = @(
    [PSCustomObject]@{ Name = 'OPENCODE_INSTALLER_URL'; Value = $OPENCODE_INSTALLER_URL }
    [PSCustomObject]@{ Name = 'OPENCODE_INSTALLER_SHA256'; Value = $OPENCODE_INSTALLER_SHA256 }
    [PSCustomObject]@{ Name = 'OPENCODE_ARTIFACT_VERSION'; Value = $OPENCODE_ARTIFACT_VERSION }
    [PSCustomObject]@{ Name = 'OPENCODE_NPM_VERSION'; Value = $OPENCODE_NPM_VERSION }
    [PSCustomObject]@{ Name = 'OPENCODE_NPM_SHA256'; Value = $OPENCODE_NPM_SHA256 }
    [PSCustomObject]@{ Name = 'ANTIGRAVITY_INSTALLER_URL'; Value = $ANTIGRAVITY_INSTALLER_URL }
    [PSCustomObject]@{ Name = 'ANTIGRAVITY_INSTALLER_SHA256'; Value = $ANTIGRAVITY_INSTALLER_SHA256 }
    [PSCustomObject]@{ Name = 'ANTIGRAVITY_ARTIFACT_VERSION'; Value = $ANTIGRAVITY_ARTIFACT_VERSION }
    [PSCustomObject]@{ Name = 'CLAUDE_CODE_VERSION'; Value = $CLAUDE_CODE_VERSION }
    [PSCustomObject]@{ Name = 'CLAUDE_CODE_NPM_SHA256'; Value = $CLAUDE_CODE_NPM_SHA256 }
    [PSCustomObject]@{ Name = 'OLLAMA_BINARY_URL'; Value = $OLLAMA_BINARY_URL }
    [PSCustomObject]@{ Name = 'OLLAMA_BINARY_SHA256'; Value = $OLLAMA_BINARY_SHA256 }
    [PSCustomObject]@{ Name = 'OLLAMA_ARTIFACT_VERSION'; Value = $OLLAMA_ARTIFACT_VERSION }
)

function Assert-WslExternalArtifactInputs([object[]]$Entries) {
    foreach ($entry in $Entries) {
        [void](New-WslEnvironmentEntry -Name $entry.Name -Value $entry.Value)
    }
}

function Assert-VerifiedHttpsArtifact([string]$Label, [string]$Uri, [string]$Version, [string]$Sha256) {
    if (-not (Test-ImmutableVersion $Version)) {
        throw "$Label requer versão explícita e imutável."
    }
    if (-not (Test-SecureHttpsUri $Uri $Version)) {
        throw "$Label requer URL HTTPS versionada, sem credenciais, consultas, fragmentos ou referências móveis."
    }
    if (-not (Test-Sha256Value $Sha256)) {
        throw "$Label requer SHA-256 explícito de 64 dígitos."
    }
}

function Assert-VerifiedNpmArtifact([string]$Label, [string]$Version, [string]$Sha256) {
    if (-not (Test-ImmutableVersion $Version)) {
        throw "$Label requer versão NPM explícita e imutável."
    }
    if (-not (Test-Sha256Value $Sha256)) {
        throw "$Label requer SHA-256 do tarball NPM principal."
    }
}

function Assert-ExternalArtifactProvenance {
    # Assert-WslExternalArtifactInputs já recusou tipos não textuais e CR/LF.
    # Esta etapa é pura: ocorre antes de WSL, downloads ou privilégios no WSL.
    if (-not [string]::IsNullOrEmpty([string]$OPENCODE_INSTALLER_URL)) {
        Assert-VerifiedHttpsArtifact -Label 'OpenCode CLI' -Uri $OPENCODE_INSTALLER_URL -Version $OPENCODE_ARTIFACT_VERSION -Sha256 $OPENCODE_INSTALLER_SHA256
    } else {
        if (-not [string]::IsNullOrEmpty([string]$OPENCODE_INSTALLER_SHA256) -or -not [string]::IsNullOrEmpty([string]$OPENCODE_ARTIFACT_VERSION)) {
            throw 'Metadados do instalador OpenCode exigem OPENCODE_INSTALLER_URL.'
        }
        Assert-VerifiedNpmArtifact -Label 'OpenCode CLI' -Version $OPENCODE_NPM_VERSION -Sha256 $OPENCODE_NPM_SHA256
    }
    Assert-VerifiedHttpsArtifact -Label 'Antigravity CLI' -Uri $ANTIGRAVITY_INSTALLER_URL -Version $ANTIGRAVITY_ARTIFACT_VERSION -Sha256 $ANTIGRAVITY_INSTALLER_SHA256
    Assert-VerifiedNpmArtifact -Label 'Claude Code CLI' -Version $CLAUDE_CODE_VERSION -Sha256 $CLAUDE_CODE_NPM_SHA256
    Assert-VerifiedHttpsArtifact -Label 'Ollama' -Uri $OLLAMA_BINARY_URL -Version $OLLAMA_ARTIFACT_VERSION -Sha256 $OLLAMA_BINARY_SHA256
}

function Test-WslArtifactHashes([string]$WslRoot, [string]$ProvisionHash, [string]$CommonHash, [string]$PathSafetyHash, [string]$WslUser) {
    $expectedProvision = $ProvisionHash.ToLowerInvariant()
    $expectedCommon = $CommonHash.ToLowerInvariant()
    $expectedPathSafety = $PathSafetyHash.ToLowerInvariant()
    $quotedWslRoot = ConvertTo-BashSingleQuoted $WslRoot
    $verificationCommand = @"
set -eu
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PATH
root=$quotedWslRoot
provision_actual=`$(sha256sum "`$root/windows/provision.sh" | cut -d ' ' -f1)
common_actual=`$(sha256sum "`$root/common/install_clis.sh" | cut -d ' ' -f1)
path_safety_actual=`$(sha256sum "`$root/common/path_safety.sh" | cut -d ' ' -f1)
test "`$provision_actual" = "$expectedProvision"
test "`$common_actual" = "$expectedCommon"
test "`$path_safety_actual" = "$expectedPathSafety"
"@
    $wslSanitizedEnvironment = @(
        'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
        "HOME=/home/$WslUser"
        "USER=$WslUser"
        "LOGNAME=$WslUser"
        'BASH_ENV='
        'ENV='
    )
    & $WslExe -d $Distro -- /usr/bin/env -i $wslSanitizedEnvironment /bin/bash --noprofile --norc -c $verificationCommand
    if ($LASTEXITCODE -ne 0) {
        throw 'Os bytes copiados para o WSL não correspondem aos SHA-256 verificados.'
    }
}

function Test-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    (New-Object Security.Principal.WindowsPrincipal($id)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# ---------------------------------------------------------------------------
# Detecção robusta de distro WSL (corrige bug UTF-16 de $WslExe -l -q)
# $WslExe -l -q retorna UTF-16 LE; o PowerShell lê como bytes nulos/vazio.
# Esta função força a decodificação correta e ainda tenta fallback via
# $WslExe --list --verbose para garantir compatibilidade com builds mais antigos.
# ---------------------------------------------------------------------------
function Test-WslDistro([string]$Name) {
    # Tentativa 1: forçar decodificação UTF-16 LE
    try {
        $prev = [Console]::OutputEncoding
        [Console]::OutputEncoding = [System.Text.Encoding]::Unicode
        $list = (& $WslExe -l -q 2>$null) -join "`n"
        [Console]::OutputEncoding = $prev
        if ($list -match [regex]::Escape($Name)) { return $true }
    } catch { }

    # Tentativa 2: wsl --list --verbose (disponível no WSL2 moderno)
    try {
        $verbose = (& $WslExe --list --verbose 2>$null) -join "`n"
        if ($verbose -match [regex]::Escape($Name)) { return $true }
    } catch { }

    # Tentativa 3: verificar saída bruta de bytes e decodificar manualmente
    try {
        $raw = & $WslExe -l -q 2>$null
        $decoded = [System.Text.Encoding]::Unicode.GetString(
            [System.Text.Encoding]::Default.GetBytes(($raw -join "`n"))
        )
        if ($decoded -match [regex]::Escape($Name)) { return $true }
    } catch { }

    return $false
}

# ----------------------------------------------------------------------------
# 0. Pré-checagens
# ----------------------------------------------------------------------------
Write-Host @"
===================================================================
  OpenCode Ecosystem Core - Instalador Windows (WSL2 + Ubuntu)
  OpenCode CLI + Antigravity CLI + Ollama + Ecossistema nativo
===================================================================
"@ -ForegroundColor Magenta

if (-not (Test-Admin)) {
    Write-Err "Este script precisa ser executado como ADMINISTRADOR."
    Write-Host "Clique com o botao direito no PowerShell > 'Executar como administrador' e rode novamente."
    exit 1
}

$build = [System.Environment]::OSVersion.Version.Build
if ($build -lt 19041) {
    Write-Err "Windows build $build nao suporta WSL2 (requer build 19041+ / Windows 10 2004+)."
    exit 1
}
Write-Ok "Windows build $build compativel com WSL2."

if (-not $ScriptSelf) {
    Write-Err "O script deve ser salvo localmente para validar a instalação."
    exit 1
}
$hasLocalProvision = [bool]($provisionLocal -and (Test-Path -LiteralPath $provisionLocal))
$hasLocalCommon = [bool]($commonLocal -and (Test-Path -LiteralPath $commonLocal))
$hasLocalPathSafety = [bool]($pathSafetyLocal -and (Test-Path -LiteralPath $pathSafetyLocal))
try {
    # Valida todos os dados antes de solicitar a instalação do WSL.
    Assert-InstallationInputs -HasLocalProvision $hasLocalProvision -HasLocalCommon $hasLocalCommon -HasLocalPathSafety $hasLocalPathSafety
    Assert-WslExternalArtifactInputs -Entries $externalArtifactInputs
    Assert-ExternalArtifactProvenance
    [void](New-WslEnvironmentEntry -Name 'ECOSYSTEM_REF' -Value $EcosystemRef)
} catch {
    Write-Err $_.Exception.Message
    exit 1
}

# Os bytes que poderão ser executados no WSL são preparados e conferidos antes
# de qualquer instalação de WSL/DISM. Uma falha de procedência não altera o SO.
$tempInstallerRoot = Get-ArtifactCacheRoot -Version $ProvisionVersion -ProvisionHash $ProvisionSha256 -CommonHash $CommonInstallerSha256 -PathSafetyHash $PathSafetySha256
$tempProvision = Join-Path $tempInstallerRoot 'windows/provision.sh'
$tempCommon = Join-Path $tempInstallerRoot 'common/install_clis.sh'
$tempPathSafety = Join-Path $tempInstallerRoot 'common/path_safety.sh'
try {
    New-Item -ItemType Directory -Path (Split-Path -Parent $tempProvision) -Force | Out-Null
    New-Item -ItemType Directory -Path (Split-Path -Parent $tempCommon) -Force | Out-Null

    if ($provisionLocal -and (Test-Path -LiteralPath $provisionLocal)) {
        Copy-Item -LiteralPath $provisionLocal -Destination $tempProvision -Force
        Convert-CrlfToLf -Path $tempProvision
        Test-VerifiedFile -Path $tempProvision -ExpectedSha256 $ProvisionSha256 -Label 'provision.sh local'
        Write-Ok "provision.sh local normalizado e verificado por SHA-256."
    } else {
        Get-VerifiedArtifact -Uri $ProvisionUri -Version $ProvisionVersion -ExpectedSha256 $ProvisionSha256 -Destination $tempProvision -Label 'provision.sh' -NormalizeLineEndings
        Write-Ok "provision.sh versionado, normalizado e verificado por SHA-256."
    }
    if (-not ($commonLocal -and (Test-Path -LiteralPath $commonLocal))) {
        throw 'installer/common/install_clis.sh deve estar presente no checkout local; nenhum fallback remoto será usado.'
    }
    Copy-Item -LiteralPath $commonLocal -Destination $tempCommon -Force
    Convert-CrlfToLf -Path $tempCommon
    Test-VerifiedFile -Path $tempCommon -ExpectedSha256 $CommonInstallerSha256 -Label 'installer/common/install_clis.sh'
    Write-Ok "Biblioteca comum de CLIs normalizada e verificada por SHA-256."
    Copy-Item -LiteralPath $pathSafetyLocal -Destination $tempPathSafety -Force
    Convert-CrlfToLf -Path $tempPathSafety
    Test-VerifiedFile -Path $tempPathSafety -ExpectedSha256 $PathSafetySha256 -Label 'installer/common/path_safety.sh'
    Write-Ok "Biblioteca comum de validação de caminhos normalizada e verificada por SHA-256."
} catch {
    Write-Err "Falha ao preparar os artefatos verificados antes do WSL: $($_.Exception.Message)"
    exit 1
}

# ----------------------------------------------------------------------------
# 1. Proteções do Windows
# ----------------------------------------------------------------------------
Write-Step "Etapa 1/5: Preservando proteções do Windows"
Write-Ok "Defender, Firewall e verificações de origem permanecem inalterados."

# ----------------------------------------------------------------------------
# 2. WSL2 + Ubuntu
# ----------------------------------------------------------------------------
Write-Step "Etapa 2/5: Verificando WSL2 + Ubuntu"

$wslInstalled    = $false
$distroInstalled = $false
try {
    $null = & $WslExe --status 2>$null
    if ($LASTEXITCODE -eq 0) { $wslInstalled = $true }
} catch { $wslInstalled = $false }

if ($wslInstalled) {
    # Usa função robusta que corrige bug de codificação UTF-16
    $distroInstalled = Test-WslDistro -Name $Distro
}

if (-not $wslInstalled -or -not $distroInstalled) {
    Write-Warn2 "WSL/Ubuntu ausente. Instalando agora (isso pode demorar varios minutos)..."
    & $WslExe --install -d $Distro
    if ($LASTEXITCODE -ne 0) {
        Write-Warn2 "Instalacao direta falhou; habilitando features manualmente..."
        & $DismExe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Err "Falha ao habilitar Microsoft-Windows-Subsystem-Linux."
            exit 1
        }
        & $DismExe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Err "Falha ao habilitar VirtualMachinePlatform."
            exit 1
        }
    }

    Write-Host ""
    Write-Warn2 "REINICIALIZACAO NECESSARIA para concluir a instalacao do WSL."
    Write-Host  "Após reiniciar, faça a retomada manual executando novamente este arquivo local com os mesmos parâmetros validados." -ForegroundColor Yellow
    Write-Host  "Se o Ubuntu abrir pedindo usuario/senha, crie-os e feche a janela." -ForegroundColor Yellow
    $answer = Read-Host "Reiniciar agora? (S/N)"
    if ($answer -match '^[sS]') {
        Restart-Computer -Force
    } else {
        Write-Warn2 "Reinicialização adiada; após reiniciar, faça a retomada manual pelo arquivo local."
    }
    exit 0
}
Write-Ok "WSL2 + Ubuntu ja instalados."

# Garante usuário default configurado (primeira execução do Ubuntu)
$userCheck = (& $WslExe -d $Distro -- /usr/bin/whoami 2>$null)
if ($LASTEXITCODE -ne 0 -or -not $userCheck) {
    Write-Warn2 "O Ubuntu precisa de configuracao inicial (usuario/senha)."
    Write-Host "Uma janela do Ubuntu vai abrir. Crie seu usuario/senha, digite 'exit' e este instalador continuara."
    Start-Process -FilePath $WslExe -ArgumentList "-d $Distro" -Wait
}
$wslUser = (& $WslExe -d $Distro -- /usr/bin/whoami).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($wslUser) -or $wslUser -notmatch '^[a-z_][a-z0-9_-]{0,31}$') {
    Write-Err "Não foi possível confirmar o usuário padrão do Ubuntu."
    exit 1
}
Write-Ok "Ubuntu operacional (usuario: $wslUser)."
$wslSanitizedEnvironment = @(
    'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
    "HOME=/home/$wslUser"
    "USER=$wslUser"
    "LOGNAME=$wslUser"
    'BASH_ENV='
    'ENV='
)

# ----------------------------------------------------------------------------
# 3. Provisionamento dentro do Ubuntu
# ----------------------------------------------------------------------------
Write-Step "Etapa 3/5: Provisionando o Ubuntu (CLIs + Ecossistema)"

try {
    # Rehash no host reduz a janela entre o preflight anterior e a cópia WSL.
    Test-VerifiedFile -Path $tempProvision -ExpectedSha256 $ProvisionSha256 -Label 'provision.sh pronto para staging'
    Test-VerifiedFile -Path $tempCommon -ExpectedSha256 $CommonInstallerSha256 -Label 'installer/common/install_clis.sh pronto para staging'
    Test-VerifiedFile -Path $tempPathSafety -ExpectedSha256 $PathSafetySha256 -Label 'installer/common/path_safety.sh pronto para staging'

    # Conversão Windows -> WSL só aceita um cache em unidade local montável.
    if ($tempInstallerRoot -notmatch '^[A-Za-z]:\\') {
        throw "Cache temporário não montável pelo WSL: $tempInstallerRoot"
    }
    $drive = $tempInstallerRoot.Substring(0, 1).ToLowerInvariant()
    $rest = $tempInstallerRoot.Substring(2) -replace '\\', '/'
    $wslPath = "/mnt/$drive$rest"
    $wslProvisionSource = ConvertTo-BashSingleQuoted "$wslPath/windows/provision.sh"
    $wslCommonSource = ConvertTo-BashSingleQuoted "$wslPath/common/install_clis.sh"
    $wslPathSafetySource = ConvertTo-BashSingleQuoted "$wslPath/common/path_safety.sh"
    $prepareWslCommand = @"
set -eu
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PATH
umask 077
safe_directory() {
    candidate=`$1
    if [ -L "`$candidate" ]; then
        printf '%s\n' "staging WSL recusado: componente simbólico em `$candidate" >&2
        exit 1
    fi
    if [ -e "`$candidate" ]; then
        [ -d "`$candidate" ] || { printf '%s\n' "staging WSL recusado: não diretório em `$candidate" >&2; exit 1; }
    else
        mkdir -- "`$candidate"
    fi
    [ ! -L "`$candidate" ] && [ -d "`$candidate" ] || { printf '%s\n' "staging WSL recusado após criação em `$candidate" >&2; exit 1; }
    [ "`$(stat -c '%u' "`$candidate")" = "`$(id -u)" ] || { printf '%s\n' "staging WSL recusado: proprietário inesperado em `$candidate" >&2; exit 1; }
    mode=`$(stat -c '%a' "`$candidate")
    [ `$((8#`$mode & 8#022)) -eq 0 ] || { printf '%s\n' "staging WSL recusado: permissões externas em `$candidate" >&2; exit 1; }
}
case "`${HOME:-}" in /*) ;; *) printf '%s\n' 'staging WSL recusado: HOME inválido' >&2; exit 1 ;; esac
safe_directory "`$HOME"
safe_directory "`$HOME/.cache"
safe_directory "`$HOME/.cache/opencode-ecosystem-installer"
root=`$(mktemp -d "`$HOME/.cache/opencode-ecosystem-installer/session.XXXXXX")
[ -d "`$root" ] && [ ! -L "`$root" ] || { printf '%s\n' 'staging WSL recusado: sessão inválida' >&2; exit 1; }
mkdir -- "`$root/windows" "`$root/common"
cp $wslProvisionSource "`$root/windows/provision.sh"
cp $wslCommonSource "`$root/common/install_clis.sh"
cp $wslPathSafetySource "`$root/common/path_safety.sh"
chmod 700 "`$root/windows/provision.sh" "`$root/common/install_clis.sh" "`$root/common/path_safety.sh"
printf '%s\n' "`$root"
"@
    $preparedWslRoot = [string](& $WslExe -d $Distro -- /usr/bin/env -i $wslSanitizedEnvironment /bin/bash --noprofile --norc -c $prepareWslCommand | Select-Object -Last 1)
    $prepareExitCode = $LASTEXITCODE
    if ($prepareExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($preparedWslRoot)) {
        throw 'Falha ao copiar os artefatos verificados para o WSL.'
    }
    $wslInstallerRoot = $preparedWslRoot.Trim()
    if ($wslInstallerRoot -notmatch '^/[A-Za-z0-9._/-]+$' -or $wslInstallerRoot -match '/(?:\.|\.\.)/') {
        throw "Diretório de staging WSL inválido: $wslInstallerRoot"
    }
    if (-not $ScriptDirectory) {
        throw 'Não foi possível localizar o checkout-fonte local do wrapper.'
    }
    $checkoutRoot = Split-Path -Parent (Split-Path -Parent $ScriptDirectory)
    $wslSourceCheckout = Convert-WindowsPathToWslPath -Path $checkoutRoot
    $wslEnvironment = @(
        (New-WslEnvironmentEntry -Name 'ECOSYSTEM_REF' -Value $EcosystemRef)
        (New-WslEnvironmentEntry -Name 'ECOSYSTEM_SOURCE_DIR' -Value $wslSourceCheckout)
        (New-WslEnvironmentEntry -Name 'ECOSYSTEM_STAGED_INSTALLER' -Value '1')
        (New-WslEnvironmentEntry -Name 'ECOSYSTEM_PROVISION_SHA256' -Value $ProvisionSha256)
        (New-WslEnvironmentEntry -Name 'ECOSYSTEM_COMMON_INSTALLER_SHA256' -Value $CommonInstallerSha256)
        (New-WslEnvironmentEntry -Name 'ECOSYSTEM_PATH_SAFETY_SHA256' -Value $PathSafetySha256)
    )
    foreach ($entry in $externalArtifactInputs) {
        $wslEnvironment += (New-WslEnvironmentEntry -Name $entry.Name -Value $entry.Value)
    }
    # Rehash dentro do WSL: os bytes executados são os bytes aprovados acima.
    Test-WslArtifactHashes -WslRoot $wslInstallerRoot -ProvisionHash $ProvisionSha256 -CommonHash $CommonInstallerSha256 -PathSafetyHash $PathSafetySha256 -WslUser $wslUser
} catch {
    Write-Err "Falha ao preparar os artefatos verificados no WSL: $($_.Exception.Message)"
    exit 1
}
Write-Host "Executando provisionamento (OpenCode CLI, Antigravity, Ollama, Ecossistema)..." -ForegroundColor Cyan
Write-Host "Isso pode levar de 5 a 20 minutos dependendo da conexao.`n"
$quotedWslProvision = ConvertTo-BashSingleQuoted "$wslInstallerRoot/windows/provision.sh"
$wslRuntimeEnvironment = $wslSanitizedEnvironment + $wslEnvironment
& $WslExe -d $Distro -- /usr/bin/env -i $wslRuntimeEnvironment /bin/bash --noprofile --norc -c "exec $quotedWslProvision"
if ($LASTEXITCODE -ne 0) {
    Write-Err "Provisionamento falhou; atalhos não serão criados. Consulte ~/.opencode-ecosystem-install.log no Ubuntu."
    exit 1
}
Write-Ok "Provisionamento concluido."

# ----------------------------------------------------------------------------
# 4. Atalhos na Área de Trabalho (Limpeza e Recriação do Zero)
# ----------------------------------------------------------------------------
Write-Step "Etapa 4/5: Criando atalhos na Area de Trabalho"

$Desktop = [Environment]::GetFolderPath('Desktop')
$WShell  = New-Object -ComObject WScript.Shell
$EcoDir  = "/home/$wslUser/opencode-ecosystem-core"
$VenvPython = "$EcoDir/.venv/bin/python"
$quotedVenvPython = ConvertTo-BashSingleQuoted $VenvPython
& $WslExe -d $Distro -- /usr/bin/env -i $wslSanitizedEnvironment /bin/bash --noprofile --norc -c "test -x $quotedVenvPython"
if ($LASTEXITCODE -ne 0) {
    Write-Err "A virtualenv esperada não está disponível; atalhos não serão criados."
    exit 1
}

# Remove atalhos antigos para recriar do zero
$oldShortcuts = @(
    'OpenCode Ecosystem.lnk',
    'Antigravity CLI.lnk',
    'Claude Code CLI.lnk',
    'Claude Code (Ecosystem).lnk',
    'Ecosystem (marceloclaro).lnk'
)
foreach ($oldSc in $oldShortcuts) {
    $scPath = Join-Path $Desktop $oldSc
    if (Test-Path $scPath) {
        Remove-Item $scPath -Force -ErrorAction SilentlyContinue
    }
}

# Prepara ícone do ecossistema
$AppDir = Join-Path $env:LOCALAPPDATA 'OpenCodeEcosystem'
if (-not (Test-Path $AppDir)) { New-Item -ItemType Directory -Path $AppDir -Force | Out-Null }
$LocalIco = Join-Path $AppDir 'icon.ico'

try {
    $wslIco = "\\wsl.localhost\$Distro\home\$wslUser\opencode-ecosystem-core\assets\icon.ico"
    if (Test-Path $wslIco) {
        Copy-Item $wslIco $LocalIco -Force -ErrorAction SilentlyContinue
    }
} catch { }
$IconTarget = if (Test-Path $LocalIco) { $LocalIco } else { "$WslExe,0" }

function New-EcoShortcut {
    param([string]$Name, [string]$Arguments, [string]$Description, [string]$IconLocation)
    $lnkPath = Join-Path $Desktop "$Name.lnk"
    $sc = $WShell.CreateShortcut($lnkPath)
    $sc.TargetPath  = $WslExe
    $sc.Arguments   = $Arguments
    $sc.Description = $Description
    $sc.WorkingDirectory = $env:USERPROFILE
    if ($IconLocation) { $sc.IconLocation = $IconLocation }
    $sc.Save()
    Write-Ok "Atalho criado: $Name"
}

New-EcoShortcut -Name 'OpenCode Ecosystem' `
    -Arguments "-d $Distro --cd $EcoDir -- /bin/bash -lic `"opencode`"" `
    -Description 'OpenCode CLI com o OpenCode Ecosystem Core nativo (209 agentes + 6 MCPs + APM)' `
    -IconLocation $IconTarget

New-EcoShortcut -Name 'Antigravity CLI' `
    -Arguments "-d $Distro --cd $EcoDir -- /bin/bash -lic `"agy`"" `
    -Description 'Google Antigravity CLI no diretorio do ecossistema' `
    -IconLocation $IconTarget

New-EcoShortcut -Name 'Claude Code CLI' `
    -Arguments "-d $Distro --cd $EcoDir -- /bin/bash -lic `"claude`"" `
    -Description 'Claude Code CLI no diretorio do ecossistema' `
    -IconLocation $IconTarget

New-EcoShortcut -Name 'Ecosystem (marceloclaro)' `
    -Arguments "-d $Distro --cd $EcoDir -- /bin/bash -lic `"$EcoDir/.venv/bin/python -m marceloclaro.cli`"" `
    -Description 'CLI interativo do orquestrador metacognitivo marceloclaro' `
    -IconLocation "$env:SystemRoot\System32\cmd.exe,0"

# ----------------------------------------------------------------------------
# 5. Resumo final
# ----------------------------------------------------------------------------
Write-Step "Etapa 5/5: Concluido com Sucesso!"
Write-Host @"

===================================================================
  INSTALACAO CONCLUIDA — OPENCODE ECOSYSTEM CORE v3.9.0
===================================================================
  Atalhos criados na Area de Trabalho:
    [1] OpenCode Ecosystem        -> OpenCode CLI + 209 agentes nativos
    [2] Antigravity CLI           -> Google Antigravity (agy)
    [3] Claude Code CLI           -> Claude Code CLI (@anthropic-ai)
    [4] Ecosystem (marceloclaro)  -> CLI do orquestrador metacognitivo

  Recursos Configurados:
    - WSL2 + Ubuntu Linux otimizado
    - 209 Agentes Especialistas + 6 Servidores MCP
    - Microsoft APM (222 primitivas gerenciadas)
    - Raciocínio Formal: AlphaProof, AlphaGeometry, Lean 4 e E-Graph
    - Modelos Locais Ollama & Colibri MoE em C nativo

  Primeiros Passos:
    - Diagnóstico de saúde:  wsl -d Ubuntu -- /bin/bash -lic "cd ~/opencode-ecosystem-core && .venv/bin/python -m marceloclaro.cli doctor"
    - Modelos locais free:   wsl -d Ubuntu -- ollama pull llama3.2
    - Log de instalacao:     ~/.opencode-ecosystem-install.log (no Ubuntu)
===================================================================
"@ -ForegroundColor Green
