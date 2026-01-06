# Plan: Clean HTML Cruft from Intermediary Files

## Problem Statement
The extracted HTML files contain significant cruft that:
1. Inflates file size (17KB for a relatively simple document)
2. Could overload context windows during markdown conversion
3. Makes manual review harder

## Identified Cruft Categories

### 1. **Empty/Whitespace Elements** (High Priority)
- `<p><strong></strong> </p>` - empty paragraphs with empty bold
- `<span> </span>` and `<span><br></span>` - whitespace-only spans
- `<p><span> </span></p>` - nested whitespace
- `<div style="padding:0px;margin:0px;height:1px;"></div>` - spacer divs
- Empty table cells: `<td valign="top" width="44"> </td>`

### 2. **Layout Tables** (High Priority)
- System info tables: `tbSysDokInfo`, `tbSysDokFormaal`, `tbSysAfsnitStart`
- Logo table: `tblDokNameLogo`
- Document references table: `tblBodyDocReferences`
- Wrapper tables with `tableDokAfsnit` class (keep inner content, remove wrapper)

### 3. **Redundant Attributes** (Medium Priority)
- Table attributes: `cellpadding`, `cellspacing`, `border`
- Width specs: `width="100%"`, `width="27%"`, `width="44"`
- Vertical align: `valign="top"`
- Inline styles: `style="..."` (most are presentation-only)
- Column groups: `<colgroup><col width="44"><col width="*"></colgroup>`

### 4. **System-Specific Classes** (Medium Priority)
Remove class attributes entirely:
- `dsidDocContWrap`, `dsidDocNameLogo`, `dsidDocNameCell`
- `tbSysDokInfo`, `tbSysDokFormaal`, `tbSysAfsnitStart`
- `tableDokAfsnit`, `spD4DocBody`, `spD4DocBodyEnd`
- `rubBesNr`, `d4RefInt`, `docHeadLabel`, `hideScreen`, `hidePrint`

### 5. **Redundant Anchors** (Medium Priority)
Multiple anchor names for same location:
```html
<a name="dafs5619148"></a><a name="afs3730102"></a><a name="nr"></a><a name="Nr"></a><a name="NR"></a><a name="rub1"></a><a name="Rub1"></a>
```
Keep only one meaningful anchor or remove entirely.

### 6. **Non-Content Elements** (Low Priority - Optional)
- Logo images: `<img class="dsidPageLogo" ...>`
- Navigation links section (the internal jump links)
- Print/screen-only divs: `class="hideScreen"`, `class="hidePrint"`

## Proposed Implementation

### Approach: Add HTML Sanitization to `extract_html.py`

Add a new function `sanitize_html()` that runs after extraction:

```python
def sanitize_html(html: str) -> str:
    """Remove cruft from extracted HTML to reduce size."""

    # 1. Remove empty elements
    html = re.sub(r'<span>\s*</span>', '', html)
    html = re.sub(r'<p>\s*(<strong>\s*</strong>)?\s*</p>', '', html)
    html = re.sub(r'<div[^>]*style="[^"]*height:\s*1px[^"]*"[^>]*>\s*</div>', '', html)

    # 2. Remove layout tables (keep content tables with bgcolor headers)
    # ... pattern matching for system tables

    # 3. Strip attributes (keep only essential ones)
    html = re.sub(r'\s+(cellpadding|cellspacing|valign|width)="[^"]*"', '', html)
    html = re.sub(r'\s+class="[^"]*"', '', html)
    html = re.sub(r'\s+style="[^"]*"', '', html)  # Be careful - might want to preserve some

    # 4. Remove redundant anchors
    html = re.sub(r'(<a name="[^"]*"></a>)+', lambda m: m.group(0).split('</a>')[0] + '</a>', html)

    # 5. Collapse multiple whitespace
    html = re.sub(r'\n\s*\n', '\n', html)

    return html
```

### Preservation Rules

**KEEP:**
- Content tables with green headers (`bgcolor="#99cc00"`) - these are the main data
- Actual text content
- Lists (`<ul>`, `<ol>`, `<li>`)
- Bold/italic formatting (`<strong>`, `<b>`, `<em>`, `<i>`)
- Line breaks within content (`<br>`)
- Links (`<a href="...">`)
- The document logistics table (version history) - useful metadata

**REMOVE:**
- All system wrapper elements
- Empty whitespace elements
- Presentation-only attributes
- Redundant class names
- Navigation jump links
- Logo images

## Expected Results

- **Current size**: ~17KB for simple document
- **Expected size**: ~5-8KB (60-70% reduction)
- **Benefit**: More content, less noise for markdown conversion

## Testing Strategy

1. Run extraction on all 3 MHTML files
2. Compare before/after sizes
3. Verify content tables are preserved
4. Check markdown conversion quality is maintained or improved

## Files to Modify

- `extract_html.py` - Add `sanitize_html()` function and integrate into `process_file()`

## Alternative Approaches Considered

1. **Separate cleanup script** - More modular but adds another step to workflow
2. **Cleanup during markdown conversion** - Too late, context already consumed
3. **Use BeautifulSoup** - More robust parsing but adds dependency

Recommendation: Implement in `extract_html.py` using regex for simplicity and no new dependencies.
