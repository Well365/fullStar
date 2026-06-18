from pathlib import Path
from typing import Optional, Union

from tg_notify.core.client import TelegramClient
from tg_notify.core.screenshot import ScreenshotMode, capture_app_window, capture_screenshot
from tg_notify.core.types import MessageResult

ChatId = Union[int, str]


class Notify:
    """High-level notify API for scripts and build pipelines."""

    def __init__(
        self,
        token: Optional[str] = None,
        default_chat_id: Optional[ChatId] = None,
        config_path: Optional[str] = None,
    ):
        self._token = token
        self._default_chat_id = default_chat_id
        self._config_path = config_path
        self._client: Optional[TelegramClient] = None

    def _get_client(self) -> TelegramClient:
        if self._client is None:
            self._client = TelegramClient(
                token=self._token,
                default_chat_id=self._default_chat_id,
                config_path=self._config_path,
            )
        return self._client

    def text(self, message: str, chat_id: Optional[ChatId] = None, **kwargs) -> MessageResult:
        return self._get_client().send_text(message, chat_id=chat_id, **kwargs)

    def file(
        self,
        file_path: Union[str, Path],
        chat_id: Optional[ChatId] = None,
        **kwargs,
    ) -> MessageResult:
        return self._get_client().send_document(file_path, chat_id=chat_id, **kwargs)

    def photo(
        self,
        file_path: Union[str, Path],
        chat_id: Optional[ChatId] = None,
        caption: Optional[str] = None,
        **kwargs,
    ) -> MessageResult:
        return self._get_client().send_photo(
            file_path,
            chat_id=chat_id,
            caption=caption,
            **kwargs,
        )

    def screenshot(
        self,
        chat_id: Optional[ChatId] = None,
        caption: Optional[str] = None,
        mode: ScreenshotMode = "full",
        output_path: Optional[Union[str, Path]] = None,
        delete_after_send: bool = True,
        **kwargs,
    ) -> MessageResult:
        path = capture_screenshot(output_path=output_path, mode=mode)
        try:
            return self.photo(path, chat_id=chat_id, caption=caption, **kwargs)
        finally:
            if delete_after_send and output_path is None and path.is_file():
                path.unlink(missing_ok=True)

    def app_screenshot(
        self,
        app: Optional[str] = None,
        chat_id: Optional[ChatId] = None,
        caption: Optional[str] = None,
        app_path: Optional[Union[str, Path]] = None,
        bundle_id: Optional[str] = None,
        process_name: Optional[str] = None,
        wait_seconds: float = 2.0,
        window_index: int = 1,
        no_shadow: bool = False,
        output_path: Optional[Union[str, Path]] = None,
        delete_after_send: bool = True,
        **kwargs,
    ) -> MessageResult:
        path = capture_app_window(
            app=app,
            app_path=app_path,
            bundle_id=bundle_id,
            process_name=process_name,
            wait_seconds=wait_seconds,
            window_index=window_index,
            no_shadow=no_shadow,
            output_path=output_path,
        )
        try:
            return self.photo(path, chat_id=chat_id, caption=caption, **kwargs)
        finally:
            if delete_after_send and output_path is None and path.is_file():
                path.unlink(missing_ok=True)


class _LazyNotify:
    """Defer TelegramClient creation until the first send call."""

    def __init__(self):
        self._notify: Optional[Notify] = None

    def _get(self) -> Notify:
        if self._notify is None:
            self._notify = Notify()
        return self._notify

    def text(self, message: str, chat_id: Optional[ChatId] = None, **kwargs) -> MessageResult:
        return self._get().text(message, chat_id=chat_id, **kwargs)

    def file(
        self,
        file_path: Union[str, Path],
        chat_id: Optional[ChatId] = None,
        **kwargs,
    ) -> MessageResult:
        return self._get().file(file_path, chat_id=chat_id, **kwargs)

    def photo(
        self,
        file_path: Union[str, Path],
        chat_id: Optional[ChatId] = None,
        caption: Optional[str] = None,
        **kwargs,
    ) -> MessageResult:
        return self._get().photo(
            file_path,
            chat_id=chat_id,
            caption=caption,
            **kwargs,
        )

    def screenshot(
        self,
        chat_id: Optional[ChatId] = None,
        caption: Optional[str] = None,
        mode: ScreenshotMode = "full",
        output_path: Optional[Union[str, Path]] = None,
        delete_after_send: bool = True,
        **kwargs,
    ) -> MessageResult:
        return self._get().screenshot(
            chat_id=chat_id,
            caption=caption,
            mode=mode,
            output_path=output_path,
            delete_after_send=delete_after_send,
            **kwargs,
        )

    def app_screenshot(
        self,
        app: Optional[str] = None,
        chat_id: Optional[ChatId] = None,
        caption: Optional[str] = None,
        app_path: Optional[Union[str, Path]] = None,
        bundle_id: Optional[str] = None,
        process_name: Optional[str] = None,
        wait_seconds: float = 2.0,
        window_index: int = 1,
        no_shadow: bool = False,
        output_path: Optional[Union[str, Path]] = None,
        delete_after_send: bool = True,
        **kwargs,
    ) -> MessageResult:
        return self._get().app_screenshot(
            app=app,
            chat_id=chat_id,
            caption=caption,
            app_path=app_path,
            bundle_id=bundle_id,
            process_name=process_name,
            wait_seconds=wait_seconds,
            window_index=window_index,
            no_shadow=no_shadow,
            output_path=output_path,
            delete_after_send=delete_after_send,
            **kwargs,
        )


notify = _LazyNotify()
