import json
from pathlib import Path

import pytest

import tg_notify.core.config as cfg
from tg_notify.core.config import resolve_chat_id, resolve_token
from tg_notify.core.exceptions import TelegramConfigError


@pytest.fixture(autouse=True)
def _no_dotenv(monkeypatch):
    # load_dotenv() finds the project-root .env via find_dotenv() (walks up from
    # config.py, NOT cwd), refilling deleted vars with real secrets. Disable it so
    # config tests are controlled purely by env vars / explicit args.
    monkeypatch.setattr(cfg, "_load_dotenv", lambda: None)


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
