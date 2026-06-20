"""Tests for the monitor's auto-default env parsing + key inject command build."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_MON = Path(__file__).resolve().parent / "iterm-monitor.py"
_spec = importlib.util.spec_from_file_location("iterm_monitor_mod", _MON)
mon = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mon)


def test_auto_default_seconds_default(monkeypatch):
    monkeypatch.delenv("TG_ITERM_MONITOR_AUTO_DEFAULT", raising=False)
    assert mon._auto_default_seconds() == 60.0


def test_auto_default_seconds_off(monkeypatch):
    monkeypatch.setenv("TG_ITERM_MONITOR_AUTO_DEFAULT", "off")
    assert mon._auto_default_seconds() == 0.0


def test_auto_default_seconds_false(monkeypatch):
    monkeypatch.setenv("TG_ITERM_MONITOR_AUTO_DEFAULT", "false")
    assert mon._auto_default_seconds() == 0.0


def test_auto_default_seconds_no(monkeypatch):
    monkeypatch.setenv("TG_ITERM_MONITOR_AUTO_DEFAULT", "no")
    assert mon._auto_default_seconds() == 0.0


def test_auto_default_seconds_custom(monkeypatch):
    monkeypatch.setenv("TG_ITERM_MONITOR_AUTO_DEFAULT", "30")
    assert mon._auto_default_seconds() == 30.0


def test_auto_default_caption_default(monkeypatch):
    monkeypatch.delenv("TG_ITERM_AUTO_DEFAULT_CAPTION", raising=False)
    assert "默认" in mon._auto_default_caption()


def test_reload_cursors_on_change_detects_switch():
    import importlib.util, sys
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "iterm_monitor_mod", Path(__file__).resolve().parent / "iterm-monitor.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.reload_cursors_on_change("w1-t1", "w1-t3") is True
    assert mod.reload_cursors_on_change("w1-t3", "w1-t3") is False
