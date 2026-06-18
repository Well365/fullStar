from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class MessageResult:
    """Result of a successful Telegram API call."""

    chat_id: int
    message_id: Optional[int] = None
    raw: Any = None
