#!/usr/bin/env python3
"""
Extract and convert HTML tables from MHTML files to Markdown format.

This script processes MHTML files containing laboratory information tables
and converts them to clean, readable Markdown files with proper Danish
character encoding.
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
from html import unescape


class MHTMLTableExtractor:
    """Extract tables from MHTML files and convert to Markdown."""

    # Danish character mappings for quoted-printable encoding
    DANISH_CHAR_MAP = {
        '=C3=98': 'Ø',
        '=C3=B8': 'ø',
        '=C3=85': 'Å',
        '=C3=A5': 'å',
        '=C3=86': 'Æ',
        '=C3=A6': 'æ',
        '=C3=89': 'É',
        '=C3=A9': 'é',
        '=C2=B0': '°',
        '=E2=94=82': '│',
        '=3D': '=',
        '=20': ' ',
    }

    def __init__(self, verbose: bool = False):
        """
        Initialize the extractor.

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose

    def log(self, message: str) -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[INFO] {message}")

    def decode_quoted_printable(self, text: str) -> str:
        """
        Decode quoted-printable encoding in text.

        Args:
            text: Text with quoted-printable encoding

        Returns:
            Decoded text with proper Danish characters
        """
        for encoded, decoded in self.DANISH_CHAR_MAP.items():
            text = text.replace(encoded, decoded)
        return text

    def extract_main_table(self, filepath: Path) -> Optional[str]:
        """
        Extract the main laboratory information table from an MHTML file.

        Args:
            filepath: Path to the MHTML file

        Returns:
            HTML string of the extracted table, or None if not found
        """
        self.log(f"Reading file: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove soft line breaks (quoted-printable continuation)
        content = re.sub(r'=\r?\n', '', content)

        # Find the main table with green headers (bgcolor="#99cc00")
        # This table contains the laboratory information
        pattern = r'<table[^>]*>.*?bgcolor.*?#99cc00.*?UNDERS.*?PRINCIP.*?</table>'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

        if not match:
            self.log("Main table not found")
            return None

        table_html = match.group(0)

        # Decode the HTML
        table_html = self.decode_quoted_printable(table_html)
        table_html = unescape(table_html)

        self.log("Table extracted successfully")
        return table_html

    def parse_table_rows(self, table_html: str) -> List[Tuple[str, str]]:
        """
        Parse table rows and extract cell content.

        Args:
            table_html: HTML string of the table

        Returns:
            List of tuples (header, content) for each row
        """
        rows = []

        # Find all <tr> tags
        tr_pattern = r'<tr[^>]*>(.*?)</tr>'
        tr_matches = re.finditer(tr_pattern, table_html, re.DOTALL | re.IGNORECASE)

        for tr_match in tr_matches:
            row_html = tr_match.group(1)

            # Find all <td> or <th> tags in this row
            cell_pattern = r'<t[dh][^>]*>(.*?)</t[dh]>'
            cell_matches = re.finditer(cell_pattern, row_html, re.DOTALL | re.IGNORECASE)

            cells = []
            for cell_match in cell_matches:
                cell_html = cell_match.group(1)
                cell_text = self._parse_cell_content(cell_html)
                cells.append(cell_text)

            if len(cells) >= 2:  # Only keep rows with at least 2 cells
                rows.append((cells[0], cells[1]))

        self.log(f"Parsed {len(rows)} rows")
        return rows

    def _parse_cell_content(self, cell_html: str, indent_level: int = 0) -> str:
        """
        Parse cell content recursively, handling nested lists properly.

        Args:
            cell_html: HTML content of the cell
            indent_level: Current indentation level for nested lists

        Returns:
            Formatted text content
        """
        result = []
        indent = "  " * indent_level

        # Handle ordered lists (convert to numbered items, or bullets for sub-lists)
        ol_pattern = r'<ol[^>]*>(.*?)</ol>'
        for ol_match in re.finditer(ol_pattern, cell_html, re.DOTALL | re.IGNORECASE):
            ol_content = ol_match.group(1)

            # Extract list items
            li_pattern = r'<li[^>]*>(.*?)</li>'
            li_matches = list(re.finditer(li_pattern, ol_content, re.DOTALL | re.IGNORECASE))

            for i, li_match in enumerate(li_matches, 1):
                li_html = li_match.group(1)

                # Check for nested lists
                has_nested = bool(re.search(r'<[ou]l[^>]*>', li_html, re.IGNORECASE))

                if has_nested:
                    # Parse nested content recursively
                    nested_content = self._parse_cell_content(li_html, indent_level + 1)
                    # Extract text before nested list
                    text_before = re.sub(r'<[ou]l[^>]*>.*?</[ou]l>', '', li_html, flags=re.DOTALL | re.IGNORECASE)
                    text_before = self._remove_html_tags(text_before).strip()

                    if text_before:
                        result.append(f"{indent}- {text_before}")
                    if nested_content:
                        result.append(nested_content)
                else:
                    # Simple list item
                    text = self._remove_html_tags(li_html)
                    text = re.sub(r'\s+', ' ', text).strip()
                    if text:
                        result.append(f"{indent}- {text}")

            # Remove processed <ol> from cell_html
            cell_html = cell_html.replace(ol_match.group(0), '')

        # Handle unordered lists
        ul_pattern = r'<ul[^>]*>(.*?)</ul>'
        for ul_match in re.finditer(ul_pattern, cell_html, re.DOTALL | re.IGNORECASE):
            ul_content = ul_match.group(1)

            # Extract list items
            li_pattern = r'<li[^>]*>(.*?)</li>'
            for li_match in re.finditer(li_pattern, ul_content, re.DOTALL | re.IGNORECASE):
                li_html = li_match.group(1)

                # Check for nested lists
                has_nested = bool(re.search(r'<[ou]l[^>]*>', li_html, re.IGNORECASE))

                if has_nested:
                    nested_content = self._parse_cell_content(li_html, indent_level + 1)
                    text_before = re.sub(r'<[ou]l[^>]*>.*?</[ou]l>', '', li_html, flags=re.DOTALL | re.IGNORECASE)
                    text_before = self._remove_html_tags(text_before).strip()

                    if text_before:
                        result.append(f"{indent}- {text_before}")
                    if nested_content:
                        result.append(nested_content)
                else:
                    text = self._remove_html_tags(li_html)
                    text = re.sub(r'\s+', ' ', text).strip()
                    if text:
                        result.append(f"{indent}- {text}")

            # Remove processed <ul> from cell_html
            cell_html = cell_html.replace(ul_match.group(0), '')

        # Handle remaining paragraphs (non-list content)
        # Remove lists first as we've already processed them
        cell_html = re.sub(r'<[ou]l[^>]*>.*?</[ou]l>', '', cell_html, flags=re.DOTALL | re.IGNORECASE)

        # Split by paragraph tags
        paragraphs = re.split(r'</p>\s*<p[^>]*>|<p[^>]*>|</p>', cell_html, flags=re.IGNORECASE)

        for para in paragraphs:
            # Remove all remaining HTML tags
            text = self._remove_html_tags(para)
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            if text and text not in result:
                result.append(text)

        return '\n'.join(result)

    def _remove_html_tags(self, html: str) -> str:
        """
        Remove HTML tags from text while preserving content including < and > characters.

        This is more careful than a simple regex because it only removes actual HTML tags,
        not comparison operators like < or >.

        Args:
            html: HTML string

        Returns:
            Text with HTML tags removed
        """
        # Remove actual HTML tags (opening and closing tags with proper tag names)
        # Tag names must start with a letter
        text = re.sub(r'</?[a-zA-Z][^>]*>', '', html)
        return text

    def rows_to_markdown(self, rows: List[Tuple[str, str]], title: str) -> str:
        """
        Convert table rows to Markdown format.

        Args:
            rows: List of (header, content) tuples
            title: Title for the markdown document

        Returns:
            Formatted markdown string
        """
        markdown_lines = []
        markdown_lines.append(f"# {title}\n")

        # Define metadata headers to skip (from document header table)
        metadata_headers = {
            'Dokumentbrugere:',
            'Læseadgang:',
            'Coronavirus (SARS-Coronavirus-2)',
            'KLINISK MIKROBIOLOGISK AFSNIT'
        }

        for header, content in rows:
            header = header.strip()
            content = content.strip()

            # Skip empty rows
            if not header and not content:
                continue

            # Skip navigation rows with │
            if '│' in header or '│' in content:
                continue

            # Skip metadata/header rows
            if any(meta in header for meta in metadata_headers):
                continue

            # Skip rows where header starts with known metadata patterns
            if header.startswith('Dokument ID:') or header.startswith('Niveau:'):
                continue

            # Format as markdown
            markdown_lines.append(f"## {header}\n")
            markdown_lines.append(f"{content}\n")

        return '\n'.join(markdown_lines)

    def extract_document_title(self, filepath: Path) -> str:
        """
        Extract document title from the MHTML file metadata.

        Args:
            filepath: Path to the MHTML file

        Returns:
            Document title or default title
        """
        # Use the filename without extension as default
        default_title = filepath.stem

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Read first 5000 chars to find the title
                content = f.read(5000)

            # Look for <title> tag
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            if title_match:
                title = title_match.group(1)
                # Decode quoted-printable
                title = self.decode_quoted_printable(title)
                title = unescape(title)
                # Extract just the document name part
                if ' - ' in title:
                    parts = title.split(' - ')
                    if len(parts) >= 3:
                        return ' - '.join(parts[1:])
                return title
        except Exception as e:
            self.log(f"Could not extract title: {e}")

        return default_title

    def process_file(self, input_path: Path, output_path: Optional[Path] = None) -> bool:
        """
        Process a single MHTML file and convert it to Markdown.

        Args:
            input_path: Path to input MHTML file
            output_path: Path to output Markdown file (auto-generated if None)

        Returns:
            True if successful, False otherwise
        """
        self.log(f"Processing: {input_path.name}")

        # Extract the table
        table_html = self.extract_main_table(input_path)
        if not table_html:
            print(f"ERROR: Could not extract table from {input_path.name}")
            return False

        # Parse rows
        rows = self.parse_table_rows(table_html)
        if not rows:
            print(f"ERROR: No rows found in {input_path.name}")
            return False

        # Get title
        title = self.extract_document_title(input_path)

        # Convert to markdown
        markdown = self.rows_to_markdown(rows, title)

        # Determine output path
        if output_path is None:
            output_path = input_path.with_suffix('.md')

        # Write output
        self.log(f"Writing to: {output_path.name}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"✓ Converted {input_path.name} -> {output_path.name}")
        return True

    def process_directory(self, directory: Path, pattern: str = "*.mhtml") -> Tuple[int, int]:
        """
        Process all MHTML files in a directory.

        Args:
            directory: Directory containing MHTML files
            pattern: Glob pattern for matching files

        Returns:
            Tuple of (successful_count, failed_count)
        """
        files = list(directory.glob(pattern))

        if not files:
            print(f"No files matching '{pattern}' found in {directory}")
            return 0, 0

        print(f"Found {len(files)} file(s) to process\n")

        successful = 0
        failed = 0

        for file_path in sorted(files):
            if self.process_file(file_path):
                successful += 1
            else:
                failed += 1

        return successful, failed


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Extract tables from MHTML files and convert to Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single file
  %(prog)s input.mhtml

  # Process a single file with custom output name
  %(prog)s input.mhtml -o output.md

  # Process all MHTML files in current directory
  %(prog)s --all

  # Process all MHTML files in a specific directory
  %(prog)s --all -d /path/to/files
        """
    )

    parser.add_argument(
        'input_file',
        nargs='?',
        type=Path,
        help='Input MHTML file to process'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output Markdown file path (default: same name as input with .md extension)'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all MHTML files in the directory'
    )

    parser.add_argument(
        '-d', '--directory',
        type=Path,
        default=Path('.'),
        help='Directory to process (default: current directory)'
    )

    parser.add_argument(
        '-p', '--pattern',
        default='*.mhtml',
        help='File pattern to match (default: *.mhtml)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.all and not args.input_file:
        parser.error("Either provide an input file or use --all to process all files")

    # Create extractor
    extractor = MHTMLTableExtractor(verbose=args.verbose)

    if args.all:
        # Process all files in directory
        successful, failed = extractor.process_directory(args.directory, args.pattern)
        print(f"\n{'='*60}")
        print(f"Summary: {successful} successful, {failed} failed")
        sys.exit(0 if failed == 0 else 1)
    else:
        # Process single file
        if not args.input_file.exists():
            print(f"ERROR: File not found: {args.input_file}")
            sys.exit(1)

        success = extractor.process_file(args.input_file, args.output)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
