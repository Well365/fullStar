class TgkitError(Exception):
    """Base error for tg_notify."""


class TelegramConfigError(TgkitError):
    """Missing or invalid Telegram configuration."""


class TelegramSendError(TgkitError):
    """Failed to send a Telegram message."""


class ScreenshotError(TgkitError):
    """Failed to capture a screenshot."""
