#!/usr/bin/env python3
"""List iTerm2 windows, tabs, and sessions (for TG_ITERM_* configuration)."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "term-bridge"))
from iterm_tabs import list_targets  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="List iTerm windows/tabs for TG_ITERM_* config")
    args = parser.parse_args()

    code, rows = list_targets()
    if code != 0:
        err = rows[0].get("error", "failed") if rows else "failed"
        print(err, file=sys.stderr)
        return code

    print("iTerm 目标列表（发 Telegram 时可用 [别名] 或 [t2] 区分）\n")
    cur_w = os.environ.get("TG_ITERM_WINDOW", "1")
    cur_t = os.environ.get("TG_ITERM_TAB", "1")

    last_w = None
    for row in rows:
        w, t = row["window"], row["tab"]
        if w != last_w:
            if last_w is not None:
                print()
            print(f"Window {w}:")
            last_w = w
        sess = row["sessions"]
        note = f", {sess} panes" if sess > 1 else ""
        mark = "  ← 当前 .env" if str(w) == cur_w and str(t) == cur_t else ""
        print(f"  tab {t}: {row['name']!r}{note}")
        print(f"    [t{t}] / @t{t}:   TG_ITERM_WINDOW={w} TG_ITERM_TAB={t}{mark}")

    print(f"\n当前 .env 默认: TG_ITERM_WINDOW={cur_w}  TG_ITERM_TAB={cur_t}")
    print("别名: TG_ITERM_ALIASES=fz:1:7,mobile-agent:1:11")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
