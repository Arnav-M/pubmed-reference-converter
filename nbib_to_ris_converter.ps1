# PowerShell script to convert .nbib (MEDLINE) files to .ris format

function Convert-NbibToRis {
    param(
        [string]$InputFile,
        [string]$OutputFile
    )
    
    if (-not (Test-Path $InputFile)) {
        Write-Host "Error: Input file '$InputFile' not found!" -ForegroundColor Red
        return
    }
    
    Write-Host "Converting $InputFile to $OutputFile..." -ForegroundColor Green
    
    try {
        $content = Get-Content -Path $InputFile -Raw -Encoding UTF8
        
        # Split content into individual records (separated by blank lines)
        $records = $content -split '\r?\n\r?\n'
        
        $risEntries = @()
        
        foreach ($record in $records) {
            if ([string]::IsNullOrWhiteSpace($record)) {
                continue
            }
            
            $risEntry = "TY  - JOUR`r`n"  # Default to journal article
            
            # Split record into lines
            $lines = $record -split '\r?\n'
            
            foreach ($line in $lines) {
                if ([string]::IsNullOrWhiteSpace($line)) {
                    continue
                }
                
                # Parse MEDLINE format tags
                if ($line -match '^([A-Z]{2,4})\s*-\s*(.+)$') {
                    $tag = $matches[1]
                    $value = $matches[2]
                    
                    switch ($tag) {
                        'TI' { $risEntry += "TI  - $value`r`n" }
                        'AB' { $risEntry += "AB  - $value`r`n" }
                        'AU' { $risEntry += "AU  - $value`r`n" }
                        'FAU' { $risEntry += "AU  - $value`r`n" }
                        'TA' { $risEntry += "JF  - $value`r`n" }
                        'JT' { $risEntry += "JF  - $value`r`n" }
                        'VI' { $risEntry += "VL  - $value`r`n" }
                        'IP' { $risEntry += "IS  - $value`r`n" }
                        'PG' { 
                            if ($value -match '(\d+)-(\d+)') {
                                $risEntry += "SP  - $($matches[1])`r`n"
                                $risEntry += "EP  - $($matches[2])`r`n"
                            }
                        }
                        'DP' { $risEntry += "PY  - $value`r`n" }
                        'PMID' { $risEntry += "AN  - $value`r`n" }
                        'DOI' { $risEntry += "DO  - $value`r`n" }
                        'SO' { $risEntry += "JF  - $value`r`n" }
                        'SB' { $risEntry += "KW  - $value`r`n" }
                        'MH' { $risEntry += "KW  - $value`r`n" }
                        'EDAT' { $risEntry += "Y2  - $value`r`n" }
                        'LID' { 
                            if ($value -match 'doi') {
                                $risEntry += "DO  - $($value -replace '\s*\[doi\]', '')`r`n"
                            }
                        }
                        'AID' { 
                            if ($value -match 'doi') {
                                $risEntry += "DO  - $($value -replace '\s*\[doi\]', '')`r`n"
                            }
                        }
                    }
                }
            }
            
            $risEntry += "ER  - `r`n`r`n"
            $risEntries += $risEntry
        }
        
        # Write to output file
        $risEntries -join "" | Out-File -FilePath $OutputFile -Encoding UTF8
        
        Write-Host "Conversion completed successfully!" -ForegroundColor Green
        Write-Host "Output saved to: $OutputFile" -ForegroundColor Yellow
        Write-Host "Total records converted: $($risEntries.Count)" -ForegroundColor Yellow
        
    }
    catch {
        Write-Host "Error during conversion: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Main script
param(
    [string]$InputFile,
    [string]$OutputFile
)

if (-not $InputFile) {
    Write-Host "Usage: .\nbib_to_ris_converter.ps1 -InputFile input.nbib -OutputFile output.ris" -ForegroundColor Yellow
    Write-Host "Or interactively:" -ForegroundColor Yellow
    
    # Interactive mode
    $InputFile = Read-Host "Enter path to .nbib file"
    $OutputFile = Read-Host "Enter output .ris file name (press Enter for auto-generated name)"
    
    if ([string]::IsNullOrWhiteSpace($OutputFile)) {
        $OutputFile = [System.IO.Path]::ChangeExtension($InputFile, '.ris')
    }
}

Convert-NbibToRis -InputFile $InputFile -OutputFile $OutputFile 