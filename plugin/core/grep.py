"""In-document search for shuck-file."""

import re
from pathlib import Path
from .models import Result, Section
from .segmenter import segment_document


def grep_document(filepath: Path, extractor, keyword: str) -> Result:
    """Search for a keyword across document sections."""
    sections = segment_document(filepath, extractor)
    ext = filepath.suffix.lower()

    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    matched_sections = []
    total_matches = 0

    for sec in sections:
        matches = list(pattern.finditer(sec.content))
        if not matches:
            continue
        total_matches += len(matches)

        # Bold the keyword in context lines
        highlighted_lines = []
        for line in sec.content.split("\n"):
            if pattern.search(line):
                bolded = pattern.sub(lambda m: f"**{m.group()}**", line)
                highlighted_lines.append(bolded)

        matched_content = f"## {sec.id}: {sec.title} ({len(matches)} match{'es' if len(matches) != 1 else ''})\n\n"
        matched_content += "\n".join(highlighted_lines)
        matched_sections.append(Section(
            id=sec.id,
            title=sec.title,
            type=sec.type,
            content=matched_content,
            tokens=len(matched_content) // 4,
            density=sec.density,
        ))

    if not matched_sections:
        content = f"*No matches for \"{keyword}\" found in document.*\n"
    else:
        content = "\n\n".join(s.content for s in matched_sections).strip() + "\n"

    return Result(
        source=filepath.name,
        format=ext.lstrip("."),
        mode="grep",
        content=content,
        sections=matched_sections,
        total_tokens=len(content) // 4,
    )
