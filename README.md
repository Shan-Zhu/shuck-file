<p align="right">
  <a href="README_CN.md">🇨🇳 中文</a>
</p>

# shuck-file

> Feed any document to your AI agent — in one command.

**shuck-file** converts documents to clean Markdown for AI agents and LLMs. Small files output directly; large files return a **document map** with section summaries, token counts, and actionable next steps — so agents only pull what they need.

## Why shuck-file?

AI agents need a bridge that's **context-aware**:

- **Small file** → `shuck report.docx` → full Markdown on stdout
- **Large file** → `shuck report.docx` → document map with sections and extraction options
- **Targeted extraction** → `shuck report.docx --sections s1,s3` → only what you need
- **Search** → `shuck report.docx --grep "revenue"` → find without reading everything

## Supported Formats

| Format | Extension | Library | What's Preserved |
|--------|-----------|---------|-----------------|
| Word | `.docx` | python-docx | Headings, bold/italic, lists, tables |
| PDF | `.pdf` | pdfplumber | Text content, page breaks |
| Excel | `.xlsx` | openpyxl | All sheets as Markdown tables |
| PowerPoint | `.pptx` | python-pptx | Titles, text, tables, speaker notes |
| CSV | `.csv` | stdlib | All rows/columns as a table |

## Quick Start

```bash
git clone https://github.com/Shan-Zhu/shuck-file.git
pip install -r requirements.txt
python plugin/shuck.py report.docx
```

## Usage

### Auto-Routing (default)

Small files output directly, large files return a document map.

```bash
# Small file → direct Markdown output
shuck document.pdf

# Large file → document map with sections table + next steps
shuck large-report.pdf
```

### Extraction Options

```bash
# Force full output (bypass map mode)
shuck report.pdf --all

# Extract specific sections
shuck report.pdf --sections s1,s3

# Tables only
shuck report.pdf --tables-only

# Search within document
shuck report.pdf --grep "revenue"

# Token budget (smart compression)
shuck report.pdf --budget 4000

# Combinations work
shuck report.pdf --sections s2,s3 --budget 2000
```

### Excel/CSV Specific

```bash
# Column headers and types
shuck data.xlsx --schema-only

# Headers + first N rows
shuck data.xlsx --sample 5
```

### Power User Subcommands

```bash
# Force map mode (even on small files)
shuck probe document.docx

# Force full extraction (alias for --all)
shuck pull document.docx
```

### Output Control

```bash
# Write to file
shuck document.pdf -o output.md

# Write to directory (auto-named)
shuck document.pdf -d ./converted/

# Skip YAML frontmatter
shuck document.pdf --no-frontmatter

# List supported formats
shuck --formats
```

### Map Mode Output

When a file is large, shuck returns a document map:

```markdown
# Document Map: quarterly-report.pdf

**6 pages | ~12,400 tokens | 6 sections**

## Sections

| # | Title | Type | Tokens | Density |
|---|-------|------|--------|---------|
| s1 | Executive Summary | narrative | 450 | high |
| s2 | Q3 Financial Results | mixed | 2,800 | high |
| s3 | Revenue Breakdown | tabular | 3,200 | high |
| ...

## Next Steps

- `shuck quarterly-report.pdf --all` -- full document (~12,400 tokens)
- `shuck quarterly-report.pdf --sections s1,s2` -- high-density (~3,250 tokens)
- `shuck quarterly-report.pdf --grep "..."` -- search for keywords
```

### Claude Code Plugin

Install as a Claude Code plugin, then use `/shuck`:

```
/shuck path/to/document.xlsx
```

The skill triggers automatically when you reference a supported document format.

## Installation

### As a Claude Code Plugin

```bash
claude plugin add /path/to/shuck-file
```

### Standalone

```bash
git clone https://github.com/Shan-Zhu/shuck-file.git
cd shuck-file
pip install -r requirements.txt
```

### Minimal Install (by format)

```bash
pip install python-docx      # .docx only
pip install pdfplumber        # .pdf only
pip install openpyxl          # .xlsx only
pip install python-pptx       # .pptx only
# .csv needs no extra dependencies
```

## Architecture

```
plugin/
├── shuck.py              # CLI entrypoint
├── core/
│   ├── router.py          # Auto-routing logic
│   ├── segmenter.py       # Document segmentation
│   ├── mapper.py          # Map mode renderer
│   ├── budget.py          # Smart compression
│   ├── grep.py            # In-document search
│   ├── frontmatter.py     # YAML frontmatter
│   └── models.py          # Data models
├── extractors/
│   ├── base.py            # Base extractor ABC
│   ├── docx_ext.py        # Word extractor
│   ├── pdf_ext.py         # PDF extractor
│   ├── xlsx_ext.py        # Excel extractor
│   ├── pptx_ext.py        # PowerPoint extractor
│   └── csv_ext.py         # CSV extractor
tests/
├── test_extractors.py     # 39 tests
├── test_router.py
├── test_segmenter.py
├── test_budget.py
└── test_grep.py
```

## License

MIT
