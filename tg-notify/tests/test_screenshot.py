import platform
from unittest.mock import MagicMock, patch

import pytest

from tg_notify.core.exceptions import ScreenshotError
from tg_notify.core.screenshot import capture_screenshot, _as_applescript_literal


def test_capture_screenshot_unsupported_platform(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    with pytest.raises(ScreenshotError, match="only supported on macOS"):
        capture_screenshot()


def test_applescript_literal_escapes_quote_and_backslash():
    assert _as_applescript_literal('a"b') == '"a\\"b"'
    assert _as_applescript_literal("a\\b") == '"a\\\\b"'
    assert _as_applescript_literal("iTerm") == '"iTerm"'


def test_applescript_literal_blocks_process_name_injection():
    # a process_name trying to break out of the literal stays contained
    evil = 'X" to activate\ntell application "Finder" to quit\n--'
    lit = _as_applescript_literal(evil)
    assert lit.startswith('"') and lit.endswith('"')
    assert "\n" not in lit  # newlines escaped, can't split the source line
    # every quote inside the literal is escaped → no unescaped breakout
    assert '"' not in lit[1:-1].replace('\\"', '')


def test_capture_screenshot_success(tmp_path):
    output = tmp_path / "shot.png"
    output.write_bytes(b"fake")

    with patch("tg_notify.core.screenshot.subprocess.run") as run:
        with patch("tg_notify.core.screenshot.platform.system", return_value="Darwin"):
            path = capture_screenshot(output_path=output)

    assert path == output
    run.assert_called_once()
    assert run.call_args.args[0][-1] == str(output)
