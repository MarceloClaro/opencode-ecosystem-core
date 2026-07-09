# ============================================================
# Script de Verificacao de Referencias - Dissertacao
# Verifica DOIs via CrossRef API e URLs via HTTP HEAD
# ============================================================

$ErrorActionPreference = "Continue"

# --- DOIs para verificar ---
$dois = @(
    @{key="ALMEIDA2024";  doi="10.54033/cadpedv21n9-232"},
    @{key="BARBOSA2013";  doi="10.26849/bts.v39i2.349"},
    @{key="BARRON1998";   doi="10.1080/10508406.1998.9672056"},
    @{key="BARROWS1996";  doi="10.1002/tl.37219966804"},
    @{key="BLACK1998";    doi="10.1080/0969595980050102"},
    @{key="CALLEGARIO2025"; doi="10.28998/lte.2024.n.2.17872"},
    @{key="CANTANHEDE2026"; doi="10.47820/recima21.v7i4.7525"},
    @{key="GOMES2009";    doi="10.1590/S0100-55022009000300014"},
    @{key="GUSMAO2022";   doi="10.5902/1984644464040"},
    @{key="MACHADO2025";  doi="10.51473/rcmos.v2i2.25"},
    @{key="MACIEL2018";   doi="10.17921/2447-8733.2018v19n2p195-201"},
    @{key="MENEZES2020";  doi="10.5935/0034-7140.20200010"},
    @{key="MEZZARI2011";  doi="10.1590/S0100-55022011000100015"},
    @{key="MIRANDA2022";  doi="10.34117/bjdv8n4-353"},
    @{key="RIBEIRO2023";  doi="10.54021/seesv4n1-027"},
    @{key="RIBEIRO2025";  doi="10.58422/repesq.2025.e1751"},
    @{key="RIOS2026";     doi="10.22481/praxisedu.v22i53.17193"},
    @{key="SANTOS2019";   doi="10.18265/1517-03062015v1n44p113-121"},
    @{key="SANTOS2024";   doi="10.17921/2447-8733.2024v25n1p51-59"},
    @{key="SCHMIDT1983";  doi="10.1111/j.1365-2923.1983.tb01086.x"},
    @{key="SILVA2023";    doi="10.5585/45.2023.24026"},
    @{key="SOARES2013";   doi="10.1590/S0101-73302013000300013"},
    @{key="SOARES2021";   doi="10.4025/actascieduc.v44i1.52168"},
    @{key="SOUSA2025";    doi="10.36560/18320252057"},
    @{key="TEODORO2024";  doi="10.14244/reveduc.v18i1.5376"},
    @{key="DAHAL2026";    doi="10.3389/frma.2025.1669578"},
    @{key="PAULUS2023";   doi="10.1177/15344843221138381"},
    @{key="KABIR2025";    doi="10.1177/16094069251336810"}
)

