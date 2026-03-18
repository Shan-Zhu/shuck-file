# shuck-file

> Feed any document to your AI agent — in one command.

**shuck-file** converts documents to clean Markdown, designed for AI agents and LLMs. It outputs to stdout by default so agents can capture content directly, supports metadata probing for smart decision-making, and works as both a standalone CLI tool and a Claude Code plugin.

## Why shuck-file?

AI agents can't read binary document formats. They need a bridge:

- **Agent can't read `.docx`** → `shuck report.docx` → clean Markdown on stdout
- **Agent needs to check size first** → `shuck data.xlsx --meta` → JSON with token estimate
- **Zero config** → no settings files, no output directories — just pipe and go

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
# Clone
git clone https://github.com/YourUsername/shuck-file.git

# Install dependencies (or just the ones you need)
pip install -r requirements.txt

# Convert
python shuck.py report.docx
```

## Usage

### CLI

```bash
# Convert to stdout (default, agent-friendly)
python shuck.py document.pdf

# Write to a specific file
python shuck.py document.pdf -o output.md

# Write to a directory (auto-named, collision-safe)
python shuck.py document.pdf -d ./converted/

# Probe metadata before converting (agent workflow)
python shuck.py spreadsheet.xlsx --meta

# Skip YAML frontmatter
python shuck.py document.docx --no-frontmatter

# List supported formats
python shuck.py --formats
```

### Claude Code Plugin

Install as a Claude Code plugin, then use the `/shuck` command:

```
/shuck path/to/document.xlsx
```

The skill also triggers automatically when you share or reference a supported document format in conversation.

### Agent Integration

The recommended agent workflow:

```bash
# 1. Probe — check file info and estimated token count
python shuck.py report.xlsx --meta
# → {"file": "report.xlsx", "format": "xlsx", "sheets": ["Sheet1", "Data"], "estimated_tokens": 3200}

# 2. Convert — capture stdout directly
python shuck.py report.xlsx
# → Markdown with YAML frontmatter

# 3. Analyze — process the content as needed
```

### Output Format

By default, output includes YAML frontmatter:

```markdown
---
source: report.docx
format: docx
converted_by: shuck v1.0.0
---

# Report Title

Content here...
```

Use `--no-frontmatter` to omit it.

## Installation

### As a Claude Code Plugin

```bash
# Via Claude Code CLI
claude plugin add /path/to/shuck-file
```

### Standalone

```bash
git clone https://github.com/YourUsername/shuck-file.git
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

## License

MIT

---

## 中文简介

**shuck-file** 是一个面向 AI agent 设计的文档转 Markdown 工具，支持 Word、PDF、Excel、PowerPoint 和 CSV 五种格式。

核心设计理念：**stdout 优先**（agent 直接捕获）、**`--meta` 元数据探查**（先了解文件再决策）、**零配置**（单命令即用）。既可作为命令行工具独立使用，也可作为 Claude Code 插件自动触发。
