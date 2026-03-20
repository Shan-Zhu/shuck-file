"""CSV extractor for shuck-file."""

import csv
from pathlib import Path
from .base import BaseExtractor


def _cell_str(v: str) -> str:
    return v.replace("|", "\\|").replace("\n", " ")


class CsvExtractor(BaseExtractor):

    def extract(self, filepath: Path) -> str:
        text = filepath.read_text(encoding="utf-8", errors="replace")

        try:
            dialect = csv.Sniffer().sniff(text[:8192])
            delimiter = dialect.delimiter
        except csv.Error:
            delimiter = ","

        reader = csv.reader(text.splitlines(), delimiter=delimiter)
        rows = [row for row in reader if any(cell.strip() for cell in row)]

        if not rows:
            return "*Empty CSV file*\n"

        max_cols = max(len(r) for r in rows)
        for r in rows:
            while len(r) < max_cols:
                r.append("")

        md_lines = []
        md_lines.append("| " + " | ".join(_cell_str(c) for c in rows[0]) + " |")
        md_lines.append("| " + " | ".join(["---"] * max_cols) + " |")
        for row in rows[1:]:
            md_lines.append("| " + " | ".join(_cell_str(c) for c in row) + " |")

        return "\n".join(md_lines) + "\n"

    def estimate_tokens(self, filepath: Path) -> int:
        return filepath.stat().st_size // 4

    def extract_tables(self, filepath: Path) -> str:
        return self.extract(filepath)

    def extract_schema(self, filepath: Path) -> str:
        text = filepath.read_text(encoding="utf-8", errors="replace")

        try:
            dialect = csv.Sniffer().sniff(text[:8192])
            delimiter = dialect.delimiter
        except csv.Error:
            delimiter = ","

        reader = csv.reader(text.splitlines(), delimiter=delimiter)
        rows = [row for row in reader if any(cell.strip() for cell in row)]

        if not rows:
            return "*Empty CSV file*\n"

        header = rows[0]
        data_rows = len(rows) - 1

        # Infer types from first data row
        types = ["text"] * len(header)
        if len(rows) > 1:
            for i, cell in enumerate(rows[1]):
                if i < len(types):
                    try:
                        float(cell)
                        types[i] = "number"
                    except (ValueError, TypeError):
                        types[i] = "text"

        md_lines = [f"**CSV** ({data_rows} rows)\n"]
        md_lines.append("| Column | Type |")
        md_lines.append("| --- | --- |")
        for col, typ in zip(header, types):
            md_lines.append(f"| {_cell_str(col)} | {typ} |")

        return "\n".join(md_lines) + "\n"

    def extract_sample(self, filepath: Path, n: int = 5) -> str:
        text = filepath.read_text(encoding="utf-8", errors="replace")

        try:
            dialect = csv.Sniffer().sniff(text[:8192])
            delimiter = dialect.delimiter
        except csv.Error:
            delimiter = ","

        reader = csv.reader(text.splitlines(), delimiter=delimiter)
        rows = [row for row in reader if any(cell.strip() for cell in row)]

        if not rows:
            return "*Empty CSV file*\n"

        max_cols = max(len(r) for r in rows)
        total = len(rows) - 1
        sample = rows[:n + 1]

        for r in sample:
            while len(r) < max_cols:
                r.append("")

        md_lines = [f"**CSV** (showing {min(n, total)}/{total} rows)\n"]
        md_lines.append("| " + " | ".join(_cell_str(c) for c in sample[0]) + " |")
        md_lines.append("| " + " | ".join(["---"] * max_cols) + " |")
        for row in sample[1:]:
            md_lines.append("| " + " | ".join(_cell_str(c) for c in row) + " |")

        return "\n".join(md_lines) + "\n"
