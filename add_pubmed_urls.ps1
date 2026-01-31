# PowerShell script to add PubMed URLs to .ris file based on PMIDs

function Add-PubmedUrls {
    param(
        [string]$InputFile,
        [string]$OutputFile
    )
    
    if (-not (Test-Path $InputFile)) {
        Write-Host "Error: Input file '$InputFile' not found!" -ForegroundColor Red
        return
    }
    
    Write-Host "Adding PubMed URLs to $InputFile..." -ForegroundColor Green
    
    try {
        $content = Get-Content -Path $InputFile -Raw -Encoding UTF8
        
        # Split content into individual records (separated by ER -)
        $records = $content -split 'ER\s*-'
        
        $updatedRecords = @()
        $urlsAdded = 0
        
        foreach ($record in $records) {
            if ([string]::IsNullOrWhiteSpace($record)) {
                continue
            }
            
            $updatedRecord = $record
            
            # Look for PMID in the AN field
            if ($record -match '(?m)^AN\s*-\s*(\d+)') {
                $pmid = $matches[1]
                $pubmedUrl = "https://pubmed.ncbi.nlm.nih.gov/$pmid/"
                
                # Add URL field before the ER - line
                $updatedRecord = $record.TrimEnd()
                $updatedRecord += "`r`nUR  - $pubmedUrl`r`n"
                $urlsAdded++
            }
            
            $updatedRecord += "ER  - `r`n`r`n"
            $updatedRecords += $updatedRecord
        }
        
        # Write to output file
        $updatedRecords -join "" | Out-File -FilePath $OutputFile -Encoding UTF8
        
        Write-Host "PubMed URLs added successfully!" -ForegroundColor Green
        Write-Host "Output saved to: $OutputFile" -ForegroundColor Yellow
        Write-Host "Total URLs added: $urlsAdded" -ForegroundColor Yellow
        
    }
    catch {
        Write-Host "Error during processing: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Main execution
$InputFile = "pubmed-labiaplast-set.ris"
$OutputFile = "pubmed-labiaplast-set-with-urls.ris"

Add-PubmedUrls -InputFile $InputFile -OutputFile $OutputFile

Write-Host "`nNow running the RIS processing script to extract titles and URLs..." -ForegroundColor Cyan 