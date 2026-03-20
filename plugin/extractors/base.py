"""Base extractor abstract class."""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseExtractor(ABC):
    """Abstract base for all document extractors."""

    @abstractmethod
    def extract(self, filepath: Path) -> str:
        """Full Markdown extraction (v1 behavior)."""

    @abstractmethod
    def estimate_tokens(self, filepath: Path) -> int:
        """Cheap token estimate without full parse."""

    def extract_tables(self, filepath: Path) -> str:
        """Override for formats with tables. Returns empty by default."""
        return ""

    def extract_schema(self, filepath: Path) -> str:
        """Override for xlsx/csv. Returns empty by default."""
        return ""

    def extract_sample(self, filepath: Path, n: int = 5) -> str:
        """Override for xlsx/csv. Returns empty by default."""
        return ""
