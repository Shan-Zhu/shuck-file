"""Tests for document segmentation."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "plugin"))

from core.segmenter import (
    _classify_type,
    _classify_density,
    _make_section,
    _segment_by_headings,
    _force_split,
)


class TestClassifyType:
    def test_narrative(self):
        text = "This is a paragraph of text.\nAnother line of content.\nMore text here."
        assert _classify_type(text) == "narrative"

    def test_tabular(self):
        text = "| A | B |\n| --- | --- |\n| 1 | 2 |\n| 3 | 4 |\n| 5 | 6 |"
        assert _classify_type(text) == "tabular"

    def test_mixed(self):
        text = "Some intro text.\n| A | B |\n| --- | --- |\n| 1 | 2 |\nMore narrative.\nExtra line.\nAnother.\nMore.\nAgain."
        assert _classify_type(text) in ("mixed", "narrative")

    def test_boilerplate(self):
        text = "Copyright 2024 Acme Corp. All rights reserved.\nConfidential."
        assert _classify_type(text) == "boilerplate"


class TestClassifyDensity:
    def test_high_density(self):
        text = "quantum physics entropy thermodynamics wavelength frequency amplitude"
        assert _classify_density(text) == "high"

    def test_low_density(self):
        text = "the the the the the the the the the the the the is is is is"
        assert _classify_density(text) == "low"


class TestMakeSection:
    def test_basic(self):
        sec = _make_section("s1", "Title", "Some content here")
        assert sec.id == "s1"
        assert sec.title == "Title"
        assert sec.tokens > 0
        assert sec.type == "narrative"


class TestSegmentByHeadings:
    def test_with_headings(self):
        content = "# Introduction\n\nSome intro.\n\n# Methods\n\nSome methods.\n\n# Results\n\nSome results."
        sections = _segment_by_headings(content, ".docx")
        assert len(sections) == 3
        assert sections[0].title == "Introduction"

    def test_no_headings(self):
        content = "Para one.\n\nPara two.\n\nPara three."
        sections = _segment_by_headings(content, ".docx")
        assert len(sections) >= 1

    def test_pre_heading_content(self):
        content = "Preamble text.\n\n# Chapter 1\n\nContent."
        sections = _segment_by_headings(content, ".docx")
        assert sections[0].title == "Introduction"


class TestForceSplit:
    def test_no_split_needed(self):
        sec = _make_section("s1", "Short", "short content")
        result = _force_split([sec])
        assert len(result) == 1

    def test_split_large(self):
        # Create a section with >3000 tokens (~12000 chars)
        long_text = "\n\n".join(f"Paragraph {i}. " + "word " * 200 for i in range(20))
        sec = _make_section("s1", "Long Section", long_text)
        result = _force_split([sec])
        assert len(result) > 1
        assert result[0].id.startswith("s1")
