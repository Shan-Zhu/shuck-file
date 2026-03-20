"""DOCX extractor for shuck-file."""

import sys
from pathlib import Path
from .base import BaseExtractor


class DocxExtractor(BaseExtractor):

    def extract(self, filepath: Path) -> str:
        try:
            from docx import Document
            from docx.oxml.ns import qn
        except ImportError:
            print("Missing dependency: python-docx\n  pip install python-docx", file=sys.stderr)
            sys.exit(1)

        doc = Document(str(filepath))
        lines: list[str] = []

        for element in doc.element.body:
            tag = element.tag.split("}")[-1]
            if tag == "p":
                lines.append(_convert_paragraph(element, doc))
            elif tag == "tbl":
                lines.append(_convert_table(element, doc))

        return "\n".join(lines).strip() + "\n"

    def estimate_tokens(self, filepath: Path) -> int:
        return filepath.stat().st_size // 4

    def extract_tables(self, filepath: Path) -> str:
        try:
            from docx import Document
            from docx.oxml.ns import qn
        except ImportError:
            return ""

        doc = Document(str(filepath))
        tables = []
        for element in doc.element.body:
            tag = element.tag.split("}")[-1]
            if tag == "tbl":
                tables.append(_convert_table(element, doc))
        return "\n".join(tables).strip() + "\n" if tables else ""


# ── Internal helpers ────────────────────────


def _run_text(run) -> str:
    from docx.oxml.ns import qn

    text = run.text or ""
    if not text.strip():
        return text

    rpr = run.find(qn("w:rPr"))
    bold = False
    italic = False
    if rpr is not None:
        bold = rpr.find(qn("w:b")) is not None and rpr.find(qn("w:b")).get(qn("w:val"), "true") != "false"
        italic = rpr.find(qn("w:i")) is not None and rpr.find(qn("w:i")).get(qn("w:val"), "true") != "false"

    if bold and italic:
        return f"***{text}***"
    elif bold:
        return f"**{text}**"
    elif italic:
        return f"*{text}*"
    return text


def _paragraph_text(element) -> str:
    from docx.oxml.ns import qn

    parts = []
    for run in element.findall(qn("w:r")):
        parts.append(_run_text(run))
    return "".join(parts)


def _get_style_name(element, doc) -> str:
    from docx.oxml.ns import qn

    ppr = element.find(qn("w:pPr"))
    if ppr is not None:
        style_el = ppr.find(qn("w:pStyle"))
        if style_el is not None:
            return style_el.get(qn("w:val"), "")
    return ""


def _get_numpr(element):
    from docx.oxml.ns import qn

    ppr = element.find(qn("w:pPr"))
    if ppr is not None:
        return ppr.find(qn("w:numPr"))
    return None


def _convert_paragraph(element, doc) -> str:
    from docx.oxml.ns import qn

    style = _get_style_name(element, doc).lower()
    text = _paragraph_text(element)

    for level in range(1, 7):
        if style in (f"heading{level}", f"heading {level}"):
            return f"\n{'#' * level} {text}\n"

    if style == "title":
        return f"\n# {text}\n"
    if style == "subtitle":
        return f"\n## {text}\n"

    numpr = _get_numpr(element)
    if numpr is not None or "list" in style:
        indent_level = 0
        if numpr is not None:
            ilvl = numpr.find(qn("w:ilvl"))
            if ilvl is not None:
                indent_level = int(ilvl.get(qn("w:val"), "0"))
        prefix = "  " * indent_level + "- "
        return prefix + text

    if not text.strip():
        return ""
    return text + "\n"


def _convert_table(element, doc) -> str:
    from docx.oxml.ns import qn

    rows = element.findall(qn("w:tr"))
    if not rows:
        return ""

    table_data: list[list[str]] = []
    for tr in rows:
        cells = []
        for tc in tr.findall(qn("w:tc")):
            cell_texts = []
            for p in tc.findall(qn("w:p")):
                cell_texts.append(_paragraph_text(p).strip())
            cells.append(" ".join(cell_texts).replace("|", "\\|"))
        table_data.append(cells)

    if not table_data:
        return ""

    max_cols = max(len(row) for row in table_data)
    for row in table_data:
        while len(row) < max_cols:
            row.append("")

    md_lines = ["\n"]
    md_lines.append("| " + " | ".join(table_data[0]) + " |")
    md_lines.append("| " + " | ".join(["---"] * max_cols) + " |")
    for row in table_data[1:]:
        md_lines.append("| " + " | ".join(row) + " |")
    md_lines.append("")

    return "\n".join(md_lines)
