"""Tests for in-document search."""

import os
import tempfile
from pathlib import Path

from shuck_file.core.grep import grep_document
from shuck_file.extractors.csv_ext import CsvExtractor


def _make_csv(content: str) -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return Path(f.name)


class TestGrepDocument:
    def test_found(self):
        p = _make_csv("Name,City\nAlice,NewYork\nBob,Boston\n")
        ext = CsvExtractor()
        result = grep_document(p, ext, "Alice")
        assert result.mode == "grep"
        assert "**Alice**" in result.content
        os.unlink(p)

    def test_not_found(self):
        p = _make_csv("Name,City\nAlice,NYC\n")
        ext = CsvExtractor()
        result = grep_document(p, ext, "Charlie")
        assert "No matches" in result.content
        os.unlink(p)

    def test_case_insensitive(self):
        p = _make_csv("Name,City\nAlice,NYC\n")
        ext = CsvExtractor()
        result = grep_document(p, ext, "alice")
        assert "**Alice**" in result.content
        os.unlink(p)

    def test_multiple_matches(self):
        p = _make_csv("A,B\nfoo,bar\nfoo,baz\n")
        ext = CsvExtractor()
        result = grep_document(p, ext, "foo")
        assert result.content.count("**foo**") == 2
        os.unlink(p)
