"""Data models for shuck-file v2.0."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Section:
    """A logical section of a document."""
    id: str                          # e.g. "s1", "s2", "s3a"
    title: str                       # Section heading or auto-generated label
    type: str = "narrative"          # narrative | tabular | mixed | boilerplate
    content: str = ""                # Markdown content
    tokens: int = 0                  # Estimated token count
    density: str = "medium"          # high | medium | low
    page: Optional[int] = None       # Source page/slide/sheet number
    warnings: list[str] = field(default_factory=list)


@dataclass
class Result:
    """Output of a document conversion."""
    source: str                      # Filename
    format: str                      # Extension without dot
    mode: str = "direct"             # direct | map | grep | sections
    quality: str = "complete"        # complete | partial | failed
    quality_note: Optional[str] = None
    content: str = ""                # Markdown output
    sections: list[Section] = field(default_factory=list)
    total_tokens: int = 0
    warnings: list[str] = field(default_factory=list)
