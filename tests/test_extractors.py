"""Tests for extractor classes."""

import os
import tempfile
from pathlib import Path

from shuck_file.extractors import get_extractor, SUPPORTED_FORMATS
from shuck_file.extractors.csv_ext import CsvExtractor


class TestCsvExtractor:
    """Test CSV extractor (no external deps needed)."""

    def _make_csv(self, content: str) -> Path:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8")
        f.write(content)
        f.close()
        return Path(f.name)

    def test_basic_csv(self):
        p = self._make_csv("Name,Age,City\nAlice,30,NYC\nBob,25,LA\n")
        ext = CsvExtractor()
        result = ext.extract(p)
        assert "| Name | Age | City |" in result
        assert "| Alice | 30 | NYC |" in result
        os.unlink(p)

    def test_empty_csv(self):
        p = self._make_csv("")
        ext = CsvExtractor()
        result = ext.extract(p)
        assert "Empty CSV" in result
        os.unlink(p)

    def test_estimate_tokens(self):
        p = self._make_csv("a,b,c\n1,2,3\n")
        ext = CsvExtractor()
        tokens = ext.estimate_tokens(p)
        assert tokens > 0
        os.unlink(p)

    def test_schema(self):
        p = self._make_csv("Name,Age,Score\nAlice,30,95.5\nBob,25,88.0\n")
        ext = CsvExtractor()
        result = ext.extract_schema(p)
        assert "| Column | Type |" in result
        assert "Name" in result
        os.unlink(p)

    def test_sample(self):
        rows = "ID,Value\n" + "\n".join(f"{i},{i*10}" for i in range(100))
        p = self._make_csv(rows)
        ext = CsvExtractor()
        result = ext.extract_sample(p, 3)
        assert "3/100" in result
        os.unlink(p)

    def test_get_extractor(self):
        p = self._make_csv("a,b\n1,2\n")
        ext = get_extractor(p)
        assert isinstance(ext, CsvExtractor)
        os.unlink(p)


class TestSupportedFormats:
    def test_all_formats_present(self):
        expected = {".docx", ".pdf", ".xlsx", ".pptx", ".csv"}
        assert set(SUPPORTED_FORMATS.keys()) == expected

    def test_unsupported_format(self):
        import pytest
        with pytest.raises(ValueError, match="Unsupported"):
            get_extractor(Path("test.txt"))
