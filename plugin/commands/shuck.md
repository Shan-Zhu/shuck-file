---
name: shuck
description: Convert a document (.docx, .pdf, .xlsx, .pptx, .csv) to Markdown
allowed-tools: Bash(python*), Bash(pip*)
---

# /shuck <path>

Convert a document to Markdown and display the result.

## Instructions

### Step 1: Validate the file

Check that the file exists and has a supported extension (.docx, .pdf, .xlsx, .pptx, .csv).

### Step 2: Install dependencies if needed

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

### Step 3: Convert

Run shuck. It auto-detects file size and picks the best mode:
```bash
python "{{PLUGIN_DIR}}/shuck.py" "<path>"
```

- **Small files**: outputs full Markdown directly
- **Large files**: outputs a document map with sections and suggested next steps

### Step 4: Follow up

If the result is a map (large file), follow the suggested next steps based on the user's needs:

```bash
# Extract specific sections
python "{{PLUGIN_DIR}}/shuck.py" "<path>" --sections s1,s3

# Search within document
python "{{PLUGIN_DIR}}/shuck.py" "<path>" --grep "keyword"

# Tables only
python "{{PLUGIN_DIR}}/shuck.py" "<path>" --tables-only

# Compress to fit budget
python "{{PLUGIN_DIR}}/shuck.py" "<path>" --budget 4000

# Force full output
python "{{PLUGIN_DIR}}/shuck.py" "<path>" --all
```

### Step 5: Present the result

Display the Markdown content. If the user had a specific request (summarize, extract data, answer questions), do that with the converted content.
