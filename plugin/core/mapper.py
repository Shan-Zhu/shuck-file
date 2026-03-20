"""Map-mode Markdown renderer."""

from pathlib import Path
from .models import Result


def render_map(filepath: Path, result: Result) -> str:
    """Render a document map as Markdown."""
    ext = filepath.suffix.lower()
    sections = result.sections
    total_tokens = result.total_tokens

    # Page/slide/sheet count
    count_label = _count_label(ext, sections)

    lines = []
    lines.append(f"# Document Map: {filepath.name}\n")
    lines.append(f"**{count_label} | ~{total_tokens:,} tokens | {len(sections)} sections**\n")

    # Sections table
    lines.append("## Sections\n")
    lines.append("| # | Title | Type | Tokens | Density |")
    lines.append("|---|-------|------|--------|---------|")
    for s in sections:
        lines.append(f"| {s.id} | {s.title} | {s.type} | {s.tokens:,} | {s.density} |")
    lines.append("")

    # Preview: first narrative section, up to ~200 tokens
    preview = _generate_preview(sections)
    if preview:
        lines.append("## Preview\n")
        for pline in preview.split("\n"):
            lines.append(f"> {pline}")
        lines.append("")

    # Next steps
    lines.append("## Next Steps\n")
    fname = filepath.name
    lines.append(f"- `shuck {fname} --all` -- full document (~{total_tokens:,} tokens)")

    # Suggest --sections with high-density subset
    high_density = [s for s in sections if s.density == "high"]
    if high_density and len(high_density) < len(sections):
        ids = ",".join(s.id for s in high_density)
        tokens = sum(s.tokens for s in high_density)
        lines.append(f"- `shuck {fname} --sections {ids}` -- high-density sections (~{tokens:,} tokens)")

    # Tables suggestion
    has_tables = any(s.type in ("tabular", "mixed") for s in sections)
    if has_tables:
        table_tokens = sum(s.tokens for s in sections if s.type in ("tabular", "mixed"))
        lines.append(f"- `shuck {fname} --tables-only` -- tables only (~{table_tokens:,} tokens)")

    # Budget suggestion
    if total_tokens > 4000:
        lines.append(f"- `shuck {fname} --budget 4000` -- compressed to fit budget")

    # Grep reminder
    lines.append(f"- `shuck {fname} --grep \"...\"` -- search for keywords")

    # xlsx/csv specific
    if ext in (".xlsx", ".csv"):
        lines.append(f"- `shuck {fname} --schema-only` -- column headers + types only")
        lines.append(f"- `shuck {fname} --sample 5` -- headers + first 5 rows")

    lines.append("")

    # Warnings
    if result.warnings:
        lines.append("## Warnings\n")
        for w in set(result.warnings):
            lines.append(f"- {w}")
        lines.append("")

    return "\n".join(lines)


def _count_label(ext: str, sections: list) -> str:
    """Generate a count label based on format."""
    n = len(sections)
    if ext == ".pdf":
        return f"{n} pages"
    elif ext == ".pptx":
        return f"{n} slides"
    elif ext == ".xlsx":
        return f"{n} sheets"
    else:
        return f"{n} sections"


def _generate_preview(sections: list, max_tokens: int = 200) -> str:
    """Extract preview from first narrative section."""
    for s in sections:
        if s.type in ("narrative", "mixed") and s.content.strip():
            # Strip heading lines
            text_lines = []
            for line in s.content.split("\n"):
                if line.strip().startswith("#"):
                    continue
                if line.strip():
                    text_lines.append(line.strip())

            text = " ".join(text_lines)
            # Truncate to ~max_tokens (approx max_tokens*4 chars)
            max_chars = max_tokens * 4
            if len(text) > max_chars:
                text = text[:max_chars].rsplit(" ", 1)[0] + "..."
            return text

    return ""
