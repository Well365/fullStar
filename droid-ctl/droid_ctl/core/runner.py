"""Subprocess wrapper around adb."""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Union

from droid_ctl.core.adb_path import resolve_adb_path
from droid_ctl.core.exceptions import AdbkitError

BytesOrStr = Union[bytes, str]


class AdbRunner:
    def __init__(self, serial: Optional[str] = None, adb_path: Optional[Path] = None):
        self._adb_path = adb_path
        self._serial = serial or os.environ.get("ADB_SERIAL") or os.environ.get("ANDROID_SERIAL")

    @property
    def adb(self) -> Path:
        if self._adb_path is None:
            self._adb_path = resolve_adb_path()
        return self._adb_path

    def base_cmd(self) -> List[str]:
        cmd = [str(self.adb)]
        if self._serial:
            cmd.extend(["-s", self._serial])
        return cmd

    def run(
        self,
        *args: str,
        check: bool = True,
        capture_output: bool = False,
        text: bool = False,
        timeout: Optional[float] = None,
        input_data: Optional[bytes] = None,
    ) -> subprocess.CompletedProcess:
        cmd = self.base_cmd() + list(args)
        try:
            return subprocess.run(
                cmd,
                check=check,
                capture_output=capture_output,
                text=text,
                timeout=timeout,
                input=input_data,
            )
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            raise AdbkitError(f"adb failed ({exc.returncode}): {' '.join(cmd)}\n{stderr}") from exc
        except FileNotFoundError as exc:
            raise AdbkitError(f"adb binary missing: {self.adb}") from exc

    def run_bytes(self, *args: str, timeout: Optional[float] = 60) -> bytes:
        result = self.run(*args, capture_output=True, timeout=timeout)
        assert result.stdout is not None
        return result.stdout

    def shell(self, command: str, timeout: Optional[float] = 60) -> str:
        result = self.run("shell", command, capture_output=True, text=True, timeout=timeout)
        return (result.stdout or "").strip()
