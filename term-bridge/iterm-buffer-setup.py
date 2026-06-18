#!/usr/bin/env python3
"""Raise iTerm2 scrollback buffer (profile setting) for longer Claude Code output."""
from __future__ import annotations

import argparse
import plistlib
import sys
from pathlib import Path

PLIST = Path.home() / "Library/Preferences/com.googlecode.iterm2.plist"


def configure(*, unlimited: bool = True, lines: int = 100_000) -> tuple[int, str]:
    if sys.platform != "darwin":
        return 1, "macOS only"
    if not PLIST.is_file():
        return 1, f"iTerm2 preferences not found: {PLIST}"

    with PLIST.open("rb") as f:
        data = plistlib.load(f)

    profiles = data.get("New Bookmarks")
    if not isinstance(profiles, list) or not profiles:
        return 1, "No iTerm profiles (New Bookmarks) in preferences"

    changed = 0
    for profile in profiles:
        if not isinstance(profile, dict):
            continue
        name = profile.get("Name", "?")
        if unlimited:
            if profile.get("Unlimited Scrollback") is not True:
                profile["Unlimited Scrollback"] = True
                changed += 1
                print(f"  ✓ {name}: Unlimited Scrollback = on")
            else:
                print(f"  · {name}: already unlimited")
        else:
            old = profile.get("Scrollback Lines")
            profile["Unlimited Scrollback"] = False
            profile["Scrollback Lines"] = int(lines)
            if old != lines:
                changed += 1
            print(f"  ✓ {name}: Scrollback Lines = {lines}")

    if changed:
        with PLIST.open("wb") as f:
            plistlib.dump(data, f)

    msg = (
        "iTerm scrollback updated. Open a new tab/window (or restart iTerm) for best results.\n"
        "Also enable in mobile-agent: TG_ITERM_LOG_BUFFER=1 (local log, default on)."
    )
    return 0, msg


def main() -> int:
    parser = argparse.ArgumentParser(description="Increase iTerm2 scrollback buffer")
    parser.add_argument("--lines", type=int, default=100_000, help="If not unlimited")
    parser.add_argument(
        "--no-unlimited",
        action="store_true",
        help="Use fixed line count instead of unlimited scrollback",
    )
    args = parser.parse_args()
    code, msg = configure(unlimited=not args.no_unlimited, lines=args.lines)
    print(msg)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
