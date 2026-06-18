#!/usr/bin/env python3
"""tg-relay entry with iTerm tab routing."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "term-bridge"))
sys.path.insert(0, str(ROOT / "tg-relay"))

spec = importlib.util.spec_from_file_location("tg_relay", ROOT / "tg-relay" / "tg-relay.py")
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

from tg_relay_patches import apply  # noqa: E402

apply(mod)

if __name__ == "__main__":
    raise SystemExit(mod.main())