# --- URLs sem DOI para verificar ---
$urls = @(
    @{key="AUSUBEL2000";  url="https://www.worldcat.org/title/aquisicao-e-retencao-de-conhecimentos-uma-perspectiva-cognitiva/oclc/48731696"},
    @{key="BACICH2018";   url="https://www.amazon.com.br/Metodologias-Ativas-aprendizagem-profundamente/dp/8584291156"},
    @{key="BARDIN2016";   url="https://search.worldcat.org/pt/title/319215399"},
    @{key="BONWELL1991";  url="https://eric.ed.gov/?id=ED336049"},
    @{key="BRASIL2018";   url="https://www.gov.br/mec/pt-br/escola-em-tempo-integral/arquivos/BNCC_EI_EF_110518_versaofinal.pdf"},
    @{key="COSTA2020";    url="https://www.editoracontentus.com.br/"},
    @{key="CRESWELL2018"; url="https://www.worldcat.org/title/projeto-de-pesquisa-metodos-qualitativo-quantitativo-e-misto/oclc/1085179213"},
    @{key="FREITAS2024";  url="https://periodicos.ideau.com.br/index.php/rei/article/view/170"},
    @{key="LIBANEO2006";  url="https://www.worldcat.org/title/didatica/oclc/48964035"},
    @{key="MORAN2018";    url="https://www.amazon.com.br/Metodologias-Ativas-uma-Educacao-Inovadora/dp/8584291156"},
    @{key="MUNHOZ2015";   url="https://www.worldcat.org/title/abp-aprendizagem-baseada-em-problemas-ferramenta-de-apoio-ao-docente-no-processo-de-ensino-e-aprendizagem/oclc/923552901"},
    @{key="OECD2019";     url="https://www.oecd.org/pisa/"},
    @{key="OLIVEIRA2023"; url="https://educacaopublica.cecierj.edu.br/artigos/23/8/o-uso-das-metodologias-ativas-de-aprendizagem-na-formacao-do-professor-das-universidades-para-a-pratica-nas-escolas"},
    @{key="PAIVA2016";    url="https://sanare.emnuvens.com.br/sanare/article/view/1049"},
    @{key="PORTER1980";   url="https://search.worldcat.org/title/610796358"},
    @{key="SELWYN2022";   url="https://www.bloomsbury.com/uk/education-and-technology-9781350139183/"},
    @{key="THOMAS2000";   url="https://www.pblworks.org/sites/default/files/2019-01/A_Review_of_Research_on_Project_Based_Learning.pdf"},
    @{key="VALENTE2018";  url="https://www.amazon.com.br/Metodologias-Ativas-Educacao-Inovadora/dp/8584291156"},
    @{key="VEIGA2014";    url="https://www.worldcat.org/title/educacao-basica-no-brasil-conceitos-e-praticas/oclc/883601054"}
)

$results = @()

Write-Host ""
Write-Host "========================================"
Write-Host "  VERIFICACAO DE REFERENCIAS BIBLIOGRAFICAS"
Write-Host "========================================"
Write-Host ""

# --- Verificar DOIs via CrossRef ---
Write-Host "--- FASE 1: Verificando DOIs via CrossRef API ---"
Write-Host ""

foreach ($item in $dois) {
    $key = $item.key
    $doi = $item.doi
    $crossrefUrl = "https://api.crossref.org/works/$doi"
    
    try {
        $response = Invoke-RestMethod -Uri $crossrefUrl -Method Get -TimeoutSec 15 -ErrorAction Stop
        $status = "OK"
        $title = ""
        if ($response.message.title) {
            $title = $response.message.title[0]
            if ($title.Length -gt 60) { $title = $title.Substring(0, 60) + "..." }
        }
        Write-Host "  [OK]   $key -- $doi" -ForegroundColor Green
        if ($title) { Write-Host "         Title: $title" -ForegroundColor DarkGray }
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq 404) {
            $status = "404-NOT_FOUND"
            Write-Host "  [FAIL] $key -- $doi (404: DOI not found in CrossRef)" -ForegroundColor Red
        }
        elseif ($statusCode -eq 429) {
            $status = "429-RATE_LIMIT"
            Write-Host "  [WARN] $key -- $doi (429: Rate limit, waiting 2s...)" -ForegroundColor Yellow
            Start-Sleep -Seconds 2
            try {
                $response = Invoke-RestMethod -Uri $crossrefUrl -Method Get -TimeoutSec 15 -ErrorAction Stop
                $status = "OK"
                Write-Host "         Retry OK" -ForegroundColor Green
            }
            catch {
                $status = "429-FAIL"
                Write-Host "         Retry FAIL" -ForegroundColor Red
            }
        }
        else {
            $status = "ERROR: $statusCode"
            Write-Host "  [FAIL] $key -- $doi (HTTP $statusCode)" -ForegroundColor Red
        }
    }
    
    $results += [PSCustomObject]@{
        Key     = $key
        Type    = "DOI"
        Value   = $doi
        Status  = $status
    }
    
    Start-Sleep -Milliseconds 800
}

