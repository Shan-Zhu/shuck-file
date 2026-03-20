"""YAML frontmatter generator for shuck output."""

from typing import Optional
from .. import __version__


def make_frontmatter(
    source: str,
    fmt: str,
    mode: str = "direct",
    quality: str = "complete",
    quality_note: Optional[str] = None,
    query: Optional[str] = None,
    matches: Optional[int] = None,
) -> str:
    """Generate YAML frontmatter block."""
    lines = [
        "---",
        f"source: {source}",
        f"format: {fmt}",
        f"converted_by: shuck v{__version__}",
    ]
    if mode != "direct":
        lines.append(f"mode: {mode}")
    lines.append(f"quality: {quality}")
    if quality_note:
        lines.append(f"quality_note: {quality_note}")
    if query is not None:
        lines.append(f"query: \"{query}\"")
    if matches is not None:
        lines.append(f"matches: {matches}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines) + "\n"
