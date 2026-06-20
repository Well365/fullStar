# term-bridge/test_target_default.py
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import target_default as td
from iterm_target import ItermTarget


def test_parse_state_valid():
    assert td.parse_state('{"window": 1, "tab": 3}') == ItermTarget(window=1, tab=3)


def test_parse_state_window_null_is_front():
    assert td.parse_state('{"window": null, "tab": 2}') == ItermTarget(window=None, tab=2)


@pytest.mark.parametrize("raw", ["", "not json", "{}", '{"tab": 0}', '{"window": 1}', '{"tab": "x"}', "[]"])
def test_parse_state_invalid_returns_none(raw):
    assert td.parse_state(raw) is None


def test_dump_then_parse_roundtrip():
    t = ItermTarget(window=2, tab=5)
    assert td.parse_state(td.dump_state(t)) == t


def test_write_then_read_roundtrip(tmp_path):
    p = tmp_path / "target-default.json"
    written = td.write_default(1, 4, path=p)
    assert written == ItermTarget(window=1, tab=4)
    assert td.read_default(path=p) == ItermTarget(window=1, tab=4)


def test_read_missing_file_returns_none(tmp_path):
    assert td.read_default(path=tmp_path / "nope.json") is None


def test_read_corrupt_file_returns_none(tmp_path):
    p = tmp_path / "target-default.json"
    p.write_text("{ broken", encoding="utf-8")
    assert td.read_default(path=p) is None


def test_write_is_atomic_no_partial(tmp_path):
    p = tmp_path / "target-default.json"
    td.write_default(None, 7, path=p)
    # file is complete, parseable JSON with the expected fields
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data == {"window": None, "tab": 7}


def test_clear_default_removes_file(tmp_path):
    p = tmp_path / "target-default.json"
    td.write_default(1, 2, path=p)
    td.clear_default(path=p)
    assert not p.exists()
    td.clear_default(path=p)  # idempotent, no raise


def test_current_target_uses_default_when_set(tmp_path, monkeypatch):
    p = tmp_path / "target-default.json"
    td.write_default(1, 9, path=p)
    monkeypatch.setattr(td, "default_path", lambda: p)
    assert td.current_target() == ItermTarget(window=1, tab=9)


def test_current_target_falls_back_to_resolve(tmp_path, monkeypatch):
    monkeypatch.setattr(td, "default_path", lambda: tmp_path / "absent.json")
    monkeypatch.setattr(td, "resolve_target", lambda: ItermTarget(window=1, tab=1))
    assert td.current_target() == ItermTarget(window=1, tab=1)
