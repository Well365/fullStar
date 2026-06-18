"""High-level iOS device: screenshot (idevice) + tap/swipe (WDA)."""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from iphone_ctl.core.exceptions import IOSkitError
from iphone_ctl.core.idevice import resolve_udid, take_screenshot_idevice
from iphone_ctl.core.wda import WdaClient


def default_shot_dir() -> Path:
    path = Path(os.environ.get("IOS_SHOT_DIR", "/tmp/ioskit"))
    path.mkdir(parents=True, exist_ok=True)
    return path


class IOSDevice:
    """Real device: libimobiledevice screenshot + WDA coordinate control."""

    def __init__(
        self,
        udid: Optional[str] = None,
        wda_url: Optional[str] = None,
        bundle_id: Optional[str] = None,
    ):
        self.udid = resolve_udid(udid)
        self.wda = WdaClient(base_url=wda_url, bundle_id=bundle_id)

    def screenshot(self, output: Optional[Path] = None, via_wda: bool = False) -> Path:
        out = output or default_shot_dir() / f"{datetime.now():%Y%m%d_%H%M%S}.png"
        out.parent.mkdir(parents=True, exist_ok=True)

        if via_wda or os.environ.get("IOS_SHOT_VIA_WDA") == "1":
            out.write_bytes(self.wda.screenshot_png())
            return out

        try:
            return take_screenshot_idevice(self.udid, out)
        except IOSkitError as idevice_err:
            if self.wda.is_ready():
                out.write_bytes(self.wda.screenshot_png())
                return out
            raise IOSkitError(
                f"screenshot failed ({idevice_err}). "
                "iOS 17+ options: (1) start WDA + ./mob-compose/ios-start, "
                "(2) sudo pymobiledevice3 remote tunneld"
            ) from idevice_err

    def tap(self, x: int, y: int, bundle_id: Optional[str] = None) -> None:
        self.wda.tap(x, y, bundle_id=bundle_id)

    def swipe(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        duration: float = 0.3,
        bundle_id: Optional[str] = None,
    ) -> None:
        self.wda.swipe(x1, y1, x2, y2, duration=duration, bundle_id=bundle_id)

    def wda_status(self) -> Dict[str, Any]:
        return self.wda.status()

    def info_dict(self, shot_path: Optional[Path] = None) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "ok": True,
            "udid": self.udid,
            "wda_url": self.wda.base_url,
            "wda_ready": self.wda.is_ready(),
        }
        if shot_path:
            data["path"] = str(shot_path.resolve())
            data["bytes"] = shot_path.stat().st_size
        return data

    def analyze(self, via_wda_shot: bool = False) -> Dict[str, Any]:
        shot = self.screenshot(via_wda=via_wda_shot)
        return self.info_dict(shot)
