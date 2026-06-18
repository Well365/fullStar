import asyncio
import inspect
from pathlib import Path
from typing import Any, Optional, Union

import telegram

from tg_notify.core.config import ChatId, resolve_chat_id, resolve_token
from tg_notify.core.exceptions import TelegramSendError
from tg_notify.core.types import MessageResult


def _run_telegram_call(result: Any) -> Any:
    """python-telegram-bot v20+ returns coroutines; v12 returns Message directly."""
    if inspect.isawaitable(result):
        return asyncio.run(result)
    return result


class TelegramClient:
    """Thin wrapper around python-telegram-bot for outbound messages."""

    def __init__(
        self,
        token: Optional[str] = None,
        default_chat_id: Optional[ChatId] = None,
        config_path: Optional[str] = None,
    ):
        self._token = resolve_token(token)
        self._default_chat_id = default_chat_id
        self._config_path = config_path
        self._bot = telegram.Bot(token=self._token)

    def _target_chat_id(self, chat_id: Optional[ChatId] = None) -> int:
        return resolve_chat_id(
            chat_id=chat_id if chat_id is not None else self._default_chat_id,
            config_path=self._config_path,
        )

    def send_text(
        self,
        text: str,
        chat_id: Optional[ChatId] = None,
        **kwargs,
    ) -> MessageResult:
        target = self._target_chat_id(chat_id)
        try:
            message = _run_telegram_call(
                self._bot.send_message(chat_id=target, text=text, **kwargs)
            )
        except Exception as exc:
            raise TelegramSendError(f"Failed to send text to chat {target}: {exc}") from exc
        return MessageResult(
            chat_id=target,
            message_id=getattr(message, "message_id", None),
            raw=message,
        )

    def send_document(
        self,
        file_path: Union[str, Path],
        chat_id: Optional[ChatId] = None,
        **kwargs,
    ) -> MessageResult:
        target = self._target_chat_id(chat_id)
        path = Path(file_path)
        if not path.is_file():
            raise TelegramSendError(f"Document not found: {path}")

        try:
            with open(path, "rb") as handle:
                message = _run_telegram_call(
                    self._bot.send_document(
                        chat_id=target,
                        document=handle,
                        filename=path.name,
                        **kwargs,
                    )
                )
        except TelegramSendError:
            raise
        except Exception as exc:
            raise TelegramSendError(
                f"Failed to send document {path} to chat {target}: {exc}"
            ) from exc

        return MessageResult(
            chat_id=target,
            message_id=getattr(message, "message_id", None),
            raw=message,
        )

    def send_photo(
        self,
        file_path: Union[str, Path],
        chat_id: Optional[ChatId] = None,
        caption: Optional[str] = None,
        **kwargs,
    ) -> MessageResult:
        target = self._target_chat_id(chat_id)
        path = Path(file_path)
        if not path.is_file():
            raise TelegramSendError(f"Photo not found: {path}")

        try:
            with open(path, "rb") as handle:
                message = _run_telegram_call(
                    self._bot.send_photo(
                        chat_id=target,
                        photo=handle,
                        caption=caption,
                        **kwargs,
                    )
                )
        except TelegramSendError:
            raise
        except Exception as exc:
            raise TelegramSendError(
                f"Failed to send photo {path} to chat {target}: {exc}"
            ) from exc

        return MessageResult(
            chat_id=target,
            message_id=getattr(message, "message_id", None),
            raw=message,
        )
