# Extract full citation data from .ris files into CSV
param(
    [string]$OutputFile = "extracted_ris_data.csv",
    [string]$DuplicatesFile = "duplicates_removed.csv",
    [string]$OptionalColumns = ""
)

$optionalColumnSet = @{}
if ($OptionalColumns) {
    foreach ($name in ($OptionalColumns -split '\|')) {
        $trimmed = $name.Trim()
        if ($trimmed) {
            $optionalColumnSet[$trimmed] = $true
        }
    }
}

function Test-OptionalColumn {
    param([string]$Name)
    return $optionalColumnSet.ContainsKey($Name)
}

function Build-ExportRows {
    param(
        [array]$Entries
    )

    $rows = [System.Collections.Generic.List[object]]::new()

    foreach ($entry in $Entries) {
        $row = [ordered]@{}
        $row.Title = $entry.Title

        if (Test-OptionalColumn 'Include?') {
            $row['Include?'] = ''
        }
        if (Test-OptionalColumn 'ExcludeReason') {
            $row.ExcludeReason = ''
        }
        if (Test-OptionalColumn 'Notes') {
            $row.Notes = ''
        }

        $row.Authors = $entry.Authors
        $row.Year = $entry.Year
        $row.Journal = $entry.Journal
        $row.PMID = $entry.PMID
        $row.DOI = $entry.DOI
        $row.DOIURL = $entry.DOIURL
        $row.PMCID = $entry.PMCID
        $row.PMCURL = $entry.PMCURL
        $row.Abstract = $entry.Abstract

        if (Test-OptionalColumn 'HasAbstract') {
            $row.HasAbstract = if (-not [string]::IsNullOrWhiteSpace($entry.Abstract)) { 'Yes' } else { 'No' }
        }

        if (Test-OptionalColumn 'RecordType') {
            $row.RecordType = $entry.RecordType
        }

        $row.Volume = $entry.Volume
        $row.Issue = $entry.Issue
        $row.Pages = $entry.Pages
        $row.Keywords = $entry.Keywords
        $row.PubMedURL = $entry.PubMedURL
        $row.SourceFile = $entry.SourceFile

        [void]$rows.Add([PSCustomObject]$row)
    }

    return ,$rows.ToArray()
}

function Get-RisFieldValues {
    param(
        [string]$Record,
        [string[]]$Tags
    )

    $values = [System.Collections.Generic.List[string]]::new()
    foreach ($tag in $Tags) {
        $pattern = "(?m)^$([regex]::Escape($tag))\s*-\s*(.+)$"
        $fieldMatches = [regex]::Matches($Record, $pattern)
        foreach ($fieldMatch in $fieldMatches) {
            $value = $fieldMatch.Groups[1].Value.Trim()
            if ($value) {
                [void]$values.Add($value)
            }
        }
    }
    return ,$values.ToArray()
}

