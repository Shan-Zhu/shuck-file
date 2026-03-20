"""MCP Server for shuck-file: document-to-Markdown conversion for AI agents."""

from pathlib import Path
from types import SimpleNamespace
from fastmcp import FastMCP

from . import __version__

mcp = FastMCP(
    "shuck-file",
    description="Convert documents (PDF, DOCX, XLSX, PPTX, CSV) to Markdown. Small files return full content; large files return a section map so you pull only what you need.",
)


@mcp.tool()
def shuck(
    file_path: str,
    mode: str = "auto",
    sections: str = None,
    grep: str = None,
    budget: int = None,
    tables_only: bool = False,
    schema_only: bool = False,
    sample: int = None,
) -> str:
    """Convert a document to Markdown.

    Supports PDF, DOCX, XLSX, PPTX, CSV.
    Small files return full content; large files return a section map so you pull only what you need.

    Args:
        file_path: Path to the document to convert.
        mode: "auto" (default), "all" (force full output), "probe" (force map mode).
        sections: Comma-separated section IDs to extract (e.g. "s1,s3").
        grep: Search keyword within the document.
        budget: Token budget for smart compression.
        tables_only: Extract only tables from the document.
        schema_only: Column headers + types only (xlsx/csv).
        sample: Headers + first N rows (xlsx/csv).
    """
    filepath = Path(file_path).resolve()
    if not filepath.exists():
        return f"Error: file not found: {filepath}"

    from .extractors import SUPPORTED_FORMATS

    ext = filepath.suffix.lower()
    if ext not in SUPPORTED_FORMATS:
        supported = ", ".join(SUPPORTED_FORMATS.keys())
        return f"Error: unsupported format '{ext}'. Supported: {supported}"

    # Build args namespace to match CLI interface
    args = SimpleNamespace(
        grep=grep,
        schema_only=schema_only,
        sample=sample,
        tables_only=tables_only,
        sections=sections,
        budget=budget,
        no_frontmatter=False,
        **{"all": mode == "all"},
        command="probe" if mode == "probe" else None,
    )

    from .core.router import route
    from .core.frontmatter import make_frontmatter

    result = route(filepath, args)

    output = make_frontmatter(
        source=filepath.name,
        fmt=ext.lstrip("."),
        mode=result.mode,
        quality=result.quality,
        quality_note=result.quality_note,
    )
    output += result.content
    return output


@mcp.tool()
def list_formats() -> str:
    """List all supported document formats."""
    from .extractors import SUPPORTED_FORMATS

    lines = ["Supported formats:"]
    for ext, desc in SUPPORTED_FORMATS.items():
        lines.append(f"  {ext:8s} {desc}")
    return "\n".join(lines)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
