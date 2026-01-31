# PowerShell script to process .ris files and extract URLs and titles

# Function to process a single RIS file
function Process-RisFile {
    param(
        [string]$FilePath
    )
    
    $entries = @()
    
    try {
        $content = Get-Content -Path $FilePath -Raw -Encoding UTF8
        Write-Host "Processing $($FilePath)..."
        
        # Split content into individual entries (separated by ER -)
        $records = $content -split 'ER\s*-'
        
        foreach ($record in $records) {
            if ([string]::IsNullOrWhiteSpace($record)) {
                continue
            }
            
            $title = ""
            $url = ""
            
            # Look for title (both TI and T1 patterns)
            if ($record -match '(?m)^T[I1]\s*-\s*(.+)$') {
                $title = $matches[1].Trim()
            }
            
            # Look for URL
            if ($record -match '(?m)^UR\s*-\s*(.+)$') {
                $url = $matches[1].Trim()
            }
            
            # Only add entries that have both title and URL
            if ($title -and $url) {
                $entries += [PSCustomObject]@{
                    Title = $title
                    URL = $url
                    SourceFile = Split-Path -Leaf $FilePath
                }
            }
        }
        
        Write-Host "  Found $($entries.Count) entries with both title and URL"
    }
    catch {
        Write-Host "Error reading $($FilePath): $($_.Exception.Message)" -ForegroundColor Red
    }
    
    return $entries
}

# Main script
Write-Host "Starting RIS file processing..." -ForegroundColor Green

# Get all .ris files in the current directory
$risFiles = Get-ChildItem -Filter "*.ris" -File

Write-Host "Found $($risFiles.Count) .ris files:" -ForegroundColor Yellow
foreach ($file in $risFiles) {
    Write-Host "  - $($file.Name)"
}

# Process all RIS files
$allEntries = @()
foreach ($risFile in $risFiles) {
    $entries = Process-RisFile -FilePath $risFile.FullName
    $allEntries += $entries
}

# Save to CSV
$csvFilename = "extracted_ris_data.csv"
$allEntries | Export-Csv -Path $csvFilename -NoTypeInformation -Encoding UTF8

Write-Host "`nProcessing complete!" -ForegroundColor Green
Write-Host "Total entries extracted: $($allEntries.Count)" -ForegroundColor Yellow
Write-Host "Results saved to: $csvFilename" -ForegroundColor Yellow

# Display first few entries as preview
if ($allEntries.Count -gt 0) {
    Write-Host "`nFirst few entries:" -ForegroundColor Cyan
    $allEntries | Select-Object -First 5 | Format-Table -AutoSize
} 