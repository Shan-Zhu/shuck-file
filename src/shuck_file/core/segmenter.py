"""Document segmentation into logical sections."""

import re
from pathlib import Path
from .models import Section


def segment_document(filepath, extractor) -> list[Section]:
    """Segment a document into logical sections using 3-layer strategy."""
    content = extractor.extract(filepath)
    ext = filepath.suffix.lower()

    if ext == ".xlsx":
        return _segment_by_sheets(content)
    elif ext == ".pptx":
        return _segment_by_slides(content)
    elif ext == ".csv":
        return _segment_csv(content)
    else:
        # docx, pdf: heading-based + semantic boundaries
        return _segment_by_headings(content, ext)


def _segment_by_sheets(content: str) -> list[Section]:
    """Segment xlsx by sheet headers."""
    parts = re.split(r"(?=^## Sheet: .+$)", content, flags=re.MULTILINE)
    sections = []
    idx = 1
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^## Sheet: (.+?)$", part, re.MULTILINE)
        title = m.group(1).strip() if m else f"Sheet {idx}"
        sec = _make_section(f"s{idx}", title, part)
        sections.append(sec)
        idx += 1
    return sections if sections else [_make_section("s1", "Document", content)]


def _segment_by_slides(content: str) -> list[Section]:
    """Segment pptx by slide headers."""
    parts = re.split(r"(?=^## Slide \d+)", content, flags=re.MULTILINE)
    sections = []
    idx = 1
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^## Slide \d+\s*(?:\n### (.+))?", part)
        title = m.group(1).strip() if m and m.group(1) else f"Slide {idx}"
        sec = _make_section(f"s{idx}", title, part)
        sections.append(sec)
        idx += 1
    return sections if sections else [_make_section("s1", "Document", content)]


def _segment_csv(content: str) -> list[Section]:
    """CSV is always one section."""
    return [_make_section("s1", "Data", content)]


def _segment_by_headings(content: str, ext: str) -> list[Section]:
    """Segment by Markdown headings (docx) or page breaks (pdf)."""
    if ext == ".pdf":
        # Split by horizontal rules (page breaks)
        parts = re.split(r"\n---\n", content)
        if len(parts) > 1:
            sections = []
            for idx, part in enumerate(parts, 1):
                part = part.strip()
                if not part:
                    continue
                # Try to find a heading in the page
                m = re.match(r"^#+\s+(.+)$", part, re.MULTILINE)
                title = m.group(1).strip() if m else f"Page {idx}"
                sec = _make_section(f"s{idx}", title, part)
                # Check for scanned/empty pages
                if len(part) < 10:
                    sec.warnings.append(f"Page {idx} may be scanned or empty")
                sections.append(sec)
            # Force-split large sections
            sections = _force_split(sections)
            return sections if sections else [_make_section("s1", "Document", content)]

    # Heading-based segmentation (docx, single-page pdf)
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    matches = list(heading_pattern.finditer(content))

    if not matches:
        # No headings: split by double newlines into chunks
        return _segment_by_paragraphs(content)

    sections = []
    idx = 1

    # Content before first heading
    if matches[0].start() > 0:
        pre = content[:matches[0].start()].strip()
        if pre:
            sec = _make_section(f"s{idx}", "Introduction", pre)
            sections.append(sec)
            idx += 1

    for i, m in enumerate(matches):
        title = m.group(2).strip()
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        chunk = content[start:end].strip()
        sec = _make_section(f"s{idx}", title, chunk)
        sections.append(sec)
        idx += 1

    sections = _force_split(sections)
    return sections if sections else [_make_section("s1", "Document", content)]


def _segment_by_paragraphs(content: str) -> list[Section]:
    """Fallback: split by double-newline boundaries into ~2000 token chunks."""
    paragraphs = re.split(r"\n\n+", content)
    sections = []
    idx = 1
    current_parts = []
    current_tokens = 0

    for para in paragraphs:
        para_tokens = len(para) // 4
        if current_tokens + para_tokens > 2000 and current_parts:
            text = "\n\n".join(current_parts)
            sec = _make_section(f"s{idx}", f"Section {idx}", text)
            sections.append(sec)
            idx += 1
            current_parts = []
            current_tokens = 0
        current_parts.append(para)
        current_tokens += para_tokens

    if current_parts:
        text = "\n\n".join(current_parts)
        sec = _make_section(f"s{idx}", f"Section {idx}", text)
        sections.append(sec)

    return sections if sections else [_make_section("s1", "Document", content)]


def _force_split(sections: list[Section], max_tokens: int = 3000) -> list[Section]:
    """Split oversized sections at paragraph boundaries."""
    result = []
    for sec in sections:
        if sec.tokens <= max_tokens:
            result.append(sec)
            continue
        # Split at paragraph boundaries
        paragraphs = re.split(r"\n\n+", sec.content)
        sub_idx = 0
        current_parts = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = len(para) // 4
            if current_tokens + para_tokens > max_tokens and current_parts:
                sub_id = f"{sec.id}{'abcdefghijklmnopqrstuvwxyz'[sub_idx]}" if sub_idx < 26 else f"{sec.id}_{sub_idx}"
                text = "\n\n".join(current_parts)
                sub_sec = _make_section(sub_id, f"{sec.title} (cont.)" if sub_idx > 0 else sec.title, text)
                sub_sec.page = sec.page
                sub_sec.warnings = sec.warnings.copy()
                result.append(sub_sec)
                sub_idx += 1
                current_parts = []
                current_tokens = 0
            current_parts.append(para)
            current_tokens += para_tokens

        if current_parts:
            sub_id = f"{sec.id}{'abcdefghijklmnopqrstuvwxyz'[sub_idx]}" if sub_idx > 0 and sub_idx < 26 else sec.id if sub_idx == 0 else f"{sec.id}_{sub_idx}"
            text = "\n\n".join(current_parts)
            sub_sec = _make_section(sub_id, f"{sec.title} (cont.)" if sub_idx > 0 else sec.title, text)
            sub_sec.page = sec.page
            sub_sec.warnings = sec.warnings.copy()
            result.append(sub_sec)

    return result


def _make_section(sid: str, title: str, content: str) -> Section:
    """Create a Section with auto-computed fields."""
    tokens = len(content) // 4
    sec_type = _classify_type(content)
    density = _classify_density(content)
    return Section(
        id=sid,
        title=title,
        type=sec_type,
        content=content,
        tokens=tokens,
        density=density,
    )


def _classify_type(content: str) -> str:
    """Classify section as narrative, tabular, mixed, or boilerplate."""
    lines = content.strip().split("\n")
    if not lines:
        return "narrative"

    table_lines = sum(1 for l in lines if l.strip().startswith("|"))
    ratio = table_lines / len(lines) if lines else 0

    # Boilerplate detection
    boilerplate_patterns = [
        r"(?i)^(copyright|all rights reserved|disclaimer|table of contents|confidential)",
        r"(?i)^\d{4}\s+.*(inc|corp|ltd|llc)",
    ]
    first_text = " ".join(lines[:3]).lower()
    for pat in boilerplate_patterns:
        if re.search(pat, first_text):
            return "boilerplate"

    if ratio > 0.5:
        return "tabular"
    elif ratio > 0.1:
        return "mixed"
    return "narrative"


def _classify_density(content: str) -> str:
    """Classify information density: high, medium, low."""
    words = re.findall(r"\w+", content.lower())
    if not words:
        return "low"
    unique = len(set(words))
    total = len(words)
    ratio = unique / total if total else 0

    if ratio > 0.6:
        return "high"
    elif ratio > 0.3:
        return "medium"
    return "low"
