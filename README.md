# PubMed Reference Converter

A comprehensive PowerShell toolkit for converting PubMed/MEDLINE citation files between formats. Converts NBIB (MEDLINE) files to RIS format, enriches them with PubMed URLs, and extracts structured data to CSV/Excel for easy analysis.

## Overview

This toolkit streamlines the process of working with PubMed citations by providing automated conversion and data extraction tools. Perfect for researchers conducting systematic reviews, literature searches, or citation management.

## Features

- **NBIB to RIS Conversion**: Convert PubMed MEDLINE format (.nbib) to RIS format
- **Automatic URL Enrichment**: Add PubMed URLs based on PMIDs
- **Data Extraction**: Extract titles and URLs from RIS files to CSV
- **Batch Processing**: Process multiple files at once
- **Web Scraping**: Fetch article titles from URLs
- **Clean Output**: Well-formatted CSV files ready for Excel or analysis tools

## Prerequisites

- **Windows PowerShell 5.1+** or **PowerShell 7+**
- **Windows** operating system (scripts use PowerShell-specific features)
- No additional dependencies required - uses built-in PowerShell cmdlets

## Quick Start

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

### 3. Add PubMed URLs (Optional)

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
- DOI (DOI/LID/AID)
- Keywords (MH/SB)

### 2. add_pubmed_urls.ps1

**Purpose**: Add PubMed URLs to RIS files based on PMIDs

**Usage**:
```powershell
# Edit the script to set input/output files
.\add_pubmed_urls.ps1
```

**Output**: RIS file with UR (URL) fields containing PubMed links

### 3. process_ris_files.ps1

**Purpose**: Extract titles and URLs from RIS files to CSV

**Usage**:
```powershell
# Processes all .ris files in current directory
.\process_ris_files.ps1
```

**Output**: 
- `extracted_ris_data.csv` - CSV file with Title, URL, and Source File columns
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

### 5. nbib_to_ris_converter_fixed.ps1

**Purpose**: Alternative/improved version of the NBIB to RIS converter

**Usage**: Same as nbib_to_ris_converter.ps1

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
- **Title**: Article title from the RIS file
- **URL**: PubMed or journal URL
- **SourceFile**: Original RIS file name

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
https://github.com/YOUR_USERNAME/pubmed-converter
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
