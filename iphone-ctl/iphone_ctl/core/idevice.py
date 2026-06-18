"""Physical iOS device via libimobiledevice + devicectl (iOS 17+)."""

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from iphone_ctl.core.exceptions import DeviceError, IOSkitError
from iphone_ctl.core.tools import resolve_binary


@dataclass
class IosDevice:
    udid: str


def list_devices() -> List[IosDevice]:
    bin_path = resolve_binary("idevice_id")
    result = subprocess.run(
        [str(bin_path), "-l"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        if "No device found" in stderr or not (result.stdout or "").strip():
            return []
        raise IOSkitError(f"idevice_id failed: {stderr}")
    return [IosDevice(udid=line.strip()) for line in result.stdout.splitlines() if line.strip()]


def _udid_visible_to_xcode(udid: str) -> bool:
    """Fallback when libimobiledevice cannot see iOS 17+ devices over USB."""
    if not shutil.which("xcrun"):
        return False
    result = subprocess.run(
        ["xcrun", "xctrace", "list", "devices"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return False
    return udid in (result.stdout or "")


def resolve_udid(udid: Optional[str] = None) -> str:
    udid = (udid or os.environ.get("IOS_UDID") or os.environ.get("DEVICE_UDID") or "").strip()
    devices = list_devices()
    if udid:
        if any(d.udid == udid for d in devices):
            return udid
        if _udid_visible_to_xcode(udid):
            return udid
        raise DeviceError(f"device not found: {udid}")
    if not devices:
        raise DeviceError("no iOS device connected (USB + trust this computer?)")
    if len(devices) > 1:
        ids = ", ".join(d.udid for d in devices)
        raise DeviceError(f"multiple devices — set IOS_UDID: {ids}")
    return devices[0].udid


def mount_developer_disk_image(udid: str) -> bool:
    """Mount DDI via Xcode devicectl (required for iOS 17+ debugging services)."""
    if not shutil.which("xcrun"):
        return False
    result = subprocess.run(
        [
            "xcrun", "devicectl", "device", "info", "ddiServices",
            "--device", udid,
            "--auto-mount-ddis",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def take_screenshot_idevice(udid: str, output: Path) -> Path:
    mount_developer_disk_image(udid)
    bin_path = resolve_binary("idevicescreenshot")
    output.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [str(bin_path), "-u", udid, str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise IOSkitError(
            (result.stderr or result.stdout or "idevicescreenshot failed").strip()
        )
    if not output.is_file():
        raise IOSkitError("screenshot file not created")
    return output
