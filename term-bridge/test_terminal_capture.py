"""Tests for terminal_capture_lib — Terminal.app scrollback read builder."""
from __future__ import annotations

from terminal_capture_lib import build_read_script


def test_targets_terminal_app():
    assert 'tell application "Terminal"' in build_read_script(window=1, tab=1)


def test_reads_history_scrollback():
    # history = full scrollback (vs contents = only visible)
    assert "history" in build_read_script(window=1, tab=1)


def test_front_window_when_none():
    s = build_read_script(window=None, tab=1)
    assert "front window" in s


def test_indexed_window_and_tab():
    # Address by STABLE window id, not z-order index (which drifts with focus).
    s = build_read_script(window=2, tab=3)
    assert "window id 2" in s
    assert "tab 3" in s


def test_stale_window_id_falls_back_to_front():
    # A stored id that no longer exists (or the .env default's window=1) must not
    # error the capture — it falls back to the front window inside a try.
    s = build_read_script(window=999, tab=1)
    assert "window id 999" in s
    assert "front window" in s
    assert "try" in s


def test_guards_no_window():
    assert "No Terminal window" in build_read_script(window=1, tab=1)


def test_guards_not_running_to_avoid_autolaunch():
    # `tell application "Terminal"` auto-launches a closed Terminal; guard first.
    assert "is not running" in build_read_script(window=1, tab=1)
