"""Append-only local buffer for iTerm capture (survives scrollback truncation)."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _max_log_lines() -> int:
    raw = os.environ.get("TG_ITERM_LOG_MAX_LINES", "20000").strip()
    try:
        return max(0, int(raw))
    except ValueError:
        return 20000


def _enabled() -> bool:
    v = os.environ.get("TG_ITERM_LOG_BUFFER", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _paths() -> tuple[Path, Path]:
    from iterm_target import resolve_target

    suffix = resolve_target().log_suffix()
    log = ROOT / "inbox" / f"iterm-session-{suffix}.log"
    state = ROOT / "inbox" / f"iterm-session-{suffix}.state"
    return log, state


def _read_state() -> str:
    _, state_file = _paths()
    if state_file.is_file():
        return state_file.read_text(encoding="utf-8")
    return ""


def _write_state(text: str) -> None:
    _, state_file = _paths()
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(text, encoding="utf-8")


def _overlap_line_count(prev_lines: list[str], cur_lines: list[str]) -> int:
    best = 0
    max_k = min(len(prev_lines), len(cur_lines))
    for k in range(1, max_k + 1):
        if prev_lines[-k:] == cur_lines[:k]:
            best = k
    return best


def append_capture(current: str) -> None:
    """Merge iTerm capture into local log (overlap-aware)."""
    if not _enabled() or not current:
        return

    log_file, _ = _paths()
    log_file.parent.mkdir(parents=True, exist_ok=True)
    prev = _read_state()
    cur_lines = current.splitlines()

    if not prev:
        with log_file.open("w", encoding="utf-8") as f:
            f.write(current)
            if not current.endswith("\n"):
                f.write("\n")
        _write_state(current)
        _trim_log()
        return

    if current == prev:
        return

    if current.startswith(prev):
        delta = current[len(prev) :]
        if delta:
            with log_file.open("a", encoding="utf-8") as f:
                f.write(delta)
        _write_state(current)
        _trim_log()
        return

    prev_lines = prev.splitlines()
    overlap = _overlap_line_count(prev_lines, cur_lines)
    new_lines = cur_lines[overlap:]
    if not new_lines:
        _write_state(current)
        return

    with log_file.open("a", encoding="utf-8") as f:
        if overlap == 0:
            from iterm_target import resolve_target

            f.write(f"\n--- iterm buffer gap ({resolve_target().label()}) ---\n")
        f.write("\n".join(new_lines))
        f.write("\n")
    _write_state(current)
    _trim_log()


def _trim_log() -> None:
    max_lines = _max_log_lines()
    log_file, _ = _paths()
    if max_lines <= 0 or not log_file.is_file():
        return
    lines = log_file.read_text(encoding="utf-8").splitlines()
    if len(lines) <= max_lines:
        return
    trimmed = "\n".join(lines[-max_lines:]) + "\n"
    log_file.write_text(trimmed, encoding="utf-8")


def read_log(*, tail_lines: int | None = None) -> str:
    log_file, _ = _paths()
    if not log_file.is_file():
        return ""
    text = log_file.read_text(encoding="utf-8")
    if tail_lines is not None and tail_lines > 0:
        lines = text.splitlines()
        text = "\n".join(lines[-tail_lines:])
    return text


def reset() -> None:
    log_file, state_file = _paths()
    for p in (log_file, state_file):
        if p.is_file():
            p.unlink()


def combined_text(iterm_capture: str, *, tail_lines: int | None) -> str:
    """Prefer local log (full history); fall back to live iTerm capture."""
    append_capture(iterm_capture)
    log = read_log(tail_lines=tail_lines)
    if log.strip():
        return log
    return iterm_capture
