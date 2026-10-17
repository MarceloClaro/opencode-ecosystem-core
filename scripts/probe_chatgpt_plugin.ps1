param(
    [Parameter(Mandatory=$true)][string]$Manifest,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
$null = New-Item -ItemType Directory -Path $OutputDirectory -Force
$receiptPath = Join-Path $OutputDirectory 'transport.json'
@{status='not_verified';checked_at_utc=[DateTime]::UtcNow.ToString('o');host_conversation_tools_verified=$false} | ConvertTo-Json | Set-Content -LiteralPath $receiptPath -Encoding utf8
$manifestPath=(Resolve-Path -LiteralPath $Manifest).ProviderPath
$manifestHash=(Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
$config = Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json -Depth 100
$server = $config.mcpServers.'ecosystem-core'
if ($server.type -ne 'stdio' -or -not $server.command) { throw 'Manifesto sem launcher stdio do Core.' }
$frames = [System.Collections.Generic.List[object]]::new()
$process = [System.Diagnostics.Process]::new()
$processStarted = $false
$process.StartInfo.FileName = $server.command
foreach ($argument in $server.args) { $process.StartInfo.ArgumentList.Add([string]$argument) }
if ($server.cwd) { $process.StartInfo.WorkingDirectory = $server.cwd }
$process.StartInfo.UseShellExecute = $false
$process.StartInfo.CreateNoWindow = $true
$process.StartInfo.RedirectStandardInput = $true
$process.StartInfo.RedirectStandardOutput = $true
$process.StartInfo.RedirectStandardError = $true
$utf8 = [System.Text.UTF8Encoding]::new($false)
$process.StartInfo.StandardInputEncoding = $utf8
$process.StartInfo.StandardOutputEncoding = $utf8
$process.StartInfo.StandardErrorEncoding = $utf8
$started = Get-Date
function Exchange-Mcp([object]$Request) {
    $process.StandardInput.WriteLine(($Request | ConvertTo-Json -Depth 100 -Compress))
    $process.StandardInput.Flush()
    while ($true) {
        $read = $process.StandardOutput.ReadLineAsync()
        if (-not $read.Wait(30000)) { throw 'Prazo de resposta MCP excedido.' }
        $line = $read.GetAwaiter().GetResult()
        if ($null -eq $line) { throw 'O servidor encerrou antes da resposta.' }
        $frame = $line | ConvertFrom-Json -Depth 100
        if ($frame.jsonrpc -ne '2.0') { throw 'STDOUT contém conteúdo fora de JSON-RPC.' }
        $frames.Add($frame)
        if ($frame.id -eq $Request.id) {
            if ($frame.error) { throw ($frame.error | ConvertTo-Json -Compress) }
            return $frame.result
        }
    }
}
try {
    if (-not $process.Start()) { throw 'O processo não iniciou.' }
    $processStarted = $true
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $initialized = Exchange-Mcp @{jsonrpc='2.0';id=1;method='initialize';params=@{protocolVersion='2025-11-25';capabilities=@{};clientInfo=@{name='core-plugin-windows-probe';version='1.0.0'}}}
    $process.StandardInput.WriteLine('{"jsonrpc":"2.0","method":"notifications/initialized"}')
    $process.StandardInput.Flush()
    $tools = Exchange-Mcp @{jsonrpc='2.0';id=2;method='tools/list';params=@{}}
    if ('ecosystem_integration_status' -notin $tools.tools.name -or 'ecosystem_run' -notin $tools.tools.name) {
        throw 'As ferramentas do Core não foram descobertas.'
    }
    $resource = Exchange-Mcp @{jsonrpc='2.0';id=3;method='resources/read';params=@{uri='ecosystem://books/catalog'}}
    $catalog = $resource.contents[0].text | ConvertFrom-Json -Depth 100
    $search = Exchange-Mcp @{jsonrpc='2.0';id=4;method='tools/call';params=@{name='ecosystem_library_search';arguments=@{query='MCP';top_k=1}}}
    if ($search.isError -eq $true) { throw 'A consulta real da biblioteca falhou.' }
    $retrieved = $search.content[0].text | ConvertFrom-Json -Depth 100
    if ($retrieved.abstained -ne $false -or $retrieved.evidence_count -ne 1 -or $retrieved.evidence[0].page -lt 1) {
        throw 'A consulta não apresentou uma evidência citável da biblioteca.'
    }
    if ((Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $manifestHash) {
        throw 'O manifesto mudou durante a verificação.'
    }
    $result = @{
        status='transport_verified';checked_at_utc=[DateTime]::UtcNow.ToString('o');
        manifest_path=$manifestPath;manifest_sha256=$manifestHash;manifest_unchanged=$true;
        launcher=$server;server_info=$initialized.serverInfo;protocol_version=$initialized.protocolVersion;
        tool_count=$tools.tools.Count;tool_names=@($tools.tools.name | Sort-Object);
        catalog_status=$catalog.status;catalog_book_count=$catalog.books;catalog_offline=$catalog.offline;
        catalog_uri='ecosystem://books/catalog';jsonrpc_frames_valid=$true;
        retrieval_evidence_count=$retrieved.evidence_count;retrieval_page=$retrieved.evidence[0].page;
        retrieval_source_sha256=$retrieved.evidence[0].source_sha256;
        llm_inference_executed=$false;host_conversation_tools_verified=$false;
        elapsed_seconds=[Math]::Round(((Get-Date)-$started).TotalSeconds,2)
    }
    $result | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $receiptPath -Encoding utf8
} catch {
    @{status='transport_failed';error=$_.Exception.Message;checked_at_utc=[DateTime]::UtcNow.ToString('o');host_conversation_tools_verified=$false} | ConvertTo-Json | Set-Content -LiteralPath $receiptPath -Encoding utf8
    throw
} finally {
    if ($processStarted) {
        $process.StandardInput.Close()
        if (-not $process.WaitForExit(5000)) { $process.Kill($true); $process.WaitForExit() }
        if ($stderrTask) { $stderrTask.GetAwaiter().GetResult() | Set-Content -LiteralPath (Join-Path $OutputDirectory 'server.stderr.txt') -Encoding utf8 }
    }
    $process.Dispose()
}
$result | ConvertTo-Json -Depth 100