function Get-RisUrlByPattern {
    param(
        [string[]]$Urls,
        [string]$Pattern
    )

    foreach ($url in $Urls) {
        if ($url -match $Pattern) {
            return $url
        }
    }
    return ""
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

function Get-RisDoiUrl {
    param(
        [string]$Doi,
        [string[]]$Urls
    )

    $fromUrls = Get-RisUrlByPattern -Urls $Urls -Pattern 'doi\.org'
    if ($fromUrls) {
        return $fromUrls
    }

    $normalized = Normalize-Doi -Doi $Doi
    if ($normalized) {
        return "https://doi.org/$normalized"
    }
    return ""
}

function Get-RisPmcUrl {
    param(
        [string]$PmcId,
        [string[]]$Urls
    )

    $fromUrls = Get-RisUrlByPattern -Urls $Urls -Pattern 'pmc\.ncbi\.nlm\.nih\.gov'
    if ($fromUrls) {
        return $fromUrls
    }

    if ($PmcId) {
        return "https://pmc.ncbi.nlm.nih.gov/articles/$PmcId/"
    }
    return ""
}

function Get-RisYear {
    param([string]$RawYear)

    if ([string]::IsNullOrWhiteSpace($RawYear)) {
        return ""
    }
    if ($RawYear -match '(\d{4})') {
        return $Matches[1]
    }
    return $RawYear.Trim()
}

function Process-RisFile {
    param(
        [string]$FilePath
    )

    $entries = @()

    try {
        $content = Get-Content -Path $FilePath -Raw -Encoding UTF8
        $records = $content -split 'ER\s*-'

        foreach ($record in $records) {
            if ([string]::IsNullOrWhiteSpace($record)) {
                continue
            }

            $titles = Get-RisFieldValues -Record $record -Tags @('TI', 'T1')
            $title = if ($titles.Count -gt 0) { ($titles -join ' ').Trim() } else { "" }

            if (-not $title) {
                continue
            }

            $authors = Get-RisFieldValues -Record $record -Tags @('AU', 'A1')
            $keywords = Get-RisFieldValues -Record $record -Tags @('KW')
            $abstracts = Get-RisFieldValues -Record $record -Tags @('AB', 'N2')
            $journals = Get-RisFieldValues -Record $record -Tags @('JF', 'JO', 'T2')
            $dois = Get-RisFieldValues -Record $record -Tags @('DO', 'M3')
            $pmids = Get-RisFieldValues -Record $record -Tags @('AN')
            $pmcIds = Get-RisFieldValues -Record $record -Tags @('C2')
            $pubTypes = Get-RisFieldValues -Record $record -Tags @('C3')
            $volumes = Get-RisFieldValues -Record $record -Tags @('VL')
            $issues = Get-RisFieldValues -Record $record -Tags @('IS')
            $starts = Get-RisFieldValues -Record $record -Tags @('SP')
            $ends = Get-RisFieldValues -Record $record -Tags @('EP')
            $years = Get-RisFieldValues -Record $record -Tags @('PY', 'Y1')
            $urls = Get-RisFieldValues -Record $record -Tags @('UR', 'L1', 'L2', 'L3')

            $abstract = if ($abstracts.Count -gt 0) { ($abstracts -join ' ').Trim() } else { "" }
            $journal = if ($journals.Length -gt 0) { $journals[0] } else { "" }
            $volume = if ($volumes.Length -gt 0) { $volumes[0] } else { "" }
            $issue = if ($issues.Length -gt 0) { $issues[0] } else { "" }
            $pageStart = if ($starts.Length -gt 0) { $starts[0] } else { "" }
            $pageEnd = if ($ends.Length -gt 0) { $ends[0] } else { "" }
            $pages = if ($pageStart -and $pageEnd) { "$pageStart-$pageEnd" } elseif ($pageStart) { $pageStart } else { "" }
            $recordType = if ($pubTypes.Length -gt 0) { ($pubTypes -join '; ') } else { "" }
            $doi = if ($dois.Length -gt 0) { (Normalize-Doi -Doi $dois[0]) } else { "" }
            $pmid = if ($pmids.Length -gt 0) { $pmids[0] } else { "" }
            $pmcId = if ($pmcIds.Length -gt 0) { (Normalize-PmcId -RawPmc $pmcIds[0]) } else { "" }
            $year = Get-RisYear -RawYear $(if ($years.Length -gt 0) { $years[0] } else { "" })
            $pubmedUrl = Get-RisUrlByPattern -Urls $urls -Pattern 'pubmed\.ncbi\.nlm\.nih\.gov'
            $doiUrl = Get-RisDoiUrl -Doi $doi -Urls $urls
            $pmcUrl = Get-RisPmcUrl -PmcId $pmcId -Urls $urls

            if (-not $pmid -and $pubmedUrl -match 'pubmed\.ncbi\.nlm\.nih\.gov/(\d+)') {
                $pmid = $Matches[1]
            }

            if (-not $pmcId -and $pmcUrl -match '/articles/(PMC\d+)') {
                $pmcId = $Matches[1]
            }

            $entries += [PSCustomObject]@{
                Title = $title
                Authors = ($authors -join '; ')
                Year = $year
                Journal = $journal
                PMID = $pmid
                DOI = $doi
                DOIURL = $doiUrl
                PMCID = $pmcId
                PMCURL = $pmcUrl
                Abstract = $abstract
                RecordType = $recordType
                Volume = $volume
                Issue = $issue
                Pages = $pages
                Keywords = ($keywords -join '; ')
                PubMedURL = $pubmedUrl
                SourceFile = Split-Path -Leaf $FilePath
            }
        }
    }
    catch {
        Write-Error "Error reading $FilePath : $($_.Exception.Message)"
        exit 3
    }

    return $entries
}

function Get-DedupeKey {
    param(
        [pscustomobject]$Entry
    )

    if ($Entry.PMID -match '^\d+$') {
        return "pmid:$($Entry.PMID)"
    }

    if ($Entry.DOI) {
        $doi = Normalize-Doi -Doi $Entry.DOI
        if ($doi) {
            return "doi:$doi"
        }
    }

    return ""
}

function Get-EntryRichness {
    param(
        [pscustomobject]$Entry
    )

    $score = 0
    foreach ($value in @(
        $Entry.Title, $Entry.Authors, $Entry.Year, $Entry.Journal, $Entry.PMID, $Entry.DOI,
        $Entry.DOIURL, $Entry.PMCID, $Entry.PMCURL, $Entry.Abstract, $Entry.RecordType,
        $Entry.Volume, $Entry.Issue, $Entry.Pages, $Entry.Keywords, $Entry.PubMedURL
    )) {
        if (-not [string]::IsNullOrWhiteSpace($value)) {
            $score++
        }
    }
    return $score
}

function Deduplicate-Entries {
    param(
        [array]$Entries
    )

    $seen = @{}
    $unique = [System.Collections.Generic.List[object]]::new()
    $duplicates = [System.Collections.Generic.List[object]]::new()

    foreach ($entry in $Entries) {
        $key = Get-DedupeKey -Entry $entry

        if (-not $key) {
            [void]$unique.Add($entry)
            continue
        }

        if ($seen.ContainsKey($key)) {
            $kept = $seen[$key]
            if ((Get-EntryRichness -Entry $entry) -gt (Get-EntryRichness -Entry $kept)) {
                [void]$duplicates.Add([PSCustomObject]@{
                    Title = $kept.Title
                    PMID = $kept.PMID
                    DOI = $kept.DOI
                    MatchedOn = if ($key.StartsWith('pmid:')) { 'PMID' } else { 'DOI' }
                    KeptSourceFile = $kept.SourceFile
                    RemovedSourceFile = $entry.SourceFile
                })
                $index = $unique.IndexOf($kept)
                if ($index -ge 0) {
                    $unique[$index] = $entry
                }
                $seen[$key] = $entry
            }
            else {
                [void]$duplicates.Add([PSCustomObject]@{
                    Title = $entry.Title
                    PMID = $entry.PMID
                    DOI = $entry.DOI
                    MatchedOn = if ($key.StartsWith('pmid:')) { 'PMID' } else { 'DOI' }
                    KeptSourceFile = $kept.SourceFile
                    RemovedSourceFile = $entry.SourceFile
                })
            }
            continue
        }

        $seen[$key] = $entry
        [void]$unique.Add($entry)
    }

    return @{
        Unique = @($unique.ToArray())
        Duplicates = @($duplicates.ToArray())
        TotalBefore = $Entries.Count
        RemovedCount = $duplicates.Count
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

$allEntries = @()
foreach ($risFile in $risFiles) {
    $entries = Process-RisFile -FilePath $risFile.FullName
    $allEntries += $entries
}

if ($allEntries.Count -eq 0) {
    Write-Error "NO_ENTRIES"
    exit 2
}

$dedupeResult = Deduplicate-Entries -Entries @($allEntries)
$uniqueEntries = @($dedupeResult.Unique)
$removedCount = [int]$dedupeResult.RemovedCount
$totalBefore = [int]$dedupeResult.TotalBefore

if ($uniqueEntries.Count -eq 0) {
    Write-Error "NO_ENTRIES"
    exit 2
}

if ($removedCount -gt 0) {
    @($dedupeResult.Duplicates) | Export-Csv -Path $DuplicatesFile -NoTypeInformation -Encoding UTF8
}

$abstractCount = @($uniqueEntries | Where-Object { -not [string]::IsNullOrWhiteSpace($_.Abstract) }).Count

$exportRows = Build-ExportRows -Entries $uniqueEntries
$exportRows | Export-Csv -Path $OutputFile -NoTypeInformation -Encoding UTF8
Write-Output "OK|$($uniqueEntries.Count)|$OutputFile|$($risFiles.Count)|$abstractCount|$removedCount|$totalBefore|$DuplicatesFile"
