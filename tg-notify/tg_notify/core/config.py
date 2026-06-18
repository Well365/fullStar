import json
import os
from pathlib import Path
from typing import Optional, Union

from tg_notify.core.exceptions import TelegramConfigError

ChatId = Union[int, str]


def _load_dotenv() -> None:
    """Load .env from cwd when python-dotenv is available."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def resolve_token(token: Optional[str] = None) -> str:
    _load_dotenv()
    value = token or os.environ.get("TELEGRAM_BOT_TOKEN")
    if not value:
        raise TelegramConfigError(
            "TELEGRAM_BOT_TOKEN is not set. "
            "Export it or add it to a .env file in the project root."
        )
    return value.strip()


def resolve_chat_id(
    chat_id: Optional[ChatId] = None,
    config_path: Optional[str] = None,
) -> int:
    _load_dotenv()

    if chat_id is not None:
        return int(chat_id)

    env_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if env_chat_id:
        return int(env_chat_id.strip())

    path = Path(config_path or os.environ.get("TGKIT_CONFIG_PATH", "config.json"))
    if path.is_file():
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        stored = data.get("chat_id")
        if stored is not None:
            return int(stored)

    raise TelegramConfigError(
        "Telegram chat_id is not set. Pass chat_id, set TELEGRAM_CHAT_ID, "
        "or add chat_id to config.json / TGKIT_CONFIG_PATH."
    )
