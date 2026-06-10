# PubMed Reference Converter

A comprehensive PowerShell toolkit for converting PubMed/MEDLINE citation files between formats. Converts NBIB (MEDLINE) files to RIS format, enriches them with PubMed URLs, and extracts structured data to CSV/Excel for easy analysis.

## Overview

This toolkit streamlines the process of working with PubMed citations by providing automated conversion and data extraction tools. Perfect for researchers conducting systematic reviews, literature searches, or citation management.

## Features

- **NBIB to RIS Conversion**: Convert PubMed MEDLINE format (.nbib) to RIS format
- **Automatic Link Enrichment**: Add PubMed, DOI, and PMC full-text URLs to RIS records
- **Full CSV Export**: Extract title, authors, year, journal, PMID, DOI, DOI URL, PMC ID, PMC URL, abstract, keywords, and PubMed URL from RIS files
- **Automatic deduplication**: CSV export merges records across files and removes duplicates by PMID, then DOI
- **Batch Processing**: Process multiple files at once
- **Web Scraping**: Fetch article titles from URLs
- **Excel export**: Auto-sized `.xlsx` with frozen headers and filters
- **PRISMA summary**: `prisma_summary.txt` with identification counts after export
- **Optional columns**: Screening fields, publication types, Vancouver/AMA citations (Properties tab)
- **Single merged output**: One deduplicated `references.ris` per project (no per-file `-with-urls` clutter)

## Prerequisites

- **Windows PowerShell 5.1+** or **PowerShell 7+**
- **Windows** operating system (scripts use PowerShell-specific features)
- No additional dependencies required - uses built-in PowerShell cmdlets

## GUI

### Install (end users)

