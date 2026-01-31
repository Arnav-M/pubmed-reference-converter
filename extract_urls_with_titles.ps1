# Extract URLs from RIS files and get their titles
Write-Host "Extracting URLs from RIS files..." -ForegroundColor Green

# Extract URLs from RIS files
$urls = Get-Content *.ris | Select-String -Pattern "^(UR|L1|L2|L3)\s*-\s*(.+)" | ForEach-Object { 
    $_.Matches.Groups[2].Value.Trim() 
} | Sort-Object -Unique

Write-Host "Found $($urls.Count) unique URLs" -ForegroundColor Yellow

# Save URLs to text file
$urls | Out-File -FilePath "extracted_urls.txt" -Encoding UTF8
Write-Host "URLs saved to extracted_urls.txt" -ForegroundColor Green

# Function to get page title from URL
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

# Create results with titles
Write-Host "Fetching titles for each URL..." -ForegroundColor Green
$results = @()

foreach ($url in $urls) {
    Write-Host "Processing: $url" -ForegroundColor Cyan
    $title = Get-PageTitle -url $url
    $results += [PSCustomObject]@{
        URL = $url
        Title = $title
    }
    Start-Sleep -Milliseconds 500  # Be respectful to servers
}

# Save results to CSV and text file
$results | Export-Csv -Path "urls_with_titles.csv" -NoTypeInformation -Encoding UTF8
$results | ForEach-Object { "$($_.URL) - $($_.Title)" } | Out-File -FilePath "urls_with_titles.txt" -Encoding UTF8

Write-Host "Results saved to:" -ForegroundColor Green
Write-Host "  - urls_with_titles.csv (CSV format)" -ForegroundColor White
Write-Host "  - urls_with_titles.txt (Text format)" -ForegroundColor White
Write-Host "  - extracted_urls.txt (URLs only)" -ForegroundColor White

Write-Host "Processing complete!" -ForegroundColor Green 