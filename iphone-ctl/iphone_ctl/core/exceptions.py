class IOSkitError(Exception):
    """Base error."""


class DeviceError(IOSkitError):
    """No device or bad UDID."""


class ToolNotFoundError(IOSkitError):
    """libimobiledevice binary missing."""


class WdaError(IOSkitError):
    """WebDriverAgent HTTP error."""
