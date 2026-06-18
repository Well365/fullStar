"""WebDriverAgent HTTP client — coordinate tap/swipe on real device."""

import base64
import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional, Tuple

from iphone_ctl.core.exceptions import WdaError


class WdaClient:
    """
    Talk to WDA on device (usually via iproxy 8100:8100).

  Env:
    IOS_WDA_URL — default http://127.0.0.1:8100
    IOS_WDA_BUNDLE_ID — app bundle for session (optional for coordinate ops)
    """

    def __init__(self, base_url: Optional[str] = None, bundle_id: Optional[str] = None):
        self.base_url = (base_url or os.environ.get("IOS_WDA_URL", "http://127.0.0.1:8100")).rstrip("/")
        self.bundle_id = bundle_id or os.environ.get("IOS_WDA_BUNDLE_ID")
        self._session_id: Optional[str] = None

    def _request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        timeout: float = 30,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        data = None
        headers = {"Content-Type": "application/json"}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8") or "{}"
                return json.loads(raw)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise WdaError(f"WDA HTTP {exc.code} {path}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise WdaError(
                f"cannot reach WDA at {self.base_url}. "
                f"Start WDA on device and run: iproxy 8100 8100 -u $IOS_UDID"
            ) from exc

    def status(self) -> Dict[str, Any]:
        return self._request("GET", "/status")

    def is_ready(self) -> bool:
        try:
            data = self.status()
            return bool(data.get("value", {}).get("ready", data.get("sessionId")))
        except WdaError:
            return False

    def create_session(self, bundle_id: Optional[str] = None) -> str:
        bundle_id = bundle_id or self.bundle_id
        caps: Dict[str, Any] = {}
        if bundle_id:
            caps["bundleId"] = bundle_id
        payload = {"capabilities": {"alwaysMatch": caps, "firstMatch": [caps] if caps else [{}]}}
        data = self._request("POST", "/session", payload)
        session_id = data.get("sessionId") or data.get("value", {}).get("sessionId")
        if not session_id and isinstance(data.get("value"), dict):
            session_id = data["value"].get("sessionId")
        if not session_id:
            raise WdaError(f"no sessionId in WDA response: {data}")
        self._session_id = session_id
        return session_id

    def ensure_session(self, bundle_id: Optional[str] = None) -> str:
        if self._session_id:
            return self._session_id
        return self.create_session(bundle_id=bundle_id)

    def delete_session(self) -> None:
        if not self._session_id:
            return
        try:
            self._request("DELETE", f"/session/{self._session_id}")
        finally:
            self._session_id = None

    def tap(self, x: int, y: int, bundle_id: Optional[str] = None) -> None:
        sid = self.ensure_session(bundle_id=bundle_id)
        self._request("POST", f"/session/{sid}/wda/tap", {"x": float(x), "y": float(y)})

    def swipe(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        duration: float = 0.3,
        bundle_id: Optional[str] = None,
    ) -> None:
        sid = self.ensure_session(bundle_id=bundle_id)
        self._request(
            "POST",
            f"/session/{sid}/wda/dragfromtoforduration",
            {
                "fromX": float(x1),
                "fromY": float(y1),
                "toX": float(x2),
                "toY": float(y2),
                "duration": float(duration),
            },
        )

    def screenshot_png(self) -> bytes:
        """WDA screenshot (base64 PNG). Fallback when idevicescreenshot unavailable."""
        sid = self.ensure_session()
        data = self._request("GET", f"/session/{sid}/screenshot")
        b64 = data.get("value") or data.get("sessionId")
        if isinstance(data.get("value"), str):
            b64 = data["value"]
        if not b64 or not isinstance(b64, str):
            raise WdaError(f"unexpected screenshot response: {data}")
        return base64.b64decode(b64)
