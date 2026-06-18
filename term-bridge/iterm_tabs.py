"""List open iTerm2 windows/tabs via AppleScript."""
from __future__ import annotations

import subprocess
import sys

LIST_SCRIPT = r"""
set out to ""
tell application "iTerm"
    set wCount to count of windows
    repeat with w from 1 to wCount
        tell window w
            set tCount to count of tabs
            repeat with ti from 1 to tCount
                tell tab ti
                    tell current session
                        set tName to name
                    end tell
                    set sCount to count of sessions
                end tell
                set out to out & w & "|||" & ti & "|||" & tName & "|||" & sCount & linefeed
            end repeat
        end tell
    end repeat
end tell
return out
"""


def list_targets() -> tuple[int, list[dict]]:
    if sys.platform != "darwin":
        return 1, []
    try:
        r = subprocess.run(
            ["osascript", "-e", LIST_SCRIPT],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return 1, [{"error": str(e)}]
    if r.returncode != 0:
        return r.returncode, [{"error": (r.stderr or r.stdout or "osascript failed").strip()}]

    rows: list[dict] = []
    for line in (r.stdout or "").splitlines():
        if not line.strip():
            continue
        parts = line.split("|||", 3)
        if len(parts) < 4:
            continue
        rows.append(
            {
                "window": int(parts[0]),
                "tab": int(parts[1]),
                "name": parts[2],
                "sessions": int(parts[3]),
            }
        )
    return 0, rows
