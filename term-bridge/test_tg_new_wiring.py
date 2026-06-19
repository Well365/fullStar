"""Tests for the _spawn_session stdout parser used by the relay /new wiring."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tg-relay"))
import tg_relay_patches as patches


def test_parse_spawn_output_extracts_dir_and_tab():
    res = patches._parse_spawn_output(0, "dir=/Users/x/fullStar/2026-06-19-2230\ntab=4\n", "")
    assert res.code == 0
    assert res.tab == 4
    assert res.workdir == "/Users/x/fullStar/2026-06-19-2230"


def test_parse_spawn_output_failure_keeps_raw():
    res = patches._parse_spawn_output(1, "", "osascript boom")
    assert res.code == 1
    assert res.tab is None
    assert "boom" in res.raw
