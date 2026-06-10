# Merge multiple .ris files into one deduplicated references.ris
param(
    [string]$InputFiles = "",
    [string]$OutputFile = "references.ris"
)

$InputFile = @()
if ($InputFiles) {
    $InputFile = @($InputFiles -split '\|')
}

function Normalize-Doi {
    param([string]$Doi)

    if ([string]::IsNullOrWhiteSpace($Doi)) {
        return ""
    }

    $value = $Doi.Trim()
    $value = $value -replace '^https?://(dx\.)?doi\.org/', ''
    $value = $value -replace '^doi:\s*', ''
    return $value.Trim()
}

function Get-RisRecordKey {
    param([string]$Record)

    if ($Record -match '(?m)^AN\s*-\s*(\d+)') {
        return "pmid:$($Matches[1])"
    }

    if ($Record -match '(?m)^DO\s*-\s*(.+)$') {
        $doi = Normalize-Doi -Doi $Matches[1].Trim()
        if ($doi) {
            return "doi:$doi"
        }
    }

    return ""
}

function Get-RisRecordRichness {
    param([string]$Record)

    $score = 0
    $lines = $Record -split '\r?\n'
    foreach ($line in $lines) {
        if ($line -match '^\w+\s*-\s*\S') {
            $score++
        }
    }
    return $score
}

function Split-RisRecords {
    param([string]$Content)

    $records = [System.Collections.Generic.List[string]]::new()
    foreach ($chunk in ($Content -split 'ER\s*-')) {
        $record = $chunk.Trim()
        if ($record) {
            [void]$records.Add($record)
        }
    }
    return ,$records.ToArray()
}

if (-not $InputFile -or $InputFile.Count -eq 0) {
    Write-Error "NO_INPUT_FILES"
    exit 1
}

$missing = @($InputFile | Where-Object { -not (Test-Path $_) })
if ($missing.Count -gt 0) {
    Write-Error "Missing input file(s): $($missing -join ', ')"
    exit 2
}

$seen = @{}
$unique = [System.Collections.Generic.List[string]]::new()
$removedCount = 0
$totalBefore = 0

foreach ($path in $InputFile) {
    $content = Get-Content -Path $path -Raw -Encoding UTF8
    foreach ($record in (Split-RisRecords -Content $content)) {
        $totalBefore++
        $key = Get-RisRecordKey -Record $record

        if (-not $key) {
            [void]$unique.Add($record)
            continue
        }

        if ($seen.ContainsKey($key)) {
            $removedCount++
            if ((Get-RisRecordRichness -Record $record) -gt (Get-RisRecordRichness -Record $seen[$key])) {
                $index = $unique.IndexOf($seen[$key])
                if ($index -ge 0) {
                    $unique[$index] = $record
                }
                $seen[$key] = $record
            }
            continue
        }

        $seen[$key] = $record
        [void]$unique.Add($record)
    }
}

if ($unique.Count -eq 0) {
    Write-Error "NO_ENTRIES"
    exit 3
}

$output = ($unique | ForEach-Object { "$($_)`r`nER  - `r`n" }) -join "`r`n"
$output | Out-File -FilePath $OutputFile -Encoding UTF8 -NoNewline

Write-Output "OK|$($unique.Count)|$OutputFile|$($InputFile.Count)|$removedCount|$totalBefore"
