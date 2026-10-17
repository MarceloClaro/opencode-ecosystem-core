param(
    [string]$CoreRoot='/home/marceloclaro/opencode-ecosystem-core',
    [string]$Distro='Ubuntu'
)
$ErrorActionPreference='Stop'
function Assert-CorePluginFiles([string]$Directory, [object]$ExpectedFiles) {
    if (-not (Test-Path -LiteralPath $Directory -PathType Container)) { throw 'Diretório de plugin ausente.' }
    $entries=@(Get-Item -LiteralPath $Directory -Force)+@(Get-ChildItem -LiteralPath $Directory -Recurse -Force)
    if (@($entries | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count) {
        throw 'A fonte contém links ou pontos de redirecionamento; nada foi substituído.'
    }
    $actual=@($entries | Where-Object { -not $_.PSIsContainer } | ForEach-Object { [IO.Path]::GetRelativePath($Directory,$_.FullName).Replace('\','/') })
    $expected=@($ExpectedFiles.PSObject.Properties.Name)
    if (@(Compare-Object -ReferenceObject $expected -DifferenceObject $actual).Count) {
        throw 'Arquivos inesperados ou ausentes no plugin; nada foi substituído.'
    }
    foreach ($file in $ExpectedFiles.PSObject.Properties) {
        if ((Get-FileHash -LiteralPath (Join-Path $Directory $file.Name) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $file.Value) {
            throw 'A fonte local difere deste pacote. Preserve a versão existente e prepare uma atualização explícita.'
        }
    }
}
if (-not $CoreRoot.StartsWith('/') -or $CoreRoot.Contains("`n") -or $Distro -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$') {
    throw 'Raiz Linux absoluta e distribuição WSL válida são obrigatórias.'
}
$codexExecutable=(Get-Command codex -CommandType Application -ErrorAction Stop).Source
$buildId=[Guid]::NewGuid().ToString('N')
$relativeBuild="outputs/chatgpt-plugin/$buildId"
$json=& wsl.exe -d $Distro --cd $CoreRoot --exec "$CoreRoot/.venv/bin/python" -m integrations.chatgpt_plugin --target windows-wsl --distro $Distro --destination "$relativeBuild/plugin" --archive "$relativeBuild/opencode-ecosystem-core.zip"
if ($LASTEXITCODE -ne 0) { throw 'Falha ao construir o pacote no Core.' }
$bundle=$json | ConvertFrom-Json -Depth 100
$wslRoot='\\wsl.localhost\'+$Distro+'\'+$CoreRoot.TrimStart('/').Replace('/','\')
$source=Join-Path $wslRoot "$relativeBuild/plugin"
$marketRoot=Join-Path $env:USERPROFILE '.agents/opencode-core-local'
$pluginSource=Join-Path $marketRoot 'plugins/opencode-ecosystem-core'
Assert-CorePluginFiles $source $bundle.files
if (Test-Path -LiteralPath $pluginSource) {
    Assert-CorePluginFiles $pluginSource $bundle.files
} else {
    $null=New-Item -ItemType Directory -Path (Join-Path $marketRoot 'plugins') -Force
    Copy-Item -LiteralPath $source -Destination $pluginSource -Recurse
}
$marketFile=Join-Path $marketRoot '.agents/plugins/marketplace.json'
if (Test-Path -LiteralPath $marketFile) {
    $existing=Get-Content -LiteralPath $marketFile -Raw | ConvertFrom-Json -Depth 100
    $matching=@($existing.plugins | Where-Object { $_.name -ceq 'opencode-ecosystem-core' })
    if ($existing.name -cne 'marceloclaro-core-local' -or $matching.Count -ne 1) {
        throw 'Marketplace ocupado por outra configuração; nada foi substituído.'
    }
    $entry=$matching[0]
    if ($entry.source.source -cne 'local' -or $entry.source.path -cne './plugins/opencode-ecosystem-core' -or
        [IO.Path]::GetFullPath((Join-Path $marketRoot $entry.source.path)) -ne [IO.Path]::GetFullPath($pluginSource)) {
        throw 'A origem do marketplace não corresponde ao Core local; nada foi substituído.'
    }
} else {
    $null=New-Item -ItemType Directory -Path (Split-Path $marketFile) -Force
    @{name='marceloclaro-core-local';interface=@{displayName='MarceloClaro Core local'};plugins=@(@{name='opencode-ecosystem-core';source=@{source='local';path='./plugins/opencode-ecosystem-core'};policy=@{installation='AVAILABLE';authentication='ON_INSTALL'};category='Productivity'})} | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $marketFile -Encoding utf8
}
& $codexExecutable plugin marketplace add $marketRoot --json
if ($LASTEXITCODE -ne 0) { throw 'Falha ao registrar o marketplace local.' }
$installedRaw=& $codexExecutable plugin add opencode-ecosystem-core@marceloclaro-core-local --json
if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar o plugin no aplicativo.' }
$installed=$installedRaw | ConvertFrom-Json -Depth 100
Assert-CorePluginFiles $installed.installedPath $bundle.files
$installedRaw | Set-Content -LiteralPath (Join-Path $wslRoot "$relativeBuild/installation.json") -Encoding utf8
$inventoryRaw=& $codexExecutable plugin list --json
if ($LASTEXITCODE -ne 0) { throw 'O host não confirmou o inventário após a instalação.' }
$inventory=$inventoryRaw | ConvertFrom-Json -Depth 100
$confirmed=@($inventory.installed | Where-Object { $_.pluginId -ceq $installed.pluginId -and $_.version -ceq $bundle.version })
if ($confirmed.Count -ne 1 -or $confirmed[0].installed -ne $true -or $confirmed[0].enabled -ne $true) {
    throw 'O inventário do host não confirmou instalação e habilitação da versão.'
}
@{installed=$confirmed;available=@()} | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath (Join-Path $wslRoot "$relativeBuild/host-inventory.json") -Encoding utf8
@{version=$bundle.version;bundle_sha256=$bundle.sha256;files=$bundle.files;source_path=$pluginSource;installed_path=$installed.installedPath;source_and_cache_match=$true} | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $wslRoot "$relativeBuild/package-verification.json") -Encoding utf8
# A cópia local respeita RemoteSigned sem alterar a política de execução do Windows.
$probe=Join-Path $marketRoot 'probe_chatgpt_plugin.ps1'
Copy-Item -LiteralPath (Join-Path $wslRoot 'scripts/probe_chatgpt_plugin.ps1') -Destination $probe
& $probe -Manifest (Join-Path $installed.installedPath 'mcp.json') -OutputDirectory (Join-Path $wslRoot "$relativeBuild/probe")
Write-Output 'Plugin instalado e transporte verificado. A ativação em uma conversa é uma etapa separada.'
