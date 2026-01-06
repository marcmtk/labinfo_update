# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project converts MHTML files containing Danish laboratory information into Markdown format for version control and collaboration. The workflow has two stages:

1. **Automated extraction** (`extract_html.py`): Extracts the `dsidDocContWrap` div from MHTML files, decodes quoted-printable Danish characters, sanitizes HTML cruft, and outputs `.extracted.html` files
2. **Manual conversion**: Human/assistant reviews the extracted HTML and converts to Markdown with proper formatting

## Commands

```bash
# Extract a single MHTML file to intermediary HTML
./extract_html.py "input_file.mhtml"

# Extract all MHTML files in current directory
./extract_html.py --all

# With verbose output (shows sanitization stats)
./extract_html.py --all -v

# Legacy: Direct MHTML to Markdown conversion (automated but less accurate)
./extract_mhtml_tables.py "input_file.mhtml"
./extract_mhtml_tables.py --all
```

## Architecture

### extract_html.py (Preferred)
- Extracts content from MHTML files preserving the document structure
- `decode_quoted_printable()`: Converts encoded Danish characters (ø, å, æ, etc.) to Unicode
- `sanitize_html()`: Removes layout cruft (system tables, empty elements, presentational attributes) while preserving content tables with green headers (`#99cc00`)
- Output: Complete HTML document viewable in browser

### extract_mhtml_tables.py (Legacy)
- `MHTMLTableExtractor` class with methods for complete MHTML-to-Markdown conversion
- Uses pattern matching to find content tables (green headers or bordered tables with keywords like INDIKATION, PRINCIP)
- `parse_table_rows()` / `_parse_cell_content()`: Recursive parsing of nested lists
- Renders multi-column tables as Markdown tables, 2-column as header/content pairs

## Markdown Conversion Guidelines

When converting extracted HTML to Markdown:
- Headers become `##` sections
- Tables are converted to Markdown tables
- Lists use `-` bullet points
- Danish characters (ø, å, æ) must be preserved
- Output filename should match the original MHTML source (e.g., `LABInfo KMA, SVS - I.1 - Example, ver. 5.md`)

## Requirements

Python 3.6+ with standard library only (no external dependencies).
