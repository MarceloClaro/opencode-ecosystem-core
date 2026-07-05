# ============================================================================
# OpenCode Ecosystem Core - Instalador Automático para Windows
# ----------------------------------------------------------------------------
# O que este script faz:
#   1. Instala o WSL2 + Ubuntu (se ausente), com retomada automática pós-reboot
#   2. Provisiona o Ubuntu: OpenCode CLI, Antigravity CLI, Ollama CLI
#   3. Instala o opencode-ecosystem-core (nativo no OpenCode CLI)
#   4. Cria atalhos na Área de Trabalho (1 clique):
#        - "OpenCode Ecosystem"       -> abre o OpenCode CLI dentro do ecossistema
#        - "Antigravity CLI"          -> abre o agy dentro do ecossistema
#        - "Ecosystem (marceloclaro)" -> abre o CLI nativo do orquestrador
#
# Como executar (PowerShell COMO ADMINISTRADOR):
#   Set-ExecutionPolicy Bypass -Scope Process -Force
#   irm https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/installer/windows/Install-OpenCodeEcosystem.ps1 | iex
# Ou baixe o arquivo e rode:  .\Install-OpenCodeEcosystem.ps1
# ============================================================================

#Requires -Version 5.1

$ErrorActionPreference = 'Stop'
$Distro     = 'Ubuntu'
$RepoRaw    = 'https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/installer/windows'
$ResumeKey  = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce'
$ResumeName = 'OpenCodeEcosystemInstaller'
$ScriptSelf = $MyInvocation.MyCommand.Path

