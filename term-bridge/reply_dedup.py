"""Similarity-based dedup for assistant replies sent to Telegram.

`new_content_since` only compares a candidate against the immediately-previous
send and only strips a contiguous overlap. A reply that repeats info already
sent a few messages earlier (non-consecutive, reordered, or re-emitted in full)
still reaches Telegram twice. This module keeps a rolling buffer of the last
`BUFFER_CAP` sent messages and reports a candidate as a duplicate when it is
>= `DEFAULT_THRESHOLD` similar to ANY buffered message — so the caller can skip
the send.

Mirrors the screenshot_dedup approach (persist the fingerprint of what was
actually sent; compare the next candidate before sending). Text is normalized
(whitespace collapsed, blank lines dropped) so terminal reflow doesn't change
the similarity score. Similarity is difflib's ratio in [0, 1].
"""
from __future__ import annotations

import json
import os
from difflib import SequenceMatcher
from pathlib import Path

BUFFER_CAP = 15
DEFAULT_THRESHOLD = 0.95


def normalize(text: str) -> str:
    """Collapse internal whitespace per line and drop blank lines."""
    lines = []
    for raw in text.splitlines():
        collapsed = " ".join(raw.split())
        if collapsed:
            lines.append(collapsed)
    return "\n".join(lines)


def similarity(a: str, b: str) -> float:
    """Ratio in [0, 1] of how similar two strings are (difflib)."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def is_duplicate(
    candidate: str, buffer: list[str], threshold: float = DEFAULT_THRESHOLD
) -> bool:
    """True when `candidate` is >= `threshold` similar to any buffered message.

    `candidate` is normalized here; buffer entries are stored already-normalized.
    """
    norm = normalize(candidate)
    if not norm:
        return False
    return any(similarity(norm, prev) >= threshold for prev in buffer)


def read_buffer(path: Path) -> list[str]:
    """Load the rolling buffer; missing/corrupt/invalid → empty list."""
    try:
        raw = path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return []
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(data, list):
        return []
    return [s for s in data if isinstance(s, str)]


def append_buffer(path: Path, text: str, cap: int = BUFFER_CAP) -> list[str]:
    """Append `normalize(text)` to the buffer, keep the last `cap`, atomic write."""
    buf = read_buffer(path)
    buf.append(normalize(text))
    buf = buf[-cap:]
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(buf, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)
    return buf
