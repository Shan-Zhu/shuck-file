"""Tests for budget compression."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "plugin"))

from core.budget import compress, _compress_narrative, _compress_table
from core.models import Result, Section


class TestCompressNarrative:
    def test_short_paragraph_unchanged(self):
        text = "Short paragraph."
        assert _compress_narrative(text) == text

    def test_long_paragraph_compressed(self):
        sentences = ". ".join(f"Sentence {i} with some words" for i in range(10)) + "."
        result = _compress_narrative(sentences)
        assert "[...]" in result
        assert "Sentence 0" in result
        assert "Sentence 9" in result

    def test_heading_preserved(self):
        text = "# My Heading\n\nShort paragraph."
        result = _compress_narrative(text)
        assert "# My Heading" in result


class TestCompressTable:
    def test_small_table_unchanged(self):
        table = "| A | B |\n| --- | --- |\n| 1 | 2 |\n| 3 | 4 |"
        assert _compress_table(table) == table

    def test_large_table_compressed(self):
        lines = ["| Col1 | Col2 |", "| --- | --- |"]
        for i in range(20):
            lines.append(f"| row{i} | val{i} |")
        table = "\n".join(lines)
        result = _compress_table(table)
        assert "omitted" in result
        assert "row0" in result
        assert "row19" in result


class TestCompress:
    def _make_result(self, sections):
        total = sum(s.tokens for s in sections)
        return Result(
            source="test.docx",
            format="docx",
            mode="direct",
            content="\n\n".join(s.content for s in sections),
            sections=sections,
            total_tokens=total,
        )

    def test_removes_boilerplate_first(self):
        sections = [
            Section(id="s1", title="Content", type="narrative", content="Important text. " * 50, tokens=200, density="high"),
            Section(id="s2", title="Copyright", type="boilerplate", content="Copyright notice.", tokens=100, density="low"),
        ]
        result = self._make_result(sections)
        compressed = compress(result, 250)
        assert "s2" not in [s.id for s in compressed.sections]

    def test_removes_low_density(self):
        sections = [
            Section(id="s1", title="Core", type="narrative", content="Key content. " * 50, tokens=200, density="high"),
            Section(id="s2", title="Filler", type="narrative", content="Filler text. " * 50, tokens=200, density="low"),
        ]
        result = self._make_result(sections)
        compressed = compress(result, 250)
        assert "s2" not in [s.id for s in compressed.sections]

    def test_budget_note_present(self):
        sections = [
            Section(id="s1", title="A", type="narrative", content="Content. " * 100, tokens=300, density="high"),
        ]
        result = self._make_result(sections)
        compressed = compress(result, 500)
        assert "Budget:" in compressed.content
