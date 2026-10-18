param([string]$CoreRoot='/home/marceloclaro/opencode-ecosystem-core',[string]$Distro='Ubuntu')
$ErrorActionPreference='Stop'
if (-not $CoreRoot.StartsWith('/') -or $CoreRoot.Contains("`n") -or $Distro -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$') { throw 'Raiz/distribuição inválida.' }
function Assert-ComponentFiles([string]$Directory,[object]$Expected) {
    $entries=@(Get-Item -LiteralPath $Directory -Force)+@(Get-ChildItem -LiteralPath $Directory -Recurse -Force)
    if (@($entries | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count) { throw 'Redirecionamento inesperado no pacote.' }
    $actual=@($entries | Where-Object { -not $_.PSIsContainer } | ForEach-Object { [IO.Path]::GetRelativePath($Directory,$_.FullName).Replace('\','/') })
    if (@(Compare-Object @($Expected.PSObject.Properties.Name) $actual).Count) { throw 'Inventário de arquivos divergente.' }
    foreach ($file in $Expected.PSObject.Properties) {
        if ((Get-FileHash -LiteralPath (Join-Path $Directory $file.Name)).Hash.ToLowerInvariant() -ne $file.Value) { throw 'Conteúdo divergente; fonte existente preservada.' }
    }
}
$codexExecutable=(Get-Command codex -CommandType Application -ErrorAction Stop).Source
$buildId=[Guid]::NewGuid().ToString('N')
$relativeBuild="outputs/chatgpt-components/$buildId"
$wslRoot='\\wsl.localhost\'+$Distro+'\'+$CoreRoot.TrimStart('/').Replace('/','\')
$marketRoot=Join-Path $env:USERPROFILE '.agents/opencode-core-local'
$marketFile=Join-Path $marketRoot '.agents/plugins/marketplace.json'
$bundles=@()
foreach ($component in @('rea','mirofish','lean4')) {
    $raw=& wsl.exe -d $Distro --cd $CoreRoot --exec "$CoreRoot/.venv/bin/python" -m integrations.component_plugins --target windows-wsl --distro $Distro --component $component --destination "$relativeBuild/$component/plugin" --archive "$relativeBuild/$component/plugin.zip"
    if ($LASTEXITCODE -ne 0) { throw "Falha ao construir $component." }
    $bundle=$raw | ConvertFrom-Json -Depth 100
    $source=Join-Path $wslRoot "$relativeBuild/$component/plugin"
    $target=Join-Path $marketRoot "plugins/$($bundle.name)"
    Assert-ComponentFiles $source $bundle.files
    if (Test-Path -LiteralPath $target) { Assert-ComponentFiles $target $bundle.files }
    $bundles+=@{component=$component;bundle=$bundle;source=$source;target=$target}
}
if (Test-Path -LiteralPath $marketFile) {
    $market=Get-Content -LiteralPath $marketFile -Raw | ConvertFrom-Json -Depth 100
    if ($market.name -cne 'marceloclaro-core-local') { throw 'Marketplace diferente; preservado.' }
} else {
    $market=[pscustomobject]@{name='marceloclaro-core-local';interface=@{displayName='MarceloClaro Core local'};plugins=@()}
}
# Validar tudo antes de copiar fontes ou publicar o catálogo.
foreach ($item in $bundles) {
    $name=$item.bundle.name
    $matching=@($market.plugins | Where-Object { $_.name -ceq $name })
    $expectedPath="./plugins/$name"
    if ($matching.Count -gt 1) { throw 'Entrada duplicada no marketplace; preservado.' }
    if ($matching.Count -eq 1 -and ($matching[0].source.source -cne 'local' -or $matching[0].source.path -cne $expectedPath -or [IO.Path]::GetFullPath((Join-Path $marketRoot $matching[0].source.path)) -ne [IO.Path]::GetFullPath($item.target))) { throw 'Origem divergente no marketplace; preservado.' }
    if ($matching.Count -eq 0) { $market.plugins=@($market.plugins)+@(@{name=$name;source=@{source='local';path=$expectedPath};policy=@{installation='AVAILABLE';authentication='ON_INSTALL'};category='Productivity'}) }
}
foreach ($item in $bundles) {
    if (-not (Test-Path -LiteralPath $item.target)) {
        $null=New-Item -ItemType Directory -Path (Split-Path $item.target) -Force
        Copy-Item -LiteralPath $item.source -Destination $item.target -Recurse
    }
}
$null=New-Item -ItemType Directory -Path (Split-Path $marketFile) -Force
$market | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $marketFile -Encoding utf8
& $codexExecutable plugin marketplace add $marketRoot --json
if ($LASTEXITCODE -ne 0) { throw 'Falha ao registrar marketplace.' }
$installations=@()
foreach ($item in $bundles) {
    $installedRaw=& $codexExecutable plugin add "$($item.bundle.name)@marceloclaro-core-local" --json
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar componente.' }
    $installed=$installedRaw | ConvertFrom-Json -Depth 100
    Assert-ComponentFiles $installed.installedPath $item.bundle.files
    $installations+=@{component=$item.component;installation=$installed;bundle=$item.bundle;source_and_cache_match=$true}
}
$inventoryRaw=& $codexExecutable plugin list --json
if ($LASTEXITCODE -ne 0) { throw 'Falha ao conferir inventário.' }
$inventory=$inventoryRaw | ConvertFrom-Json -Depth 100
$confirmed=@()
foreach ($item in $installations) {
    $found=@($inventory.installed | Where-Object { $_.pluginId -ceq $item.installation.pluginId -and $_.version -ceq $item.bundle.version })
    if ($found.Count -ne 1 -or $found[0].installed -ne $true -or $found[0].enabled -ne $true) { throw 'Instalação/habilitação não confirmada.' }
    $confirmed+=$found[0]
}
@{build_id=$buildId;installations=$installations;host_inventory=$confirmed;conversation_tools_verified=$false} | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath (Join-Path $wslRoot "$relativeBuild/installation.json") -Encoding utf8
Write-Output "Instalações confirmadas; recibo em $relativeBuild/installation.json. Sondas funcionais e ativação da conversa são etapas separadas."
