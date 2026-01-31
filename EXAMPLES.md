# Usage Examples

Real-world examples of how to use the PubMed Reference Converter.

## Example 1: Basic Conversion

### Scenario
You downloaded 50 articles from PubMed about diabetes treatment.

### Steps
```powershell
# Convert NBIB to RIS
.\nbib_to_ris_converter.ps1 -InputFile "diabetes-treatment.nbib" -OutputFile "diabetes-treatment.ris"

# Output:
# Converting diabetes-treatment.nbib to diabetes-treatment.ris...
# Conversion completed successfully!
# Total records converted: 50
```

### Result
- Created `diabetes-treatment.ris` with 50 articles in RIS format
- Ready to import into Zotero, Mendeley, or systematic review tools

---

## Example 2: Systematic Review Workflow

### Scenario
Conducting a systematic review on cardiovascular interventions.

### Steps
```powershell
# Step 1: Convert your PubMed search results
.\nbib_to_ris_converter.ps1 -InputFile "cardiac-rct-search.nbib" -OutputFile "cardiac-rcts.ris"

# Step 2: Add PubMed URLs for easy access
# (Edit add_pubmed_urls.ps1 to set InputFile="cardiac-rcts.ris")
.\add_pubmed_urls.ps1

# Step 3: Extract data for tracking
.\process_ris_files.ps1
```

### Result
- `cardiac-rcts.ris` - Ready for Rayyan or Covidence
- `cardiac-rcts-with-urls.ris` - Enriched with PubMed links
- `extracted_ris_data.csv` - Spreadsheet for tracking and documentation

---

## Example 3: Multiple Search Queries

### Scenario
You ran 3 different PubMed searches and want to combine them.

### Steps
```powershell
# Convert each search
.\nbib_to_ris_converter.ps1 -InputFile "search1.nbib" -OutputFile "search1.ris"
.\nbib_to_ris_converter.ps1 -InputFile "search2.nbib" -OutputFile "search2.ris"
.\nbib_to_ris_converter.ps1 -InputFile "search3.nbib" -OutputFile "search3.ris"

# Extract all to one CSV
.\process_ris_files.ps1
```

### Result
- Three separate RIS files (one per search)
- One combined CSV with all articles, tagged by source file

---

## Example 4: Data Analysis in Excel

### Scenario
Want to analyze citation patterns and create a literature table.

### Steps
```powershell
# Convert and extract
.\nbib_to_ris_converter.ps1 -InputFile "literature-review.nbib" -OutputFile "literature-review.ris"
.\process_ris_files.ps1

# Open extracted_ris_data.csv in Excel
```

### Excel Analysis
- Sort by title
- Filter by source file
- Create pivot tables
- Export to Word for literature table

---

## Example 5: Batch Processing

### Scenario
You have 10 different NBIB files to process.

### PowerShell Script
```powershell
# Create a batch processing script
$nbibFiles = Get-ChildItem -Filter "*.nbib"

foreach ($file in $nbibFiles) {
    $outputFile = $file.BaseName + ".ris"
    .\nbib_to_ris_converter.ps1 -InputFile $file.Name -OutputFile $outputFile
    Write-Host "Processed $($file.Name)" -ForegroundColor Green
}

# Then extract all RIS files to CSV
.\process_ris_files.ps1
```

### Result
- All 10 NBIB files converted to RIS
- One master CSV with all citations

---

## Example 6: Citation Management Integration

### For Zotero
```powershell
# Convert to RIS
.\nbib_to_ris_converter.ps1 -InputFile "my-references.nbib" -OutputFile "my-references.ris"

# In Zotero:
# 1. File → Import
# 2. Select my-references.ris
# 3. Choose collection
```

### For Mendeley
```powershell
# Convert to RIS
.\nbib_to_ris_converter.ps1 -InputFile "papers.nbib" -OutputFile "papers.ris"

# In Mendeley:
# 1. File → Import → RIS
# 2. Select papers.ris
```

### For EndNote
```powershell
# Convert to RIS
.\nbib_to_ris_converter.ps1 -InputFile "citations.nbib" -OutputFile "citations.ris"

# In EndNote:
# 1. File → Import → File
# 2. Import Option: Reference Manager (RIS)
# 3. Select citations.ris
```

---

## Example 7: Web Scraping URLs

### Scenario
Extract all URLs from RIS files and fetch their titles.

### Steps
```powershell
# Make sure you have RIS files with URLs
.\extract_urls_with_titles.ps1

# Output files:
# - extracted_urls.txt (list of URLs)
# - urls_with_titles.csv (URLs with fetched titles)
# - urls_with_titles.txt (formatted text)
```

### Use Cases
- Verify article availability
- Check for broken links
- Create reading list with actual titles

---

## Example 8: Custom Field Extraction

### Scenario
Need to extract specific fields beyond title and URL.

### Modify process_ris_files.ps1
```powershell
# Add extraction for authors and year
$entry = [PSCustomObject]@{
    Title = $title
    URL = $url
    Authors = $authors  # Extract from AU field
    Year = $year        # Extract from PY field
    SourceFile = Split-Path -Leaf $FilePath
}
```

---

## Example 9: Quality Control

### Scenario
Verify conversion quality before importing to review software.

### Steps
```powershell
# Convert
.\nbib_to_ris_converter.ps1 -InputFile "test.nbib" -OutputFile "test.ris"

# Check output in text editor
notepad test.ris

# Look for:
# - All TY (type) fields present
# - TI (title) fields not empty
# - ER (end record) markers
# - Proper encoding (no weird characters)
```

---

## Example 10: Troubleshooting

### Empty CSV File

**Problem**: `extracted_ris_data.csv` has no entries

**Solution**:
```powershell
# Check if RIS files have required fields
Get-Content *.ris | Select-String "^TI"  # Check titles
Get-Content *.ris | Select-String "^UR"  # Check URLs

# If missing URLs, add them first
.\add_pubmed_urls.ps1
.\process_ris_files.ps1
```

### Encoding Issues

**Problem**: Special characters appear as ���

**Solution**:
```powershell
# Re-save input file as UTF-8 in notepad
# Or use PowerShell to convert:
Get-Content input.nbib | Out-File -FilePath input-utf8.nbib -Encoding UTF8
```

---

## Tips for Large Datasets

### Processing 1000+ Citations

```powershell
# Split into batches of 100
# Process each batch separately
# Combine CSV files afterward

# Example batch processing:
$records = Get-Content large-file.nbib -Raw
# Split and process in chunks
```

### Memory Management

For very large files:
- Process in smaller batches
- Close other applications
- Use 64-bit PowerShell

---

## Advanced Workflows

### Automated Pipeline

Create a master script:

```powershell
# pipeline.ps1
param([string]$InputNbib)

$risFile = [System.IO.Path]::ChangeExtension($InputNbib, '.ris')
$enrichedFile = $risFile -replace '\.ris$', '-with-urls.ris'

# Step 1: Convert
.\nbib_to_ris_converter.ps1 -InputFile $InputNbib -OutputFile $risFile

# Step 2: Enrich
.\add_pubmed_urls.ps1 -InputFile $risFile -OutputFile $enrichedFile

# Step 3: Extract
.\process_ris_files.ps1

Write-Host "Pipeline complete!" -ForegroundColor Green
```

Usage:
```powershell
.\pipeline.ps1 -InputNbib "my-search.nbib"
```

---

**These examples cover most common use cases. Adapt them to your specific workflow!**
