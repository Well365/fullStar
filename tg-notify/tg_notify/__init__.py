"""tgkit — Telegram notify toolkit."""

from tg_notify.notify.sender import Notify, notify


def text(message: str, chat_id=None, **kwargs):
    """Send text using .env / config defaults."""
    return notify.text(message, chat_id=chat_id, **kwargs)


def file(file_path, chat_id=None, **kwargs):
    """Send a file using .env / config defaults."""
    return notify.file(file_path, chat_id=chat_id, **kwargs)


def photo(file_path, chat_id=None, caption=None, **kwargs):
    """Send an image with inline preview."""
    return notify.photo(file_path, chat_id=chat_id, caption=caption, **kwargs)


def screenshot(chat_id=None, caption=None, mode="full", **kwargs):
    """Capture the screen (macOS) and send as a photo."""
    return notify.screenshot(chat_id=chat_id, caption=caption, mode=mode, **kwargs)


def app_screenshot(app=None, chat_id=None, caption=None, **kwargs):
    """Open an app (macOS), capture its window, and send as a photo."""
    return notify.app_screenshot(app=app, chat_id=chat_id, caption=caption, **kwargs)


__all__ = ["Notify", "notify", "text", "file", "photo", "screenshot", "app_screenshot"]
__version__ = "0.1.2"
