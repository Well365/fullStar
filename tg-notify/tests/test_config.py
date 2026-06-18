import json
from pathlib import Path

import pytest

from tg_notify.core.config import resolve_chat_id, resolve_token
from tg_notify.core.exceptions import TelegramConfigError


def test_resolve_token_missing(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    with pytest.raises(TelegramConfigError):
        resolve_token()


def test_resolve_token_from_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    assert resolve_token() == "test-token"


def test_resolve_chat_id_from_config(tmp_path, monkeypatch):
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"chat_id": 999}), encoding="utf-8")
    assert resolve_chat_id(config_path=str(config)) == 999


def test_resolve_chat_id_explicit():
    assert resolve_chat_id(chat_id=123) == 123
