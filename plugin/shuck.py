#!/usr/bin/env python3
"""
shuck — Convert documents to clean Markdown for AI agents and LLMs.

Supports: .docx, .pdf, .xlsx, .pptx, .csv
"""

__version__ = "2.0.0"

import sys
import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shuck",
        description="Convert documents to clean Markdown for AI agents and LLMs.",
    )
    parser.add_argument("file", nargs="?", help="Path to the document to convert")

    # Mode flags
    parser.add_argument("--all", action="store_true", help="Force full output, bypass map mode")

    # Extraction filters
    parser.add_argument("--sections", metavar="IDs", help="Extract specific sections (e.g. s1,s3)")
    parser.add_argument("--tables-only", action="store_true", help="Extract only tables")
    parser.add_argument("--budget", type=int, metavar="N", help="Token budget with smart compression")
    parser.add_argument("--grep", metavar="KEYWORD", help="Search within document")

    # Format-specific (xlsx/csv)
    parser.add_argument("--schema-only", action="store_true", help="Column headers + types only")
    parser.add_argument("--sample", type=int, metavar="N", help="Headers + first N rows")

    # Output control (kept from v1)
    parser.add_argument("-o", "--output", metavar="FILE", help="Write output to a specific file")
    parser.add_argument("-d", "--dir", metavar="DIR", help="Write output to a directory (auto-named)")
    parser.add_argument("--no-frontmatter", action="store_true", help="Omit YAML frontmatter from output")

    # Info
    parser.add_argument("--version", action="version", version=f"shuck {__version__}")
    parser.add_argument("--formats", action="store_true", help="List supported formats and exit")

    return parser


def main():
    # Detect probe/pull subcommands before argparse
    command = None
    argv = sys.argv[1:]
    if argv and argv[0] in ("probe", "pull"):
        command = argv.pop(0)

    parser = build_parser()
    args = parser.parse_args(argv)
    args.command = command

    from extractors import SUPPORTED_FORMATS

    # --formats
    if args.formats:
        print("Supported formats:")
        for ext, desc in SUPPORTED_FORMATS.items():
            print(f"  {ext:8s} {desc}")
        sys.exit(0)

    # Require file
    if not args.file:
        parser.print_help()
        sys.exit(1)

    filepath = Path(args.file).resolve()
    if not filepath.exists():
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    ext = filepath.suffix.lower()
    if ext not in SUPPORTED_FORMATS:
        supported = ", ".join(SUPPORTED_FORMATS.keys())
        print(f"Error: unsupported format '{ext}'. Supported: {supported}", file=sys.stderr)
        sys.exit(1)

    # Route to appropriate handler
    from core.router import route
    result = route(filepath, args)

    # Build output
    output = ""
    if not args.no_frontmatter:
        from core.frontmatter import make_frontmatter
        output = make_frontmatter(
            source=filepath.name,
            fmt=ext.lstrip("."),
            mode=result.mode,
            quality=result.quality,
            quality_note=result.quality_note,
        )
    output += result.content

    # Write output
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"Written to: {out_path}", file=sys.stderr)
    elif args.dir:
        out_dir = Path(args.dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_name = filepath.stem + ".md"
        out_path = out_dir / out_name
        counter = 1
        while out_path.exists():
            out_path = out_dir / f"{filepath.stem} ({counter}).md"
            counter += 1
        out_path.write_text(output, encoding="utf-8")
        print(f"Written to: {out_path}", file=sys.stderr)
    else:
        sys.stdout.write(output)


if __name__ == "__main__":
    main()
