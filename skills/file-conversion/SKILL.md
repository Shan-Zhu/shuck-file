---
name: file-conversion
description: Use when the user provides or references .docx, .pdf, .xlsx, .pptx, or .csv files and needs to read, analyze, extract, summarize, or convert their contents. Also use when Claude encounters a binary document format it cannot read directly.
---

# File Conversion Skill

Convert documents to clean Markdown that AI agents can read and analyze.

## When to Use

- User shares or references a `.docx`, `.pdf`, `.xlsx`, `.pptx`, or `.csv` file
- User asks to "read", "analyze", "summarize", or "extract" content from a document
- You encounter a binary file format you cannot read directly
- User asks to convert a document to Markdown

## When NOT to Use

- Plain text files (`.txt`, `.md`, `.json`, `.yaml`) — read these directly
- Source code files — read these directly
- Image files (`.png`, `.jpg`) — use vision capabilities instead
- The user just wants to copy/move/rename a file

## Supported Formats

| Format | Extension | What's Preserved |
|--------|-----------|-----------------|
| Word | `.docx` | Headings, bold/italic, lists, tables |
| PDF | `.pdf` | Text content, page breaks |
| Excel | `.xlsx` | All sheets, cell data as tables |
| PowerPoint | `.pptx` | Slide titles, text, tables, notes |
| CSV | `.csv` | All rows/columns as a table |

## Agent Workflow (Recommended)

### Step 1: Probe with `--meta`

```bash
python /path/to/shuck-file/shuck.py "document.xlsx" --meta
```

Returns JSON with file info and estimated token count. Use this to decide whether to convert the full file or warn the user about large documents.

### Step 2: Convert

```bash
python /path/to/shuck-file/shuck.py "document.xlsx"
```

Output goes to stdout with YAML frontmatter. Capture directly — no need to write to a file first.

### Step 3: Analyze

Process the Markdown content as needed (summarize, extract data, answer questions, etc.).

## Command Reference

```bash
# Default: convert to stdout (agent-friendly)
python shuck.py <file>

# Write to specific file
python shuck.py <file> -o output.md

# Write to directory (auto-named, collision-safe)
python shuck.py <file> -d ./output/

# JSON metadata (probe before converting)
python shuck.py <file> --meta

# Skip YAML frontmatter
python shuck.py <file> --no-frontmatter

# List supported formats
python shuck.py --formats
```

## Installing Dependencies

Only install what you need:

```bash
# Word (.docx)
pip install python-docx

# PDF (.pdf)
pip install pdfplumber

# Excel (.xlsx)
pip install openpyxl

# PowerPoint (.pptx)
pip install python-pptx

# CSV — no extra dependencies needed (stdlib)

# All formats at once
pip install python-docx pdfplumber openpyxl python-pptx
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Missing dependency: X` | Required library not installed | Run the `pip install` command shown in the error |
| `unsupported format` | File extension not in supported list | Check `--formats` for supported types |
| `file not found` | Path doesn't exist or has typos | Verify path; quote paths with spaces |
| Empty/garbled output from PDF | Scanned PDF (image-based) | This tool extracts text only; suggest OCR tools |
