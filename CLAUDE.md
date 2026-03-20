# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install in development mode
pip install -e .

# Run all tests
python -m pytest tests/ -v

# Run a single test file
python -m pytest tests/test_router.py -v

# Run a single test
python -m pytest tests/test_router.py::TestRouterAutoRouting::test_small_file_direct -v

# CLI usage (after pip install -e .)
shuck <file>
shuck probe <file>              # force map mode
shuck <file> --all              # force full output
shuck <file> --grep "keyword"
shuck <file> --sections s1,s3
shuck <file> --budget 4000

# CLI usage (without install, from repo root)
python plugin/shuck.py <file>

# MCP Server development
fastmcp dev src/shuck_file/server.py
```

## Architecture

shuck-file is a document-to-Markdown converter for AI agents. Its core design: **one command, smart behavior** — small files output directly, large files return a document map with extraction options.

### Package Structure

```
src/shuck_file/              # PyPI package (the source of truth)
  ├── __init__.py             # Version
  ├── cli.py                  # CLI entry point (console_scripts: shuck)
  ├── server.py               # MCP Server (FastMCP)
  ├── core/                   # Core logic
  │   ├── router.py           # Auto-routing
  │   ├── segmenter.py        # Document segmentation
  │   ├── mapper.py           # Map mode renderer
  │   ├── budget.py           # Smart compression
  │   ├── grep.py             # In-document search
  │   ├── frontmatter.py      # YAML frontmatter
  │   └── models.py           # Data models
  └── extractors/             # Format-specific extractors
      ├── base.py             # Base extractor ABC
      ├── docx_ext.py         # Word
      ├── pdf_ext.py          # PDF
      ├── xlsx_ext.py         # Excel
      ├── pptx_ext.py         # PowerPoint
      └── csv_ext.py          # CSV

plugin/                       # Claude Code plugin (thin wrapper)
  ├── shuck.py                # Delegates to shuck_file.cli.main()
  ├── .claude-plugin/         # Plugin manifest
  └── commands/               # Skill definitions
```

### Request Flow

```
CLI (shuck_file/cli.py) or MCP Server (shuck_file/server.py)
  → validates file extension against SUPPORTED_FORMATS
  → calls router.route(filepath, args)

Router (core/router.py)
  → dispatches to grep/schema/sample/tables/sections if flags present
  → otherwise: estimate tokens via extractor.estimate_tokens()
  → if ≤ 4000 tokens → direct output (extractor.extract())
  → if > 4000 tokens → map mode (segmenter → mapper.render_map())

Extractors (extractors/*.py)
  → each inherits BaseExtractor ABC
  → required: extract(), estimate_tokens()
  → optional: extract_tables(), extract_schema(), extract_sample()
  → registry: get_extractor(filepath) returns correct instance by extension
```

### Key Modules

- **core/models.py** — `Section` (id, title, type, content, tokens, density) and `Result` (source, format, mode, quality, content, sections) dataclasses used throughout
- **core/segmenter.py** — splits documents by format-native structure (sheets/slides/headings/pages), classifies sections as narrative/tabular/mixed/boilerplate with high/medium/low density
- **core/mapper.py** — renders document map Markdown with sections table, preview, and auto-generated next-step commands
- **core/budget.py** — 5-step compression: remove boilerplate → remove low-density → compress narrative (first+last sentence) → compress tables (header+5 rows) → drop from end
- **core/grep.py** — case-insensitive search across segmented sections, returns matches with keyword bolded

## Platform Notes

- stdout uses `sys.stdout.buffer.write(output.encode("utf-8"))` to avoid Windows GBK encoding errors
- Token estimation heuristic: `file_size_bytes / 4` (text-heavy), `/ 3` (xlsx)
- Default auto-routing threshold: 4000 tokens
