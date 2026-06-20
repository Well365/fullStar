"""Tests for terminal_tabs._parse — Terminal.app window/tab enumeration parser.

Terminal.app addresses each terminal as `tab T of window W`; a typical layout is
several windows each holding one tab. The AppleScript emits
`window|||tab|||tty|||process|||title` per line; _parse turns that into the same
row shape iterm_tabs produces, picking a human label (custom title, else
process) and exposing the tty as the stable session_id.
"""
from __future__ import annotations

from terminal_tabs import _parse

# Real osascript output: first field is the window's STABLE id (not z-order).
SAMPLE = (
    "72|||1|||/dev/ttys000|||claude|||⠐ 新增功能列表和文档更新\n"
    "172|||1|||/dev/ttys003|||claude|||✳ 重新告诉我一次\n"
    "153|||1|||/dev/ttys005|||-zsh|||maxwell@Mac\n"
)


def test_parse_window_field_is_stable_id():
    rows = _parse(SAMPLE)
    assert [(r["window"], r["tab"]) for r in rows] == [(72, 1), (172, 1), (153, 1)]


def test_parse_uses_custom_title_as_name():
    rows = _parse(SAMPLE)
    assert rows[0]["name"] == "⠐ 新增功能列表和文档更新"
    assert rows[2]["name"] == "maxwell@Mac"


def test_parse_exposes_tty_as_session_id():
    rows = _parse(SAMPLE)
    assert [r["session_id"] for r in rows] == ["/dev/ttys000", "/dev/ttys003", "/dev/ttys005"]


def test_parse_sessions_always_one():
    rows = _parse(SAMPLE)
    assert all(r["sessions"] == 1 for r in rows)


def test_parse_falls_back_to_process_when_title_empty():
    rows = _parse("1|||1|||/dev/ttys000|||claude||| \n")  # blank title
    assert rows[0]["name"] == "claude"


def test_parse_falls_back_to_tab_label_when_title_and_proc_empty():
    rows = _parse("2|||1|||/dev/ttys000|||  |||  \n")  # no proc, no title
    assert rows[0]["name"] == "tab1"


def test_parse_title_may_contain_delimiter():
    rows = _parse("1|||1|||/dev/ttys000|||claude|||a |||b\n")  # title contains |||
    assert rows[0]["name"] == "a |||b"


def test_parse_missing_tty_yields_none_session_id():
    rows = _parse("1|||1||| |||claude|||title\n")
    assert rows[0]["session_id"] is None


def test_parse_skips_blank_and_malformed_lines():
    rows = _parse("\n1|||1|||tty|||p|||t\nGARBAGE\n2|||x|||tty|||p|||t\n")
    assert [(r["window"], r["tab"]) for r in rows] == [(1, 1)]


def test_parse_empty_input():
    assert _parse("") == []
