"""AppleScript builder for reading Terminal.app scrollback (no activate needed)."""
from __future__ import annotations


def _window_ref(window: int | None) -> str:
    # Stable `window id` (see terminal_inject_lib): plain `window N` is z-order and
    # drifts with focus, so capture must use the same stable id as inject.
    return "front window" if window is None else f"window id {int(window)}"


def build_read_script(*, window: int | None, tab: int) -> str:
    """AppleScript returning the full scrollback (`history`) of the target tab."""
    win = _window_ref(window)
    # Fall back to the front window if the id is stale/invalid (e.g. the .env
    # default's window=1 is not a real id), so capture degrades like inject
    # instead of erroring.
    return (
        'if application "Terminal" is not running then error "No Terminal running"\n'
        'tell application "Terminal"\n'
        '    if (count of windows) is 0 then error "No Terminal window open"\n'
        "    set targetWindow to front window\n"
        f"    try\n"
        f"        set targetWindow to {win}\n"
        f"    end try\n"
        f"    return history of tab {int(tab)} of targetWindow\n"
        "end tell"
    )
