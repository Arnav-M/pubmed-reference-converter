# Extract URLs from RIS files and get their titles
param(
    [string]$CsvOutput = "urls_with_titles.csv",
    [string]$TextOutput = "urls_with_titles.txt",
    [string]$UrlsOutput = "extracted_urls.txt"
)

function Get-PageTitle {
    param($url)
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 10 -UseBasicParsing
        if ($response.Content -match '<title[^>]*>([^<]+)</title>') {
            return $matches[1].Trim()
        }
        return "No title found"
    }
    catch {
        return "Error: $($_.Exception.Message)"
    }
}

function Select-ExportRisFiles {
    param(
        [System.IO.FileInfo[]]$AllFiles
    )

    $selected = [System.Collections.Generic.List[System.IO.FileInfo]]::new()
    $allNames = @($AllFiles | ForEach-Object { $_.Name })

    foreach ($file in $AllFiles) {
        $stem = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)

        if ($stem -match '-with-urls$') {
            [void]$selected.Add($file)
            continue
        }

        $enrichedName = "$stem-with-urls.ris"
        if ($allNames -contains $enrichedName) {
            continue
        }

        [void]$selected.Add($file)
    }

    return ,$selected.ToArray()
}

$canonicalRis = Join-Path (Get-Location) "references.ris"
if (Test-Path $canonicalRis) {
    $risFiles = @(Get-Item -Path $canonicalRis)
}
else {
    $allRisFiles = @(Get-ChildItem -Filter "*.ris" -File -ErrorAction SilentlyContinue)
    $risFiles = Select-ExportRisFiles -AllFiles $allRisFiles
}

if ($risFiles.Count -eq 0) {
    Write-Error "NO_RIS_FILES"
    exit 1
}

$urls = @()
foreach ($risFile in $risFiles) {
    $lines = Get-Content -Path $risFile.FullName -Encoding UTF8 -ErrorAction Stop
    foreach ($line in $lines) {
        if ($line -match '^(UR|L1|L2|L3)\s*-\s*(.+)$') {
            $urls += $matches[2].Trim()
        }
    }
}

$urls = $urls | Sort-Object -Unique

if ($urls.Count -eq 0) {
    Write-Error "NO_URLS"
    exit 2
}

$urls | Out-File -FilePath $UrlsOutput -Encoding UTF8

$results = @()
$index = 0
foreach ($url in $urls) {
    $index++
    $percent = [math]::Round(($index / $urls.Count) * 100)
    Write-Progress -Activity "Fetching web titles" -Status "$index of $($urls.Count)" -PercentComplete $percent
    $title = Get-PageTitle -url $url
    $results += [PSCustomObject]@{
        URL = $url
        Title = $title
    }
    Start-Sleep -Milliseconds 500
}
Write-Progress -Activity "Fetching web titles" -Completed

$results | Export-Csv -Path $CsvOutput -NoTypeInformation -Encoding UTF8
$results | ForEach-Object { "$($_.URL) - $($_.Title)" } | Out-File -FilePath $TextOutput -Encoding UTF8

Write-Output "OK|$($urls.Count)|$CsvOutput|$($risFiles.Count)"
