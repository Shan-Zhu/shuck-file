"""PDF extractor for shuck-file."""

import sys
from pathlib import Path
from .base import BaseExtractor


class PdfExtractor(BaseExtractor):

    def extract(self, filepath: Path) -> str:
        try:
            import pdfplumber
        except ImportError:
            print("Missing dependency: pdfplumber\n  pip install pdfplumber", file=sys.stderr)
            sys.exit(1)

        lines: list[str] = []
        with pdfplumber.open(str(filepath)) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    lines.append(text)
                if i < len(pdf.pages) - 1:
                    lines.append("\n---\n")

        return "\n\n".join(lines).strip() + "\n"

    def estimate_tokens(self, filepath: Path) -> int:
        return filepath.stat().st_size // 4

    def extract_tables(self, filepath: Path) -> str:
        try:
            import pdfplumber
        except ImportError:
            return ""

        tables_md = []
        with pdfplumber.open(str(filepath)) as pdf:
            for i, page in enumerate(pdf.pages):
                for table in page.extract_tables():
                    if not table:
                        continue
                    # Clean cells
                    cleaned = []
                    for row in table:
                        cleaned.append([
                            (cell or "").replace("|", "\\|").replace("\n", " ")
                            for cell in row
                        ])
                    if not cleaned:
                        continue
                    max_cols = max(len(r) for r in cleaned)
                    for r in cleaned:
                        while len(r) < max_cols:
                            r.append("")
                    md = []
                    md.append(f"\n**Page {i + 1} Table**\n")
                    md.append("| " + " | ".join(cleaned[0]) + " |")
                    md.append("| " + " | ".join(["---"] * max_cols) + " |")
                    for r in cleaned[1:]:
                        md.append("| " + " | ".join(r) + " |")
                    tables_md.append("\n".join(md))

        return "\n\n".join(tables_md).strip() + "\n" if tables_md else ""