Download **`PubMed-Reference-Converter-Setup.exe`** from [GitHub Releases](https://github.com/Arnav-M/pubmed-reference-converter/releases) and run the wizard. No Python or PowerShell required.

### Build the installer (maintainers)

Double-click **`build_installer.bat`**. One-time prerequisites:

1. [Python 3.10+](https://python.org)
2. [Inno Setup 6](https://jrsoftware.org/isdl.php) (free)

Output: `installer\output\PubMed-Reference-Converter-Setup.exe` — upload to GitHub Releases.

### Dev mode

`python gui.py` or `launch_gui.bat`. For dev, run `pip install -r requirements-gui.txt` once (drag-and-drop + Excel export).

The desktop app walks through:

1. **NBIB → RIS** — pick input/output files
2. **Add links** — enrich RIS with PubMed, DOI, and PMC links
3. **Full CSV** — extract full citation data (+ Excel + PRISMA summary)
4. **Web titles** — optional, fetches page titles from URLs (slow for large sets)
5. **Properties** — optional CSV columns (screening, record type, citations)

Use **Run batch pipeline** to do steps 1–3 in one click. Outputs a single deduplicated `references.ris` in your working folder (no per-file `-with-urls` copies).

Requires **Python 3.10+** (tkinter is built in). PowerShell scripts run in the background.

## Quick Start (CLI)

### 1. Download Your PubMed Citations

1. Go to [PubMed](https://pubmed.ncbi.nlm.nih.gov/)
2. Perform your search
3. Select citations
4. Click "Save" and choose format: **MEDLINE**
5. Save the `.nbib` file

### 2. Convert NBIB to RIS

```powershell
.\nbib_to_ris_converter.ps1 -InputFile "pubmed-results.nbib" -OutputFile "pubmed-results.ris"
```

Or run interactively:

```powershell
.\nbib_to_ris_converter.ps1
```

### 3. Add links (Optional)

```powershell
.\add_pubmed_urls.ps1 -InputFile "pubmed-results.ris" -OutputFile "pubmed-results-with-urls.ris"
```

### 4. Extract to CSV

```powershell
.\process_ris_files.ps1
```

This will create `extracted_ris_data.csv` with titles and URLs.

## Scripts Overview

### 1. nbib_to_ris_converter.ps1

**Purpose**: Convert PubMed MEDLINE format (.nbib) to RIS format

**Usage**:
```powershell
# Command line
.\nbib_to_ris_converter.ps1 -InputFile input.nbib -OutputFile output.ris

# Interactive mode
.\nbib_to_ris_converter.ps1
```

**Supported Fields**:
- Title (TI)
- Abstract (AB)
- Authors (AU/FAU)
- Journal (TA/JT/SO)
- Volume (VI)
- Issue (IP)
- Pages (PG)
- Publication Year (DP)
- PMID (PMID)
- PMC ID (PMC/AID [pmc])
- DOI (DOI/LID/AID)
- Keywords (MH/SB)

### 2. add_pubmed_urls.ps1

**Purpose**: Add PubMed, DOI (`https://doi.org/...`), and PMC full-text links to RIS files

**Usage**:
```powershell
# Edit the script to set input/output files
.\add_pubmed_urls.ps1
```

**Output**: RIS file with UR (URL) fields for PubMed, DOI, and PMC when available

### 3. process_ris_files.ps1

**Purpose**: Extract full citation data from RIS files to CSV

**Usage**:
```powershell
# Processes all .ris files in current directory
.\process_ris_files.ps1
```

**Output**: 
- `extracted_ris_data.csv` - deduplicated CSV with Title, Authors, Year, Journal, PMID, DOI, DOIURL, PMCID, PMCURL, Abstract, Keywords, PubMedURL, and SourceFile
- `extracted_ris_data.xlsx` - same data in Excel with auto-sized columns, frozen header row, and filters
- `duplicates_removed.csv` - audit log when duplicates are removed (matched by PMID or DOI)
- Console summary with entry counts

### 4. extract_urls_with_titles.ps1

**Purpose**: Extract URLs from RIS files and fetch their webpage titles

**Usage**:
```powershell
.\extract_urls_with_titles.ps1
```

**Output**:
- `extracted_urls.txt` - List of unique URLs
- `urls_with_titles.csv` - CSV with URLs and fetched titles
- `urls_with_titles.txt` - Text file with URLs and titles

**Note**: This script makes web requests, so it may take time for large datasets.

## Complete Workflow Example

### Example: Converting PubMed Search Results

```powershell
# Step 1: Convert NBIB to RIS
.\nbib_to_ris_converter.ps1 -InputFile "heart-disease-search.nbib" -OutputFile "heart-disease.ris"

# Step 2: Add PubMed URLs
.\add_pubmed_urls.ps1 -InputFile "heart-disease.ris" -OutputFile "heart-disease-with-urls.ris"

# Step 3: Extract to CSV for analysis
.\process_ris_files.ps1

# Output: extracted_ris_data.csv ready to open in Excel
```

## File Formats

### NBIB (MEDLINE) Format
```
PMID- 12345678
TI  - Article Title Here
AB  - Abstract text here
AU  - Smith J
AU  - Johnson M
TA  - Journal Name
```

### RIS Format
```
TY  - JOUR
TI  - Article Title Here
AB  - Abstract text here
AU  - Smith J
AU  - Johnson M
JF  - Journal Name
AN  - 12345678
UR  - https://pubmed.ncbi.nlm.nih.gov/12345678/
ER  -
```

## Use Cases

### Systematic Reviews
1. Download all search results from PubMed as NBIB
2. Convert to RIS for use in Rayyan, Covidence, or other review tools
3. Extract titles and URLs for tracking and documentation

### Citation Management
1. Export PubMed citations in MEDLINE format
2. Convert to RIS for import into Zotero, Mendeley, or EndNote
3. Enrich with PubMed URLs for easy access

### Data Analysis
1. Extract citation data to CSV
2. Analyze in Excel, R, or Python
3. Create literature maps or citation networks

### Research Workflows
1. Batch convert multiple search results
2. Merge citations from different sources
3. Extract structured data for reporting

## Troubleshooting

### "Execution of scripts is disabled on this system"

PowerShell execution policy may block scripts. Run this command:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Input file not found"

- Check the file path is correct
- Use absolute paths if relative paths don't work
- Ensure the file extension matches (.nbib or .ris)

### Encoding Issues

All scripts use UTF-8 encoding. If you see strange characters:
- Save your input files as UTF-8
- Check your PowerShell console encoding

### No Data Extracted

- Verify the RIS file has both TI (title) and UR (URL) fields
- Check that the file format is correct
- Look at console output for processing messages

## Output Files

### CSV Columns
- **Title**: Article title
- **Authors**: Semicolon-separated author list
- **Year**: Publication year (from PY)
- **Journal**: Journal name (JF)
- **PMID**: PubMed ID (AN)
- **DOI**: Digital object identifier
- **DOIURL**: Clickable DOI link (`https://doi.org/...`)
- **PMCID**: PubMed Central ID when available
- **PMCURL**: Free full-text link on PMC when available
- **Abstract**: Article abstract
- **Volume** / **Issue** / **Pages**: Bibliographic details when present
- **Keywords**: Semicolon-separated keywords (KW)
- **PubMedURL**: PubMed link when present (UR)
- **SourceFile**: Original RIS file name

### Also generated automatically
- **`extracted_ris_data.xlsx`** — same data with formatted column widths
- **`prisma_summary.txt`** — records identified, duplicates removed, unique for screening
- **`duplicates_removed.csv`** — audit log when duplicates are dropped

### Optional columns (Properties tab)
- **Include?**: Empty screening column (Y / N / Maybe)
- **ExcludeReason**: Why a record was excluded
- **Notes**: Reviewer notes
- **HasAbstract**: Yes/No for quick filtering
- **RecordType**: PubMed publication types (Journal Article, RCT, etc.)
- **CitationVancouver** / **CitationAMA**: Ready-to-paste reference strings

## Tips & Best Practices

1. **Backup Original Files**: Always keep your original NBIB files
2. **Batch Processing**: Put all RIS files in one folder for batch extraction
3. **File Naming**: Use descriptive names for tracking multiple searches
4. **Verify Output**: Check the first few entries in CSV files before analysis
5. **Large Datasets**: Process in smaller batches if you have thousands of citations

## Advanced Usage

### Modify Field Mappings

Edit the conversion scripts to customize field mappings:

```powershell
# In nbib_to_ris_converter.ps1, add new field mapping:
'NEW_TAG' { $risEntry += "RIS_TAG  - $value`r`n" }
```

### Custom URL Formats

Edit `add_pubmed_urls.ps1` to use different URL formats:

```powershell
$customUrl = "https://doi.org/$doi"  # For DOI-based URLs
```

### Filter Specific Record Types

Modify `process_ris_files.ps1` to filter by record type or other criteria.

## Limitations

- **PowerShell Only**: Scripts require Windows PowerShell (not compatible with Bash/Linux without modifications)
- **Format-Specific**: Designed for PubMed/MEDLINE and RIS formats
- **Web Scraping**: The `extract_urls_with_titles.ps1` script may be slow for large datasets
- **No Validation**: Scripts assume input files are properly formatted

## Contributing

Contributions are welcome! Areas for improvement:
- Add support for other citation formats (BibTeX, EndNote XML)
- Cross-platform compatibility (PowerShell Core)
- GUI interface for easier use
- Validation and error recovery
- Additional field mappings

## License

MIT License - Free for academic and commercial use

## Citation

If you use these tools in your research, please acknowledge:
```
PubMed Reference Converter - PowerShell toolkit for citation format conversion
https://github.com/Arnav-M/pubmed-reference-converter
```

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Verify your input file format matches MEDLINE/NBIB or RIS specifications
3. Open an issue on GitHub with example files (without sensitive data)

## Related Tools

- [Rayyan](https://www.rayyan.ai/) - Systematic review screening tool
- [Zotero](https://www.zotero.org/) - Citation management software
- [PubMed](https://pubmed.ncbi.nlm.nih.gov/) - Biomedical literature database

---

**Simplify your literature search workflow with automated citation conversion**
