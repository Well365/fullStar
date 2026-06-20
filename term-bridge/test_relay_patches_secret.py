"""Tests for tg_relay_patches._sanitized_env — keep secrets out of children."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tg-relay"))
import tg_relay_patches as patches


def test_sanitized_env_drops_token():
    clean = patches._sanitized_env({"TELEGRAM_BOT_TOKEN": "secret"})
    assert "TELEGRAM_BOT_TOKEN" not in clean


def test_sanitized_env_keeps_non_secrets():
    src = {"TELEGRAM_BOT_TOKEN": "x", "TG_ITERM_TAB": "3", "FOO": "bar"}
    clean = patches._sanitized_env(src)
    assert clean == {"TG_ITERM_TAB": "3", "FOO": "bar"}


def test_sanitized_env_returns_copy():
    src = {"TG_ITERM_TAB": "1"}
    clean = patches._sanitized_env(src)
    clean["NEW"] = "x"
    assert "NEW" not in src  # original not mutated


def test_secret_keys_includes_bot_token():
    assert "TELEGRAM_BOT_TOKEN" in patches._SECRET_ENV_KEYS
