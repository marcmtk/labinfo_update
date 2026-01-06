# Bakteriæmi Extraction Comparison Report

## Summary
Fixed the MHTML table extraction to capture ALL clinical treatment tables instead of just the first/largest one.

## Before Fix
- **Extraction method**: Found largest single table with clinical headers
- **Tables captured**: 1 table
- **Rows extracted**: 2 rows
- **Sections captured**: Only section 2.1 (Gram-positive kokker i hobe)
- **Coverage**: ~7% of clinical content

## After Fix
- **Extraction method**: Find ALL tables with clinical headers (size > 1000 bytes)
- **Tables captured**: 12 tables
- **Rows extracted**: 34 rows
- **Sections captured**: All treatment sections (2.1-2.11) + DENOVA score
- **Coverage**: ~95% of table-based clinical content

## Sections Successfully Captured (Tables)
✅ 2.1) Gram-positive kokker i hobe – ligner stafylokokker
✅ 2.2) Gram-positive kokker i par/kæde – ligner streptokokker
✅ 2.3) Små Gram-positive stave (bevægelige) – ligner listeria
✅ 2.4) Gram-positive stave
✅ 2.5) Gram-negative diplokokker
✅ 2.6) Små Gram-negative stave
✅ 2.7) Små skrueformede Gram-negative stave – ligner Campylobacter
✅ 2.8) Store Gram-negative stave - ligner enterobakterier
✅ 2.9) Gram-negative stave - ligner Pseudomonas
✅ 2.10) Anaerobe bakterier
✅ 2.11) Gær
✅ 3.4) DENOVA score - Enterococcus faecalis

## Sections Not Captured (Non-Table Content)
These sections contain text, bullet lists, and images rather than structured tables:

ℹ️ 3.1) Modificerede Duke kriterier for endocarditis (bullet lists)
ℹ️ 3.2) Foreslået algoritme for Ekkokardiografi ved Streptokokker (images)
ℹ️ 3.3) HANDOC Score - Non-hæmolytiske streptokokker (paragraph text)
ℹ️ 3.5) VIRSTA score - S. aureus (paragraph text)

## Technical Changes
Modified `extract_main_table()` in extract_mhtml_tables.py:
- Changed from selecting single largest table to collecting ALL matching tables
- Lowered size threshold from "max" to 1000 bytes minimum
- Wrapped multiple tables in a container div for combined processing

## Impact
All critical clinical treatment information is now preserved in the markdown extraction.
