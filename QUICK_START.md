# Quick Start Guide

Get up and running in 2 minutes!

## Step 1: Download PubMed Citations

1. Go to [PubMed](https://pubmed.ncbi.nlm.nih.gov/)
2. Search for articles (e.g., "heart disease treatment")
3. Select the citations you want
4. Click **Save** button
5. Choose format: **MEDLINE**
6. Save the file (it will have `.nbib` extension)

## Step 2: Place Files in the Same Folder

Put your downloaded `.nbib` file in the same folder as these scripts.

## Step 3: Convert to RIS Format

Open PowerShell in this folder and run:

```powershell
.\nbib_to_ris_converter.ps1
```

When prompted:
- Enter the path to your `.nbib` file
- Enter desired output filename (or press Enter for auto-naming)

## Step 4: Extract Data to CSV

```powershell
.\process_ris_files.ps1
```

This creates `extracted_ris_data.csv` - open it in Excel!

## That's It!

You now have a CSV file with:
- Article titles
- PubMed URLs
- Source information

Ready for analysis, systematic review, or import into other tools.

## Optional: Add PubMed URLs

Want to enrich your RIS file with direct PubMed links?

Edit `add_pubmed_urls.ps1` to set your input/output files, then run:

```powershell
.\add_pubmed_urls.ps1
```

## Need Help?

- **Execution Policy Error**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **File Not Found**: Make sure the `.nbib` file is in the correct location
- **No Data Extracted**: Check that the RIS file has title and URL fields

## Common Workflows

### For Systematic Reviews
```powershell
.\nbib_to_ris_converter.ps1
# Import the .ris file into Rayyan or Covidence
```

### For Data Analysis
```powershell
.\nbib_to_ris_converter.ps1
.\process_ris_files.ps1
# Open extracted_ris_data.csv in Excel
```

### For Citation Management
```powershell
.\nbib_to_ris_converter.ps1
# Import the .ris file into Zotero, Mendeley, or EndNote
```

---

**Simple, Fast, Effective - PubMed citations made easy**
