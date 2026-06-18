class AdbkitError(Exception):
    """Base error for droid_ctl."""


class AdbNotFoundError(AdbkitError):
    """adb binary not available."""


class DeviceError(AdbkitError):
    """No device or ambiguous device selection."""
