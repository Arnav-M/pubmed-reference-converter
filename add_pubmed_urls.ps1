# Add PubMed, DOI, and PMC full-text links to .ris records
param(
    [string]$InputFile,
    [string]$OutputFile
)

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

function Normalize-PmcId {
    param([string]$RawPmc)

    if ([string]::IsNullOrWhiteSpace($RawPmc)) {
        return ""
    }

    if ($RawPmc -match '(PMC\d+)') {
        return $Matches[1]
    }

    if ($RawPmc -match '^\d+$') {
        return "PMC$RawPmc"
    }

    return ""
}

function Get-RisFieldValue {
    param(
        [string]$Record,
        [string]$Tag
    )

    if ($Record -match "(?m)^$([regex]::Escape($Tag))\s*-\s*(.+)$") {
        return $Matches[1].Trim()
    }
    return ""
}

function Test-RecordHasUrl {
    param(
        [string]$Record,
        [string]$Pattern
    )

    $matches = [regex]::Matches($Record, '(?m)^UR\s*-\s*(.+)$')
    foreach ($match in $matches) {
        if ($match.Groups[1].Value -match $Pattern) {
            return $true
        }
    }
    return $false
}

function Add-PubmedUrls {
    param(
        [string]$InputFile,
        [string]$OutputFile
    )

    if (-not (Test-Path $InputFile)) {
        Write-Host "Error: Input file '$InputFile' not found!" -ForegroundColor Red
        exit 1
    }

    Write-Host "Adding links to $InputFile..." -ForegroundColor Green

    try {
        $content = Get-Content -Path $InputFile -Raw -Encoding UTF8
        $records = $content -split 'ER\s*-'

        $updatedRecords = @()
        $pubmedAdded = 0
        $doiAdded = 0
        $pmcAdded = 0

        foreach ($record in $records) {
            if ([string]::IsNullOrWhiteSpace($record)) {
                continue
            }

            $updatedRecord = $record.TrimEnd()
            $pmid = Get-RisFieldValue -Record $record -Tag 'AN'
            $doi = Normalize-Doi -Doi (Get-RisFieldValue -Record $record -Tag 'DO')
            $pmcId = Normalize-PmcId -RawPmc (Get-RisFieldValue -Record $record -Tag 'C2')

            if ($pmid -match '^\d+$' -and -not (Test-RecordHasUrl -Record $record -Pattern 'pubmed\.ncbi\.nlm\.nih\.gov')) {
                $updatedRecord += "`r`nUR  - https://pubmed.ncbi.nlm.nih.gov/$pmid/"
                $pubmedAdded++
            }

            if ($doi -and -not (Test-RecordHasUrl -Record $record -Pattern 'doi\.org')) {
                $updatedRecord += "`r`nUR  - https://doi.org/$doi"
                $doiAdded++
            }

            if ($pmcId -and -not (Test-RecordHasUrl -Record $record -Pattern 'pmc\.ncbi\.nlm\.nih\.gov')) {
                $updatedRecord += "`r`nUR  - https://pmc.ncbi.nlm.nih.gov/articles/$pmcId/"
                $pmcAdded++
            }

            $updatedRecord += "ER  - `r`n`r`n"
            $updatedRecords += $updatedRecord
        }

        $updatedRecords -join "" | Out-File -FilePath $OutputFile -Encoding UTF8

        Write-Host "Links added successfully!" -ForegroundColor Green
        Write-Host "Output saved to: $OutputFile" -ForegroundColor Yellow
        Write-Host "PubMed URLs added: $pubmedAdded" -ForegroundColor Yellow
        Write-Host "DOI URLs added: $doiAdded" -ForegroundColor Yellow
        Write-Host "PMC URLs added: $pmcAdded" -ForegroundColor Yellow
    }
    catch {
        Write-Host "Error during processing: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

if (-not $InputFile) {
    Write-Host "Usage: .\add_pubmed_urls.ps1 -InputFile input.ris -OutputFile output.ris" -ForegroundColor Yellow
    $InputFile = Read-Host "Enter path to .ris file"
    $OutputFile = Read-Host "Enter output .ris file name (press Enter for auto-generated name)"
    if ([string]::IsNullOrWhiteSpace($OutputFile)) {
        $base = [System.IO.Path]::GetFileNameWithoutExtension($InputFile)
        $dir = [System.IO.Path]::GetDirectoryName($InputFile)
        $OutputFile = Join-Path $dir "$base-with-urls.ris"
    }
}

Add-PubmedUrls -InputFile $InputFile -OutputFile $OutputFile