# --- Verificar URLs sem DOI ---
Write-Host ""
Write-Host "--- FASE 2: Verificando URLs (HTTP HEAD) ---"
Write-Host ""

foreach ($item in $urls) {
    $key = $item.key
    $url = $item.url
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method Head -TimeoutSec 15 -MaximumRedirection 5 -ErrorAction Stop
        $statusCode = $response.StatusCode
        $status = "OK ($statusCode)"
        Write-Host "  [OK]   $key -- HTTP $statusCode" -ForegroundColor Green
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq 403) {
            $status = "403-BLOCKED"
            Write-Host "  [WARN] $key -- HTTP 403 (blocked by WAF, URL may be active)" -ForegroundColor Yellow
        }
        elseif ($statusCode -eq 404) {
            $status = "404-NOT_FOUND"
            Write-Host "  [FAIL] $key -- HTTP 404 (URL not found)" -ForegroundColor Red
        }
        elseif ($statusCode -eq 406) {
            try {
                $response = Invoke-WebRequest -Uri $url -Method Get -TimeoutSec 15 -MaximumRedirection 5 -ErrorAction Stop
                $status = "OK (GET fallback, $($response.StatusCode))"
                Write-Host "  [OK]   $key -- GET fallback OK ($($response.StatusCode))" -ForegroundColor Green
            }
            catch {
                $status = "FAIL (GET fallback error)"
                Write-Host "  [FAIL] $key -- GET fallback error" -ForegroundColor Red
            }
        }
        else {
            $status = "ERROR: HTTP $statusCode"
            Write-Host "  [FAIL] $key -- HTTP $statusCode" -ForegroundColor Red
        }
    }
    
    $results += [PSCustomObject]@{
        Key     = $key
        Type    = "URL"
        Value   = $url
        Status  = $status
    }
    
    Start-Sleep -Milliseconds 500
}

# --- Resumo ---
Write-Host ""
Write-Host "========================================"
Write-Host "  RESUMO DA VERIFICACAO"
Write-Host "========================================"
Write-Host ""

$okCount = ($results | Where-Object { $_.Status -like "OK*" }).Count
$failCount = ($results | Where-Object { $_.Status -like "FAIL*" -or $_.Status -like "404*" }).Count
$warnCount = ($results | Where-Object { $_.Status -like "WARN*" -or $_.Status -like "403*" -or $_.Status -like "429*" }).Count

Write-Host "  Total verificadas: $($results.Count)"
Write-Host "  OK (ativas):       $okCount" -ForegroundColor Green
Write-Host "  WARN (bloqueadas): $warnCount" -ForegroundColor Yellow
Write-Host "  FAIL (inativas):   $failCount" -ForegroundColor Red

if ($failCount -gt 0) {
    Write-Host ""
    Write-Host "--- REFERENCIAS COM PROBLEMAS ---" -ForegroundColor Red
    $results | Where-Object { $_.Status -like "FAIL*" -or $_.Status -like "404*" } | ForEach-Object {
        Write-Host "  $($_.Key) [$($_.Type)] -- $($_.Value)" -ForegroundColor Red
        Write-Host "    Status: $($_.Status)" -ForegroundColor DarkRed
    }
}

if ($warnCount -gt 0) {
    Write-Host ""
    Write-Host "--- REFERENCIAS COM ALERTA ---" -ForegroundColor Yellow
    $results | Where-Object { $_.Status -like "WARN*" -or $_.Status -like "403*" -or $_.Status -like "429*" } | ForEach-Object {
        Write-Host "  $($_.Key) [$($_.Type)] -- Status: $($_.Status)" -ForegroundColor Yellow
    }
}

# Exportar para CSV
$results | Export-Csv -Path "C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex\reference_check_results.csv" -NoTypeInformation -Encoding UTF8
Write-Host ""
Write-Host "Resultados exportados para reference_check_results.csv" -ForegroundColor DarkGray