function Write-Step($msg)  { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Ok($msg)    { Write-Host "[OK] $msg"      -ForegroundColor Green }
function Write-Warn2($msg) { Write-Host "[AVISO] $msg"   -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "[ERRO] $msg"    -ForegroundColor Red }

function Test-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    (New-Object Security.Principal.WindowsPrincipal($id)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
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

# ----------------------------------------------------------------------------
# 1. Autorizacoes do Windows (Defender, Firewall, SmartScreen)
# ----------------------------------------------------------------------------
Write-Step "Etapa 1/5: Autorizando o Ecossistema no Windows"

# 1.1. Exclusoes do Windows Defender para o WSL e pasta do ecossistema
try {
    Write-Host "Adicionando exclusoes no Windows Defender para o WSL..."
    Add-MpPreference -ExclusionProcess "wsl.exe" -ErrorAction SilentlyContinue
    Add-MpPreference -ExclusionProcess "wslhost.exe" -ErrorAction SilentlyContinue
    # Exclui a unidade de rede do WSL (onde os arquivos do Ubuntu ficam)
    Add-MpPreference -ExclusionPath "\\wsl.localhost\Ubuntu" -ErrorAction SilentlyContinue
    Add-MpPreference -ExclusionPath "\\wsl$\Ubuntu" -ErrorAction SilentlyContinue
    Write-Ok "Exclusoes do Defender aplicadas."
} catch {
    Write-Warn2 "Nao foi possivel adicionar exclusoes no Defender (pode estar desativado ou gerenciado por outra politica)."
}

# 1.2. Regras de Firewall para WSL, Ollama e MCP Servers
try {
    Write-Host "Configurando regras de Firewall para WSL e Ollama..."
    # Permite tráfego de entrada/saída para o WSL
    New-NetFirewallRule -DisplayName "OpenCode Ecosystem (WSL In)" -Direction Inbound -Program "$env:SystemRoot\System32\wsl.exe" -Action Allow -ErrorAction SilentlyContinue | Out-Null
    New-NetFirewallRule -DisplayName "OpenCode Ecosystem (WSL Out)" -Direction Outbound -Program "$env:SystemRoot\System32\wsl.exe" -Action Allow -ErrorAction SilentlyContinue | Out-Null
    # Permite portas comuns de desenvolvimento e Ollama (11434)
    New-NetFirewallRule -DisplayName "OpenCode Ecosystem (Ports)" -Direction Inbound -LocalPort 11434,3000,8000,8080 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue | Out-Null
    Write-Ok "Regras de Firewall aplicadas."
} catch {
    Write-Warn2 "Nao foi possivel configurar o Firewall."
}

# 1.3. Desabilitar bloqueio de arquivos baixados (Zone.Identifier) para a sessao atual
$env:SEE_MASK_NOZONECHECKS = 1
Write-Ok "Bloqueio de arquivos baixados (SmartScreen/ZoneChecks) desativado para a instalacao."

# ----------------------------------------------------------------------------
# 2. WSL2 + Ubuntu
# ----------------------------------------------------------------------------
Write-Step "Etapa 2/5: Verificando WSL2 + Ubuntu"

$wslInstalled    = $false
$distroInstalled = $false
try {
    $null = wsl.exe --status 2>$null
    if ($LASTEXITCODE -eq 0) { $wslInstalled = $true }
} catch { $wslInstalled = $false }

if ($wslInstalled) {
    $distros = (wsl.exe -l -q 2>$null) -join "`n"
    if ($distros -match 'Ubuntu') { $distroInstalled = $true }
}

if (-not $wslInstalled -or -not $distroInstalled) {
    Write-Warn2 "WSL/Ubuntu ausente. Instalando agora (isso pode demorar varios minutos)..."
    # Agenda retomada automática após reboot
    if ($ScriptSelf) {
        $resumeCmd = "powershell.exe -NoExit -ExecutionPolicy Bypass -File `"$ScriptSelf`""
    } else {
        $resumeCmd = "powershell.exe -NoExit -ExecutionPolicy Bypass -Command `"irm $RepoRaw/Install-OpenCodeEcosystem.ps1 | iex`""
    }
    Set-ItemProperty -Path $ResumeKey -Name $ResumeName -Value $resumeCmd -Force

    wsl.exe --install -d $Distro
    if ($LASTEXITCODE -ne 0) {
        # Método legado (features manuais) para Windows mais antigos
        Write-Warn2 "Instalacao direta falhou; habilitando features manualmente..."
        dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart | Out-Null
        dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart | Out-Null
    }

    Write-Host ""
    Write-Warn2 "REINICIALIZACAO NECESSARIA para concluir a instalacao do WSL."
    Write-Host  "Apos reiniciar, o instalador CONTINUARA AUTOMATICAMENTE." -ForegroundColor Yellow
    Write-Host  "Se o Ubuntu abrir pedindo usuario/senha, crie-os e feche a janela." -ForegroundColor Yellow
    $answer = Read-Host "Reiniciar agora? (S/N)"
    if ($answer -match '^[sS]') { Restart-Computer -Force }
    exit 0
}
Write-Ok "WSL2 + Ubuntu ja instalados."
# Remove marcador de retomada, se existir
Remove-ItemProperty -Path $ResumeKey -Name $ResumeName -ErrorAction SilentlyContinue

# Garante usuário default configurado (primeira execução do Ubuntu)
$userCheck = (wsl.exe -d $Distro -- whoami 2>$null)
if ($LASTEXITCODE -ne 0 -or -not $userCheck) {
    Write-Warn2 "O Ubuntu precisa de configuracao inicial (usuario/senha)."
    Write-Host "Uma janela do Ubuntu vai abrir. Crie seu usuario/senha, digite 'exit' e este instalador continuara."
    Start-Process -FilePath 'wsl.exe' -ArgumentList "-d $Distro" -Wait
}
$wslUser = (wsl.exe -d $Distro -- whoami).Trim()
Write-Ok "Ubuntu operacional (usuario: $wslUser)."

# ----------------------------------------------------------------------------
# 2. Provisionamento dentro do Ubuntu
# ----------------------------------------------------------------------------
Write-Step "Etapa 3/5: Provisionando o Ubuntu (CLIs + Ecossistema)"

# Obtém o provision.sh: usa cópia local (se instalador foi baixado junto) ou baixa do GitHub
$provisionLocal = if ($ScriptSelf) { Join-Path (Split-Path $ScriptSelf) 'provision.sh' } else { $null }
$tempProvision  = Join-Path $env:TEMP 'provision.sh'

if ($provisionLocal -and (Test-Path $provisionLocal)) {
    Copy-Item $provisionLocal $tempProvision -Force
    Write-Ok "Usando provision.sh local."
} else {
    Write-Host "Baixando provision.sh do GitHub..."
    Invoke-WebRequest -Uri "$RepoRaw/provision.sh" -OutFile $tempProvision -UseBasicParsing
    Write-Ok "provision.sh baixado."
}

# Copia para o WSL com fim-de-linha LF e executa
$winPath = $tempProvision -replace '\\','/' -replace '^([A-Za-z]):', { "/mnt/$($_.Groups[1].Value.ToLower())" }
# Conversão robusta do caminho Windows -> WSL
$drive   = $tempProvision.Substring(0,1).ToLower()
$rest    = $tempProvision.Substring(2) -replace '\\','/'
$wslPath = "/mnt/$drive$rest"

wsl.exe -d $Distro -- bash -c "tr -d '\r' < '$wslPath' > ~/provision.sh && chmod +x ~/provision.sh"
Write-Host "Executando provisionamento (OpenCode CLI, Antigravity, Ollama, Ecossistema)..." -ForegroundColor Cyan
Write-Host "Isso pode levar de 5 a 20 minutos dependendo da conexao.`n"
wsl.exe -d $Distro -- bash -lc "~/provision.sh"
if ($LASTEXITCODE -ne 0) {
    Write-Warn2 "Provisionamento retornou avisos. Consulte ~/.opencode-ecosystem-install.log no Ubuntu."
} else {
    Write-Ok "Provisionamento concluido."
}

# ----------------------------------------------------------------------------
# 3. Atalhos na Área de Trabalho
# ----------------------------------------------------------------------------
Write-Step "Etapa 4/5: Criando atalhos na Area de Trabalho"

$Desktop = [Environment]::GetFolderPath('Desktop')
$WShell  = New-Object -ComObject WScript.Shell
$EcoDir  = "/home/$wslUser/opencode-ecosystem-core"

function New-EcoShortcut {
    param([string]$Name, [string]$Arguments, [string]$Description, [string]$IconLocation)
    $lnkPath = Join-Path $Desktop "$Name.lnk"
    $sc = $WShell.CreateShortcut($lnkPath)
    $sc.TargetPath  = "$env:SystemRoot\System32\wsl.exe"
    $sc.Arguments   = $Arguments
    $sc.Description = $Description
    $sc.WorkingDirectory = $env:USERPROFILE
    if ($IconLocation) { $sc.IconLocation = $IconLocation }
    $sc.Save()
    Write-Ok "Atalho criado: $Name"
}

# 1 clique: OpenCode CLI aberto DENTRO do ecossistema (opencode.json nativo carrega
# os 134 agentes e o servidor MCP metacognitivo automaticamente)
New-EcoShortcut -Name 'OpenCode Ecosystem' `
    -Arguments "-d $Distro --cd $EcoDir -- bash -lic `"opencode`"" `
    -Description 'OpenCode CLI com o OpenCode Ecosystem Core nativo (134 agentes + MCP)' `
    -IconLocation "$env:SystemRoot\System32\wsl.exe,0"

# 1 clique: Antigravity CLI dentro do ecossistema
New-EcoShortcut -Name 'Antigravity CLI' `
    -Arguments "-d $Distro --cd $EcoDir -- bash -lic `"agy`"" `
    -Description 'Google Antigravity CLI no diretorio do ecossistema' `
    -IconLocation "$env:SystemRoot\System32\wsl.exe,0"

# Bônus: CLI nativo do orquestrador marceloclaro
New-EcoShortcut -Name 'Ecosystem (marceloclaro)' `
    -Arguments "-d $Distro --cd $EcoDir -- bash -lic `"python3 -m marceloclaro.cli`"" `
    -Description 'CLI interativo do orquestrador metacognitivo marceloclaro' `
    -IconLocation "$env:SystemRoot\System32\cmd.exe,0"

# ----------------------------------------------------------------------------
# 4. Resumo final
# ----------------------------------------------------------------------------
Write-Step "Etapa 5/5: Concluido!"
Write-Host @"

===================================================================
  INSTALACAO CONCLUIDA
===================================================================
  Atalhos criados na Area de Trabalho:
    [1] OpenCode Ecosystem        -> OpenCode CLI + ecossistema nativo
    [2] Antigravity CLI           -> Google Antigravity (agy)
    [3] Ecosystem (marceloclaro)  -> CLI do orquestrador metacognitivo

  Observacoes:
    - No primeiro uso do OpenCode/Antigravity, faca login quando solicitado.
    - Para modelos locais gratuitos:  wsl -d Ubuntu -- ollama pull llama3.2
    - Log de provisionamento: ~/.opencode-ecosystem-install.log (no Ubuntu)
    - Para atualizar tudo no futuro, execute novamente este instalador.
===================================================================
"@ -ForegroundColor Green
