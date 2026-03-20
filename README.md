<p align="right">
  <a href="README_CN.md">🇨🇳 中文</a>
</p>

# shuck-file

[![PyPI](https://img.shields.io/pypi/v/shuck-file)](https://pypi.org/project/shuck-file/)
[![MCP Registry](https://img.shields.io/badge/MCP_Registry-available-blue)](https://registry.modelcontextprotocol.io/servers/io.github.Shan-Zhu%2Fshuck-file)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Any file in, Markdown out — read only what matters.

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

## Installation

### Via pip (recommended)

```bash
pip install shuck-file
```

This installs the `shuck` CLI command and the MCP server.

### From source

```bash
git clone https://github.com/Shan-Zhu/shuck-file.git
cd shuck-file
pip install -e .
```

## Quick Start

```bash
# Convert a document
shuck report.docx

# Force full output (bypass map mode)
shuck large-report.pdf --all

# Search within a document
shuck report.pdf --grep "revenue"
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

## MCP Server

shuck-file includes an MCP (Model Context Protocol) server, making it available to any MCP-compatible AI tool.

### Claude Code

```bash
claude mcp add shuck-file -- shuck-file
```

Or add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "shuck-file": {
      "command": "shuck-file",
      "args": []
    }
  }
}
```

### Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "shuck-file": {
      "command": "shuck-file",
      "args": []
    }
  }
}
```

### Windsurf

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "shuck-file": {
      "command": "shuck-file",
      "args": []
    }
  }
}
```

### Any MCP Client

shuck-file registers as an MCP server via the `mcp.servers` entry point. Tools exposed:

- **`shuck`** — Convert a document to Markdown with all options (mode, sections, grep, budget, etc.)
- **`list_formats`** — List supported document formats

### Claude Code Plugin

Install as a Claude Code plugin for the `/shuck` skill:

```bash
claude plugin add /path/to/shuck-file
```

## Architecture

```
src/shuck_file/
├── cli.py                # CLI entrypoint
├── server.py             # MCP Server (FastMCP)
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
plugin/                    # Claude Code plugin wrapper
tests/
├── test_extractors.py
├── test_router.py
├── test_segmenter.py
├── test_budget.py
└── test_grep.py
```

## License

MIT

<!-- mcp-name: io.github.Shan-Zhu/shuck-file -->
