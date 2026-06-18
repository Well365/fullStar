"""adbkit — Android ADB toolkit with bundled platform-tools installer."""

from droid_ctl.ops.device import Device

_device: Device = None  # type: ignore


def _get_device(serial=None) -> Device:
    global _device
    if serial is not None or _device is None:
        return Device(serial=serial)
    return _device


def screenshot(output=None, serial=None):
    return _get_device(serial).screenshot(output)


def tap(x, y, serial=None):
    _get_device(serial).tap(x, y)


def swipe(x1, y1, x2, y2, duration_ms=300, serial=None):
    _get_device(serial).swipe(x1, y1, x2, y2, duration_ms)


def input_text(text, serial=None):
    _get_device(serial).input_text(text)


def keyevent(key, serial=None):
    _get_device(serial).keyevent(key)


def analyze(with_ui=False, serial=None):
    return _get_device(serial).analyze(with_ui=with_ui)


__all__ = [
    "Device",
    "screenshot",
    "tap",
    "swipe",
    "input_text",
    "keyevent",
    "analyze",
]
__version__ = "0.1.0"
