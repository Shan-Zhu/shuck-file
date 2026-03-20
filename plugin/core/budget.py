"""Budget compression engine for shuck-file."""

import re
from .models import Result, Section


def compress(result: Result, budget: int) -> Result:
    """Compress document content to fit within token budget.

    Compression order:
    1. Remove boilerplate sections
    2. Remove low-density sections
    3. Compress narrative: keep first+last sentence per paragraph
    4. Compress tables: keep header + first 5 rows + last row
    5. Drop entire sections from end (appendices first)
    """
    sections = list(result.sections)
    if not sections:
        return result

    # Track what was omitted/compressed for the budget note
    omitted = []
    compressed = []

    # Step 1: Remove boilerplate
    remaining = []
    for s in sections:
        if s.type == "boilerplate":
            omitted.append(s.id)
        else:
            remaining.append(s)
    sections = remaining

    if _total_tokens(sections) <= budget:
        return _build_result(result, sections, omitted, compressed, budget)

    # Step 2: Remove low-density sections
    remaining = []
    for s in sections:
        if s.density == "low":
            omitted.append(s.id)
        else:
            remaining.append(s)
    sections = remaining

    if _total_tokens(sections) <= budget:
        return _build_result(result, sections, omitted, compressed, budget)

    # Step 3: Compress narrative sections
    for i, s in enumerate(sections):
        if s.type in ("narrative", "mixed"):
            new_content = _compress_narrative(s.content)
            if len(new_content) < len(s.content):
                compressed.append(s.id)
                sections[i] = Section(
                    id=s.id, title=s.title, type=s.type,
                    content=new_content, tokens=len(new_content) // 4,
                    density=s.density, page=s.page, warnings=s.warnings,
                )

    if _total_tokens(sections) <= budget:
        return _build_result(result, sections, omitted, compressed, budget)

    # Step 4: Compress tables
    for i, s in enumerate(sections):
        if s.type in ("tabular", "mixed"):
            new_content = _compress_table(s.content)
            if len(new_content) < len(s.content):
                if s.id not in compressed:
                    compressed.append(s.id)
                sections[i] = Section(
                    id=s.id, title=s.title, type=s.type,
                    content=new_content, tokens=len(new_content) // 4,
                    density=s.density, page=s.page, warnings=s.warnings,
                )

    if _total_tokens(sections) <= budget:
        return _build_result(result, sections, omitted, compressed, budget)

    # Step 5: Drop sections from end
    while sections and _total_tokens(sections) > budget:
        dropped = sections.pop()
        omitted.append(dropped.id)

    return _build_result(result, sections, omitted, compressed, budget)


def _total_tokens(sections: list[Section]) -> int:
    return sum(s.tokens for s in sections)


def _build_result(result: Result, sections: list[Section], omitted: list[str], compressed: list[str], budget: int) -> Result:
    """Build the final result with budget note."""
    content_parts = [s.content for s in sections]

    # Add budget note
    note_parts = [f"> Budget: {budget:,} tokens."]
    if omitted:
        note_parts.append(f"Omitted: {', '.join(omitted)}.")
    if compressed:
        note_parts.append(f"Compressed: {', '.join(compressed)}.")
    if omitted:
        note_parts.append(f"\n> Use `--sections {omitted[0]}` to retrieve omitted content.")

    budget_note = " ".join(note_parts)
    content = "\n\n".join(content_parts).strip() + "\n\n" + budget_note + "\n"

    return Result(
        source=result.source,
        format=result.format,
        mode=result.mode if result.mode != "map" else "direct",
        quality=result.quality,
        quality_note=result.quality_note,
        content=content,
        sections=sections,
        total_tokens=len(content) // 4,
        warnings=result.warnings,
    )


def _compress_narrative(content: str) -> str:
    """Keep first and last sentence of each paragraph."""
    paragraphs = content.split("\n\n")
    result = []
    for para in paragraphs:
        # Skip headings and short paragraphs
        if para.strip().startswith("#") or len(para) < 200:
            result.append(para)
            continue
        sentences = re.split(r"(?<=[.!?])\s+", para.strip())
        if len(sentences) <= 2:
            result.append(para)
        else:
            result.append(f"{sentences[0]} [...] {sentences[-1]}")
    return "\n\n".join(result)


def _compress_table(content: str) -> str:
    """Keep header + first 5 data rows + last row."""
    lines = content.split("\n")
    table_start = None
    table_end = None

    for i, line in enumerate(lines):
        if line.strip().startswith("|"):
            if table_start is None:
                table_start = i
            table_end = i

    if table_start is None:
        return content

    pre = lines[:table_start]
    table_lines = lines[table_start:table_end + 1]
    post = lines[table_end + 1:]

    # Table: header row, separator row, data rows
    if len(table_lines) <= 8:  # header + sep + 5 data + 1 = 8
        return content

    # Keep header (2 lines) + first 5 data + last data
    header = table_lines[:2]
    data = table_lines[2:]
    if len(data) > 6:
        compressed_data = data[:5] + [f"| *...{len(data) - 6} rows omitted...* |"] + [data[-1]]
    else:
        compressed_data = data

    result_lines = pre + header + compressed_data + post
    return "\n".join(result_lines)
