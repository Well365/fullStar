"""Device listing and serial resolution."""

import os
import re
from dataclasses import dataclass
from typing import List, Optional

from droid_ctl.core.exceptions import DeviceError
from droid_ctl.core.runner import AdbRunner


@dataclass
class DeviceInfo:
    serial: str
    state: str
    product: Optional[str] = None
    model: Optional[str] = None
    device: Optional[str] = None


def parse_devices(output: str) -> List[DeviceInfo]:
    devices: List[DeviceInfo] = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        serial, state = parts[0], parts[1]
        extra = " ".join(parts[2:]) if len(parts) > 2 else ""
        info = DeviceInfo(serial=serial, state=state)
        for key in ("product", "model", "device"):
            m = re.search(rf"{key}:(\S+)", extra)
            if m:
                setattr(info, key, m.group(1))
        devices.append(info)
    return devices


def list_devices(runner: Optional[AdbRunner] = None) -> List[DeviceInfo]:
    runner = runner or AdbRunner()
    out = runner.run("devices", "-l", capture_output=True, text=True).stdout or ""
    return parse_devices(out)


def resolve_serial(serial: Optional[str] = None, runner: Optional[AdbRunner] = None) -> str:
    if serial:
        serial = serial.strip()
    else:
        serial = (
            os.environ.get("ADB_SERIAL")
            or os.environ.get("ANDROID_SERIAL")
            or ""
        ).strip()

    runner = runner or AdbRunner(serial=serial or None)
    ready = [d for d in list_devices(runner) if d.state == "device"]

    if serial:
        matched = [d for d in ready if d.serial == serial]
        if not matched:
            raise DeviceError(f"device not ready: {serial}")
        return serial

    if not ready:
        raise DeviceError("no device connected (enable USB debugging?)")
    if len(ready) > 1:
        lines = ", ".join(d.serial for d in ready)
        raise DeviceError(f"multiple devices — set ADB_SERIAL: {lines}")
    return ready[0].serial


def screen_size(runner: AdbRunner) -> Optional[str]:
    out = runner.shell("wm size")
    for line in out.splitlines():
        if "Physical size" in line or "Override size" in line:
            return line.split(":")[-1].strip()
    return None
