param([Parameter(Mandatory=$true)][string]$Manifest,[Parameter(Mandatory=$true)][ValidateSet('rea','mirofish','lean4')][string]$Component,[Parameter(Mandatory=$true)][string]$ConfigFile,[Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference='Stop'
$null=New-Item -ItemType Directory -Path $OutputDirectory -Force
$receipt=Join-Path $OutputDirectory 'transport.json'
@{status='not_verified';conversation_tools_verified=$false} | ConvertTo-Json | Set-Content -LiteralPath $receipt -Encoding utf8
$manifestPath=(Resolve-Path -LiteralPath $Manifest).ProviderPath
$manifestHash=(Get-FileHash -LiteralPath $manifestPath).Hash.ToLowerInvariant()
$definition=Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json -Depth 100
$server=$definition.mcpServers."core-$Component"
if ($server.type -ne 'stdio' -or -not $server.command) { throw 'Launcher stdio ausente.' }
$config=Get-Content -LiteralPath $ConfigFile -Raw | ConvertFrom-Json -Depth 100
$process=[Diagnostics.Process]::new()
$process.StartInfo.FileName=$server.command
foreach ($argument in $server.args) { $process.StartInfo.ArgumentList.Add([string]$argument) }
if ($server.cwd) { $process.StartInfo.WorkingDirectory=$server.cwd }
$process.StartInfo.UseShellExecute=$false
$process.StartInfo.CreateNoWindow=$true
$process.StartInfo.RedirectStandardInput=$true
$process.StartInfo.RedirectStandardOutput=$true
$process.StartInfo.RedirectStandardError=$true
$utf8=[Text.UTF8Encoding]::new($false)
$process.StartInfo.StandardInputEncoding=$utf8
$process.StartInfo.StandardOutputEncoding=$utf8
$process.StartInfo.StandardErrorEncoding=$utf8
$started=$false
function Exchange-Component([int]$Id,[string]$Method,[object]$Params) {
    $process.StandardInput.WriteLine((@{jsonrpc='2.0';id=$Id;method=$Method;params=$Params} | ConvertTo-Json -Depth 100 -Compress)); $process.StandardInput.Flush()
    while ($true) {
        $read=$process.StandardOutput.ReadLineAsync()
        if (-not $read.Wait(630000)) { throw 'Prazo MCP excedido.' }
        $line=$read.GetAwaiter().GetResult()
        if ($null -eq $line) { throw 'Servidor encerrou antes da resposta.' }
        $frame=$line | ConvertFrom-Json -Depth 100
        if ($frame.jsonrpc -ne '2.0') { throw 'STDOUT fora do JSON-RPC.' }
        if ($frame.id -eq $Id) { if ($frame.error) { throw ($frame.error | ConvertTo-Json -Compress) }; return $frame.result }
    }
}
function Invoke-ComponentTool([int]$Id,[string]$Name,[object]$Arguments) {
    $response=Exchange-Component $Id 'tools/call' @{name=$Name;arguments=$Arguments}
    if ($response.isError -eq $true) { throw ($response.content | ConvertTo-Json -Compress) }
    return ($response.content[0].text | ConvertFrom-Json -Depth 100)
}
try {
    $started=$process.Start()
    if (-not $started) { throw 'Processo não iniciou.' }
    $stderr=$process.StandardError.ReadToEndAsync()
    $init=Exchange-Component 1 'initialize' @{protocolVersion='2025-11-25';capabilities=@{};clientInfo=@{name='core-components-probe';version='1.0.0'}}
    $process.StandardInput.WriteLine('{"jsonrpc":"2.0","method":"notifications/initialized"}'); $process.StandardInput.Flush()
    $listed=Exchange-Component 2 'tools/list' @{}
    $action=@{rea='rea_action';mirofish='mirofish_run';lean4='lean4_verify'}[$Component]
    if ($listed.tools.Count -ne 2 -or "$($Component)_status" -notin $listed.tools.name -or $action -notin $listed.tools.name) { throw 'Catálogo de ferramentas incorreto.' }
    $status=Invoke-ComponentTool 3 "$($Component)_status" @{}
    $actual=Invoke-ComponentTool 4 $action @{config=$config}
    $negative=$null; $incomplete=$null
    if ($Component -eq 'rea' -and ($actual.status -ne 'completed' -or $actual.success -ne $true)) { throw 'REA não concluiu análise real.' }
    if ($Component -eq 'mirofish' -and ($actual.status -ne 'completed' -or $actual.inference_executed -ne $true -or $actual.runtime_artifact_observed -ne $true)) { throw 'MiroFish não apresentou inferência e artefato externo.' }
    if ($Component -eq 'lean4') {
        if ($actual.is_valid -ne $true -or $actual.status -ne 'machine_checked') { throw 'Lean não comprovou o teorema de teste.' }
        $negative=Invoke-ComponentTool 5 $action @{config=@{operation='verify';code='theorem core_false : (0 : Nat) = 1 := by rfl'}}
        $incomplete=Invoke-ComponentTool 6 $action @{config=@{operation='verify';code='theorem core_incomplete : False := by sorry'}}
        if ($negative.is_valid -ne $false -or $negative.status -ne 'compiler_rejected' -or $incomplete.is_valid -ne $false -or $incomplete.compiler_executed -ne $false) { throw 'Gate Lean aceitou fonte negativa.' }
    }
    if ((Get-FileHash -LiteralPath $manifestPath).Hash.ToLowerInvariant() -ne $manifestHash) { throw 'Manifesto alterado durante a sonda.' }
    $result=@{status='transport_and_operation_verified';component=$Component;manifest_path=$manifestPath;manifest_sha256=$manifestHash;server=$init.serverInfo;tool_names=$listed.tools.name;status_response=$status;operation_response=$actual;negative_response=$negative;incomplete_response=$incomplete;checked_at_utc=[DateTime]::UtcNow.ToString('o');conversation_tools_verified=$false}
    $result | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $receipt -Encoding utf8
} catch {
    @{status='failed';component=$Component;error=$_.Exception.Message;conversation_tools_verified=$false} | ConvertTo-Json | Set-Content -LiteralPath $receipt -Encoding utf8
    throw
} finally {
    if ($started) { $process.StandardInput.Close(); if (-not $process.WaitForExit(5000)) { $process.Kill($true); $process.WaitForExit() }; $stderr.GetAwaiter().GetResult() | Set-Content -LiteralPath (Join-Path $OutputDirectory 'server.stderr.txt') -Encoding utf8 }
    $process.Dispose()
}
Write-Output "${Component}: transporte e operação verificados."
