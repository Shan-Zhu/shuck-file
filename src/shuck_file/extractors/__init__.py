"""Extractor registry for shuck-file."""

from pathlib import Path
from .base import BaseExtractor


SUPPORTED_FORMATS = {
    ".docx": "Microsoft Word",
    ".pdf":  "PDF",
    ".xlsx": "Excel Spreadsheet",
    ".pptx": "PowerPoint Presentation",
    ".csv":  "CSV (Comma-Separated Values)",
}


def get_extractor(filepath: Path) -> BaseExtractor:
    """Return the appropriate extractor for a file extension."""
    ext = filepath.suffix.lower()
    if ext == ".docx":
        from .docx_ext import DocxExtractor
        return DocxExtractor()
    elif ext == ".pdf":
        from .pdf_ext import PdfExtractor
        return PdfExtractor()
    elif ext == ".xlsx":
        from .xlsx_ext import XlsxExtractor
        return XlsxExtractor()
    elif ext == ".pptx":
        from .pptx_ext import PptxExtractor
        return PptxExtractor()
    elif ext == ".csv":
        from .csv_ext import CsvExtractor
        return CsvExtractor()
    else:
        supported = ", ".join(SUPPORTED_FORMATS.keys())
        raise ValueError(f"Unsupported format '{ext}'. Supported: {supported}")
