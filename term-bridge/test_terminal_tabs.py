"""Tests for terminal_tabs._parse — Terminal.app window/tab enumeration parser.

Terminal.app addresses each terminal as `tab T of window W`; a typical layout is
several windows each holding one tab. The AppleScript emits
`window|||tab|||title|||process` per line; _parse turns that into the same row
shape iterm_tabs produces, picking a human label (custom title, else process).
"""
from __future__ import annotations

from terminal_tabs import _parse

# Real osascript output captured from a 3-window Terminal.app session.
SAMPLE = (
    "1|||1|||⠐ 新增功能列表和文档更新|||claude\n"
    "2|||1|||✳ 重新告诉我一次|||claude\n"
    "3|||1|||maxwell@Mac|||-zsh\n"
)


def test_parse_three_windows_one_tab_each():
    rows = _parse(SAMPLE)
    assert [(r["window"], r["tab"]) for r in rows] == [(1, 1), (2, 1), (3, 1)]


def test_parse_uses_custom_title_as_name():
    rows = _parse(SAMPLE)
    assert rows[0]["name"] == "⠐ 新增功能列表和文档更新"
    assert rows[2]["name"] == "maxwell@Mac"


def test_parse_sessions_always_one():
    rows = _parse(SAMPLE)
    assert all(r["sessions"] == 1 for r in rows)


def test_parse_falls_back_to_process_when_title_empty():
    rows = _parse("1|||1||| |||claude\n")  # blank title
    assert rows[0]["name"] == "claude"


def test_parse_falls_back_to_tab_label_when_title_and_proc_empty():
    rows = _parse("2|||1|||  |||\n")
    assert rows[0]["name"] == "tab1"


def test_parse_skips_blank_and_malformed_lines():
    rows = _parse("\n1|||1|||t|||p\nGARBAGE\n2|||x|||t|||p\n")
    assert [(r["window"], r["tab"]) for r in rows] == [(1, 1)]


def test_parse_empty_input():
    assert _parse("") == []
