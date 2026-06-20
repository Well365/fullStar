"""Tests for reply_dedup — a rolling 15-message similarity gate.

new_content_since only compares against the immediately-previous send and only
strips contiguous overlap, so a whole message that repeats info sent a few
messages earlier (non-consecutive) still slips through. This module caches the
last N sent messages and skips a new send that is >= 95% similar to any of them.
"""
from __future__ import annotations

import json

from reply_dedup import (
    BUFFER_CAP,
    DEFAULT_THRESHOLD,
    append_buffer,
    is_duplicate,
    normalize,
    read_buffer,
    similarity,
)


def test_normalize_collapses_whitespace_and_drops_blank_lines():
    assert normalize("  a   b \n\n  c  \n") == "a b\nc"


def test_similarity_identical_is_one():
    assert similarity("hello world", "hello world") == 1.0


def test_similarity_disjoint_is_low():
    assert similarity("alpha beta gamma", "totally other text here") < 0.5


def test_is_duplicate_true_for_near_identical():
    buf = [normalize("源1: Caixin\n源2: OCCRP\n源3: Taipei\n源4: 共同社")]
    # same info, one trailing word differs -> well above 95%
    candidate = "源1: Caixin\n源2: OCCRP\n源3: Taipei\n源4: 共同社!"
    assert is_duplicate(candidate, buf) is True


def test_is_duplicate_false_for_novel_message():
    buf = [normalize("源1: Caixin\n源2: OCCRP")]
    assert is_duplicate("完全不同的一段新内容，讲的是别的事情", buf) is False


def test_is_duplicate_false_for_empty_buffer():
    assert is_duplicate("anything", []) is False


def test_is_duplicate_checks_all_buffer_entries_not_just_last():
    # near-dup matches an OLDER entry; the most recent entry is unrelated.
    buf = [
        normalize("旧消息 A：源1 源2 源3 源4 源5"),
        normalize("最近一条完全不同的话题 xyz"),
    ]
    candidate = "旧消息 A：源1 源2 源3 源4 源5"
    assert is_duplicate(candidate, buf) is True


def test_read_missing_file_returns_empty(tmp_path):
    assert read_buffer(tmp_path / "nope.json") == []


def test_read_corrupt_file_returns_empty(tmp_path):
    p = tmp_path / "buf.json"
    p.write_text("{ broken", encoding="utf-8")
    assert read_buffer(p) == []


def test_append_roundtrip_stores_normalized(tmp_path):
    p = tmp_path / "buf.json"
    append_buffer(p, "  hello   world  \n")
    assert read_buffer(p) == ["hello world"]


def test_append_caps_at_buffer_cap(tmp_path):
    p = tmp_path / "buf.json"
    for i in range(BUFFER_CAP + 5):
        append_buffer(p, f"message {i}")
    buf = read_buffer(p)
    assert len(buf) == BUFFER_CAP
    # oldest dropped, newest kept
    assert buf[-1] == f"message {BUFFER_CAP + 4}"
    assert buf[0] == f"message {5}"


def test_append_is_atomic_valid_json(tmp_path):
    p = tmp_path / "buf.json"
    append_buffer(p, "x")
    json.loads(p.read_text(encoding="utf-8"))  # must parse


def test_default_threshold_is_95_percent():
    assert DEFAULT_THRESHOLD == 0.95
    assert BUFFER_CAP == 15
