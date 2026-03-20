"""Tests for auto-routing logic."""

import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "plugin"))

from core.router import route, DEFAULT_THRESHOLD
from core.models import Result


def _make_csv(content: str) -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return Path(f.name)


def _make_args(**kwargs):
    args = MagicMock()
    args.grep = None
    args.schema_only = False
    args.sample = None
    args.tables_only = False
    args.sections = None
    args.all = False
    args.command = None
    args.budget = None
    args.no_frontmatter = False
    for k, v in kwargs.items():
        setattr(args, k, v)
    return args


class TestRouterAutoRouting:
    def test_small_file_direct(self):
        """Small CSV should route to direct mode."""
        p = _make_csv("Name,Age\nAlice,30\n")
        args = _make_args()
        result = route(p, args)
        assert result.mode == "direct"
        assert "| Name | Age |" in result.content
        os.unlink(p)

    def test_large_file_map(self):
        """Large CSV should route to map mode."""
        header = ",".join(f"col{i}" for i in range(20))
        rows = "\n".join(",".join(f"val{i}_{j}" for i in range(20)) for j in range(500))
        p = _make_csv(header + "\n" + rows)
        args = _make_args()
        result = route(p, args)
        assert result.mode == "map"
        assert "Document Map" in result.content
        os.unlink(p)

    def test_force_all(self):
        """--all should force direct mode even for large files."""
        header = ",".join(f"col{i}" for i in range(20))
        rows = "\n".join(",".join(f"val{i}_{j}" for i in range(20)) for j in range(500))
        p = _make_csv(header + "\n" + rows)
        args = _make_args(all=True)
        result = route(p, args)
        assert result.mode == "direct"
        os.unlink(p)

    def test_probe_subcommand(self):
        """probe should force map mode even for small files."""
        p = _make_csv("Name,Age\nAlice,30\n")
        args = _make_args(command="probe")
        result = route(p, args)
        assert result.mode == "map"
        os.unlink(p)

    def test_grep_mode(self):
        """--grep should search within document."""
        p = _make_csv("Name,Age\nAlice,30\nBob,25\n")
        args = _make_args(grep="Alice")
        result = route(p, args)
        assert result.mode == "grep"
        assert "Alice" in result.content
        os.unlink(p)

    def test_schema_only(self):
        """--schema-only should return schema."""
        p = _make_csv("Name,Age\nAlice,30\n")
        args = _make_args(schema_only=True)
        result = route(p, args)
        assert "Column" in result.content
        os.unlink(p)

    def test_sample(self):
        """--sample should return limited rows."""
        rows = "ID,Value\n" + "\n".join(f"{i},{i*10}" for i in range(100))
        p = _make_csv(rows)
        args = _make_args(sample=3)
        result = route(p, args)
        assert "showing" in result.content
        os.unlink(p)
