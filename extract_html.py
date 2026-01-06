#!/usr/bin/env python3
"""
Step 1: Extract HTML content from MHTML files.

This script extracts the dsidDocContWrap div content from MHTML files
and outputs it to intermediary HTML files for manual markdown conversion.
"""

import re
import sys
import argparse
from pathlib import Path
from html import unescape


# Danish character mappings for quoted-printable encoding
DANISH_CHAR_MAP = {
    '=C3=98': 'O',
    '=C3=B8': 'o',
    '=C3=85': 'A',
    '=C3=A5': 'a',
    '=C3=86': 'AE',
    '=C3=A6': 'ae',
    '=C3=89': 'E',
    '=C3=A9': 'e',
    '=C2=B0': 'deg',
    '=E2=94=82': '|',
    '=E2=80=93': '-',  # En dash
    '=E2=80=94': '--',  # Em dash
    '=E2=89=A5': '>=',  # Greater than or equal
    '=C3=97': 'x',  # Multiplication sign
    '=3D': '=',
    '=20': ' ',
}

# Actual Unicode character mappings (for proper display)
UNICODE_CHAR_MAP = {
    '=C3=98': '\u00D8',  # O
    '=C3=B8': '\u00F8',  # o
    '=C3=85': '\u00C5',  # A
    '=C3=A5': '\u00E5',  # a
    '=C3=86': '\u00C6',  # AE
    '=C3=A6': '\u00E6',  # ae
    '=C3=89': '\u00C9',  # E
    '=C3=A9': '\u00E9',  # e
    '=C2=B0': '\u00B0',  # degree
    '=E2=94=82': '\u2502',  # box drawing vertical
    '=E2=80=93': '\u2013',  # en dash
    '=E2=80=94': '\u2014',  # em dash
    '=E2=89=A5': '\u2265',  # >=
    '=C3=97': '\u00D7',  # multiplication
    '=3D': '=',
    '=20': ' ',
}


def decode_quoted_printable(text: str) -> str:
    """Decode quoted-printable encoding to Unicode characters."""
    for encoded, decoded in UNICODE_CHAR_MAP.items():
        text = text.replace(encoded, decoded)
    return text


def extract_dsidDocContWrap(filepath: Path, verbose: bool = False) -> str | None:
    """
    Extract the dsidDocContWrap div content from an MHTML file.

    Args:
        filepath: Path to the MHTML file
        verbose: Enable verbose logging

    Returns:
        HTML string of the extracted div content, or None if not found
    """
    if verbose:
        print(f"[INFO] Reading file: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove soft line breaks (quoted-printable continuation)
    content = re.sub(r'=\r?\n', '', content)

    # Find the dsidDocContWrap div using the opening tag
    # Note: In MHTML, equals signs are encoded as =3D, so class="..." becomes class=3D"..."
    pattern = r'<div[^>]*class=3D"dsidDocContWrap"[^>]*>'
    start_match = re.search(pattern, content, re.IGNORECASE)

    if not start_match:
        # Try decoded version
        pattern = r'<div[^>]*class="dsidDocContWrap"[^>]*>'
        start_match = re.search(pattern, content, re.IGNORECASE)

    if start_match:
        if verbose:
            print("[INFO] Found dsidDocContWrap div")
        start_pos = start_match.start()

        # Find the closing </body> tag
        body_end = content.find('</body>', start_pos)
        if body_end == -1:
            body_end = len(content)

        # Extract everything from the div start to before </body>
        raw_html = content[start_pos:body_end]

        # Clean up trailing div closures (there are usually 2: one for dsidDocContWrap, one for dsidDocOverWrap)
        raw_html = re.sub(r'\s*</div>\s*</div>\s*$', '', raw_html, flags=re.DOTALL)
    else:
        if verbose:
            print("[WARN] Could not find dsidDocContWrap div")
        return None

    # Decode quoted-printable characters
    html = decode_quoted_printable(raw_html)

    # Unescape HTML entities
    html = unescape(html)

    if verbose:
        print(f"[INFO] Extracted {len(html)} characters of HTML")

    return html


def extract_title(filepath: Path) -> str:
    """Extract document title from the MHTML file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(5000)

        # Remove soft line breaks
        content = re.sub(r'=\r?\n', '', content)

        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        if title_match:
            title = title_match.group(1)
            title = decode_quoted_printable(title)
            title = unescape(title)
            return title
    except Exception:
        pass

    return filepath.stem


def process_file(input_path: Path, output_path: Path | None = None, verbose: bool = False) -> bool:
    """
    Process a single MHTML file and extract HTML to intermediary file.

    Args:
        input_path: Path to input MHTML file
        output_path: Path to output HTML file (auto-generated if None)
        verbose: Enable verbose output

    Returns:
        True if successful, False otherwise
    """
    if verbose:
        print(f"[INFO] Processing: {input_path.name}")

    # Extract the HTML content
    html = extract_dsidDocContWrap(input_path, verbose)
    if not html:
        print(f"ERROR: Could not extract dsidDocContWrap from {input_path.name}")
        return False

    # Get title for the HTML document
    title = extract_title(input_path)

    # Determine output path
    if output_path is None:
        output_path = input_path.with_suffix('.extracted.html')

    # Create a complete HTML document
    output_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; margin: 10px 0; }}
        td, th {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; }}
    </style>
</head>
<body>
<h1>{title}</h1>
{html}
</body>
</html>
"""

    # Write output
    if verbose:
        print(f"[INFO] Writing to: {output_path.name}")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_html)

    print(f"Extracted {input_path.name} -> {output_path.name}")
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract HTML content from MHTML files (Step 1 of conversion)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single file
  %(prog)s input.mhtml

  # Process a single file with custom output name
  %(prog)s input.mhtml -o output.html

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
        help='Output HTML file path (default: same name with .extracted.html)'
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

    if args.all:
        # Process all files in directory
        files = list(args.directory.glob(args.pattern))

        if not files:
            print(f"No files matching '{args.pattern}' found in {args.directory}")
            sys.exit(0)

        print(f"Found {len(files)} file(s) to process\n")

        successful = 0
        failed = 0

        for file_path in sorted(files):
            if process_file(file_path, verbose=args.verbose):
                successful += 1
            else:
                failed += 1

        print(f"\n{'='*60}")
        print(f"Summary: {successful} successful, {failed} failed")
        sys.exit(0 if failed == 0 else 1)
    else:
        # Process single file
        if not args.input_file.exists():
            print(f"ERROR: File not found: {args.input_file}")
            sys.exit(1)

        success = process_file(args.input_file, args.output, args.verbose)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
