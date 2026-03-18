---
name: shuck
description: Convert a document (.docx, .pdf, .xlsx, .pptx, .csv) to Markdown
allowed-tools: Bash(python*), Bash(pip*)
---

# /shuck <path>

Convert a document to Markdown and display the result.

## Instructions

You are converting a document to Markdown using the shuck tool.

### Step 1: Validate the file

Check that the file exists and has a supported extension (.docx, .pdf, .xlsx, .pptx, .csv).

### Step 2: Probe with --meta

Run:
```bash
python "{{PLUGIN_DIR}}/shuck.py" "<path>" --meta
```

Review the JSON output. If `estimated_tokens` is very large (>50000), warn the user that the document is large and ask if they want to proceed.

### Step 3: Install dependencies if needed

If the conversion fails due to a missing dependency, install it:
```bash
pip install <package>
```

Packages by format:
- .docx → `python-docx`
- .pdf → `pdfplumber`
- .xlsx → `openpyxl`
- .pptx → `python-pptx`
- .csv → no extra dependency

### Step 4: Convert

Run:
```bash
python "{{PLUGIN_DIR}}/shuck.py" "<path>"
```

### Step 5: Present the result

Display the converted Markdown content to the user. If the user had a specific request (summarize, extract data, answer questions), do that with the converted content.
