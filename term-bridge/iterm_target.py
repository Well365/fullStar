"""Resolve iTerm2 window / tab / session target from env or CLI."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ItermTarget:
    """1-based window/tab; session None = active pane in tab."""

    window: int | None = 1  # None => frontmost window
    tab: int = 1
    session: int | None = None  # None => current session in tab

    def env_map(self) -> dict[str, str]:
        win = "front" if self.window is None else str(self.window)
        sess = "current" if self.session is None else str(self.session)
        return {
            "ITERM_TARGET_WINDOW": win,
            "ITERM_TARGET_TAB": str(self.tab),
            "ITERM_TARGET_SESSION": sess,
        }

    def label(self) -> str:
        w = "front" if self.window is None else f"w{self.window}"
        s = "" if self.session is None else f"/s{self.session}"
        return f"{w}/t{self.tab}{s}"

    def log_suffix(self) -> str:
        return self.label().replace("/", "-")


def _int_env(name: str, default: int | None) -> int | None:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    if raw.lower() in ("front", "active", "current"):
        return None
    try:
        v = int(raw)
        return v if v > 0 else default
    except ValueError:
        return default


def resolve_target(
    *,
    window: int | None | str | None = None,
    tab: int | None = None,
    session: int | None | str | None = None,
) -> ItermTarget:
    """Env: TG_ITERM_WINDOW, TG_ITERM_TAB, TG_ITERM_SESSION."""
    if window is None:
        win = _int_env("TG_ITERM_WINDOW", _int_env("ITERM_TARGET_WINDOW", 1))
        raw = os.environ.get("TG_ITERM_WINDOW", os.environ.get("ITERM_TARGET_WINDOW", "")).strip().lower()
        if raw in ("front", "active", "current"):
            win = None
    elif isinstance(window, str):
        win = None if window.lower() in ("front", "active", "current") else int(window)
    else:
        win = window

    if tab is None:
        tab = _int_env("TG_ITERM_TAB", _int_env("ITERM_TARGET_TAB", 1)) or 1

    if session is None:
        raw = os.environ.get("TG_ITERM_SESSION", os.environ.get("ITERM_TARGET_SESSION", "")).strip().lower()
        if not raw or raw == "current":
            sess: int | None = None
        else:
            try:
                sess = int(raw)
                if sess < 1:
                    sess = None
            except ValueError:
                sess = None
    elif isinstance(session, str):
        sess = None if session.lower() == "current" else int(session)
    else:
        sess = session if session and session > 0 else None

    return ItermTarget(window=win, tab=tab, session=sess)


def apply_target_env(target: ItermTarget, env: dict[str, str] | None = None) -> dict[str, str]:
    base = dict(env or os.environ)
    base.update(target.env_map())
    if target.window is None:
        base["TG_ITERM_WINDOW"] = "front"
    else:
        base["TG_ITERM_WINDOW"] = str(target.window)
    base["TG_ITERM_TAB"] = str(target.tab)
    if target.session is not None:
        base["TG_ITERM_SESSION"] = str(target.session)
    return base


def applescript_session_block(*, indent: str = "    ") -> str:
    """AppleScript lines that `tell` the resolved session (set env vars first)."""
    i = indent
    return f"""
{i}set winSpec to system attribute "ITERM_TARGET_WINDOW"
{i}set tabIdx to (system attribute "ITERM_TARGET_TAB") as integer
{i}set sessSpec to system attribute "ITERM_TARGET_SESSION"
{i}tell application "iTerm"
{i}    if (count of windows) is 0 then error "No iTerm window open"
{i}    if winSpec is "front" then
{i}        set targetWindow to current window
{i}    else
{i}        set winIdx to winSpec as integer
{i}        if (count of windows) < winIdx then error "Window not found"
{i}        set targetWindow to window winIdx
{i}    end if
{i}    tell targetWindow
{i}        if (count of tabs) < tabIdx then error "Tab not found"
{i}        tell tab tabIdx
{i}            if sessSpec is "current" then
{i}                tell current session
""".rstrip() + "\n"


def applescript_session_close(*, indent: str = "    ", extra_close: int = 0) -> str:
    i = indent
    lines = [
        f"{i}                end tell",
        f"{i}            else",
        f"{i}                set sessIdx to sessSpec as integer",
        f"{i}                tell session sessIdx",
    ]
    for _ in range(extra_close):
        lines.append(f"{i}                end tell")
    lines.extend(
        [
            f"{i}                end tell",
            f"{i}            end if",
            f"{i}        end tell",
            f"{i}    end tell",
            f"{i}end tell",
        ]
    )
    return "\n".join(lines)
