"""Smoke tests for tg-relay command dispatch (pure branches, no subprocess)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "term-bridge"))


def _load_relay():
    spec = importlib.util.spec_from_file_location(
        "tg_relay_cmd_mod", ROOT / "tg-relay" / "tg-relay.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_help_lists_core_commands():
    mod = _load_relay()
    out = mod._handle_command("/help")
    assert "/shot" in out
    assert "/tap" in out
    assert "/devices" in out


def test_start_returns_help():
    mod = _load_relay()
    assert mod._handle_command("/start") == mod._handle_command("/help")


def test_shot_without_platform_is_usage():
    mod = _load_relay()
    # bare /shot (no platform arg) → usage hint, not a crash
    out = mod._handle_command("/shot")
    assert "shot" in out.lower()


def test_empty_command_message():
    mod = _load_relay()
    assert mod._handle_command("") == "empty message"
