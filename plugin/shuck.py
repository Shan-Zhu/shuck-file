#!/usr/bin/env python3
"""
shuck — Convert documents to clean Markdown for AI agents and LLMs.

Thin wrapper that delegates to the shuck_file package.
"""

import sys
import os

# Allow running from repo without pip install: add src/ to path
_src = os.path.join(os.path.dirname(__file__), "..", "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from shuck_file.cli import main

if __name__ == "__main__":
    main()
