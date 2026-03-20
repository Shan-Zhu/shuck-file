"""Test configuration: ensure src/ is on sys.path for imports."""

import sys
import os

src_path = os.path.join(os.path.dirname(__file__), "..", "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)
