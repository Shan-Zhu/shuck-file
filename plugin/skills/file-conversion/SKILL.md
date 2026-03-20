---
name: file-conversion
description: Use when the user provides or references .docx, .pdf, .xlsx, .pptx, or .csv files and needs to read, analyze, extract, summarize, or convert their contents. Also use when Claude encounters a binary document format it cannot read directly.
---

# File Conversion Skill

Convert documents to clean Markdown. Small files output directly; large files return a document map with extraction options.

## When to Use

- User shares or references a `.docx`, `.pdf`, `.xlsx`, `.pptx`, or `.csv` file
- User asks to "read", "analyze", "summarize", or "extract" content from a document
- You encounter a binary file format you cannot read directly

## When NOT to Use

- Plain text files (`.txt`, `.md`, `.json`, `.yaml`) — read directly
- Source code files — read directly
- Image files — use vision capabilities instead

## Workflow

### 1. Run shuck

```bash
python "{{PLUGIN_DIR}}/shuck.py" "<path>"
```

- **Small file** → full Markdown output (use directly)
- **Large file** → document map with sections, token counts, and suggested next steps

### 2. Follow the map (large files only)

The map suggests commands. Pick based on the task:

```bash
# Get specific sections
python "{{PLUGIN_DIR}}/shuck.py" "<path>" --sections s1,s3

# Search for keywords
python "{{PLUGIN_DIR}}/shuck.py" "<path>" --grep "revenue"

# Tables only
python "{{PLUGIN_DIR}}/shuck.py" "<path>" --tables-only

# Fit within a token budget
python "{{PLUGIN_DIR}}/shuck.py" "<path>" --budget 4000

# Force full output
python "{{PLUGIN_DIR}}/shuck.py" "<path>" --all

# Excel/CSV: schema or sample
python "{{PLUGIN_DIR}}/shuck.py" "<path>" --schema-only
python "{{PLUGIN_DIR}}/shuck.py" "<path>" --sample 5
```

## Installing Dependencies

```bash
pip install python-docx pdfplumber openpyxl python-pptx
```
