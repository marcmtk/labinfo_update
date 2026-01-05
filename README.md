# LABInfo MHTML to Markdown Converter

Project to extract laboratory information from MHTML files and convert to Markdown format, enabling proper version control and easier collaboration.

## Overview

This project extracts structured laboratory information tables from MHTML web archives and converts them to clean, readable Markdown files with proper Danish character support.

## Usage

### Extract a single file

```bash
./extract_mhtml_tables.py "input_file.mhtml"
```

### Extract with custom output name

```bash
./extract_mhtml_tables.py "input_file.mhtml" -o "output.md"
```

### Extract all MHTML files in current directory

```bash
./extract_mhtml_tables.py --all
```

### Extract all MHTML files in a specific directory

```bash
./extract_mhtml_tables.py --all -d /path/to/mhtml/files
```

### Enable verbose output

```bash
./extract_mhtml_tables.py "input_file.mhtml" -v
```

## Features

- ✅ Extracts laboratory information tables from MHTML files
- ✅ Properly decodes Danish characters (ø, å, æ, etc.)
- ✅ Converts HTML lists to Markdown bullet points
- ✅ Preserves document structure and formatting
- ✅ Batch processing support for multiple files
- ✅ Automatic output filename generation
- ✅ Detailed error reporting and logging

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)
