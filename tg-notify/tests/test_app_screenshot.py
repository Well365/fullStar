import pytest

from tg_notify.core.exceptions import ScreenshotError
from tg_notify.core.screenshot import _canonical_app_name, _resolve_app_target


def test_resolve_app_target_by_name():
    launch, activate, proc = _resolve_app_target("Safari", None, None, None)
    assert launch == ["open", "-a", "Safari"]
    assert activate == "Safari"
    assert proc == "Safari"


def test_resolve_app_target_normalizes_case_from_applications():
    launch, activate, proc = _resolve_app_target("telegram", None, None, None)
    assert launch == ["open", "-a", "Telegram"]
    assert activate == "Telegram"
    assert proc == "Telegram"


def test_resolve_app_target_by_path():
    launch, activate, proc = _resolve_app_target(
        None,
        "/Applications/Calculator.app",
        None,
        None,
    )
    assert launch == ["open", "/Applications/Calculator.app"]
    assert activate == "Calculator"
    assert proc == "Calculator"


def test_resolve_app_target_requires_one_selector():
    with pytest.raises(ScreenshotError):
        _resolve_app_target(None, None, None, None)


from tg_notify.core.exceptions import ScreenshotError
from tg_notify.core.screenshot import _window_id_unsupported


def test_window_id_unsupported_detects_1728():
    exc = ScreenshotError('Could not get window id: (-1728)')
    assert _window_id_unsupported(exc)


def test_window_id_unsupported_detects_chinese_message():
    exc = ScreenshotError('不能获得 id of window 1')
    assert _window_id_unsupported(exc)
