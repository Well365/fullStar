import platform
from unittest.mock import MagicMock, patch

import pytest

from tg_notify.core.exceptions import ScreenshotError
from tg_notify.core.screenshot import capture_screenshot


def test_capture_screenshot_unsupported_platform(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    with pytest.raises(ScreenshotError, match="only supported on macOS"):
        capture_screenshot()


def test_capture_screenshot_success(tmp_path):
    output = tmp_path / "shot.png"
    output.write_bytes(b"fake")

    with patch("tg_notify.core.screenshot.subprocess.run") as run:
        with patch("tg_notify.core.screenshot.platform.system", return_value="Darwin"):
            path = capture_screenshot(output_path=output)

    assert path == output
    run.assert_called_once()
    assert run.call_args.args[0][-1] == str(output)
