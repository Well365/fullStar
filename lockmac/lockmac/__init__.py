"""lockmac — a macOS privacy veil (black-out overlay, not a lock).

Public API lives in lockmac.core; the CLI entry point is lockmac.cli:main.
"""
from lockmac import core

__all__ = ["core"]
__version__ = "0.1.0"
