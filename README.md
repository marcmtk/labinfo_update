# LABInfo MHTML to Markdown Converter

Project to extract laboratory information from MHTML files and convert to Markdown format, enabling proper version control and easier collaboration.

## Overview

This project extracts structured laboratory information tables from MHTML web archives and converts them to clean, readable Markdown files with proper Danish character support.

## Workflow

The conversion process consists of three steps:

### Step 1: Extract HTML (Automated)

Extract the `dsidDocContWrap` div content from MHTML files to intermediary HTML files.

```bash
# Extract a single file
./extract_html.py "input_file.mhtml"

# Extract all MHTML files in current directory
./extract_html.py --all

# With verbose output
./extract_html.py --all -v
```

This produces `.extracted.html` files that can be viewed in a browser.

### Step 2: Convert to Markdown (Manual)

The assistant manually reviews the extracted HTML file and converts it to Markdown format:

1. Open the `.extracted.html` file in a browser to view the content
2. Have the assistant read the HTML file and convert it to Markdown
3. The assistant creates a `.md` file with proper formatting:
   - Headers become `##` sections
   - Tables are converted to Markdown tables
   - Lists are converted to `-` bullet points
   - Danish characters are preserved
4. **Important:** Name the output `.md` file to match the original `.mhtml` source file (e.g., `LABInfo KMA, SVS - I.1 - Example, ver. 5.mhtml` → `LABInfo KMA, SVS - I.1 - Example, ver. 5.md`)

### Step 3: Compare and Verify

Compare the new Markdown output against the original HTML to verify fidelity:

1. Open the `.extracted.html` file in a browser
2. Review the `.md` file
3. Check that all content is preserved
4. Verify tables, lists, and formatting match

## Legacy Script

The original `extract_mhtml_tables.py` script combines all steps into one automated process. It remains available for reference or quick conversions:

```bash
./extract_mhtml_tables.py "input_file.mhtml"
./extract_mhtml_tables.py --all
```

## Features

- Extracts laboratory information from MHTML files
- Properly decodes Danish characters (ø, å, æ, etc.)
- Preserves document structure and formatting
- Batch processing support for multiple files
- Automatic output filename generation
- Detailed error reporting and logging

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)
