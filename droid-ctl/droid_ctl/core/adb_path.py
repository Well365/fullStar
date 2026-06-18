"""Resolve adb binary: env → repo vendor → ~/.adbkit → system SDK (no auto-download)."""

import os
import shutil
from pathlib import Path

from droid_ctl.core.exceptions import AdbNotFoundError
from droid_ctl.core.tools import (
    bundled_adb_path,
    is_installed,
    repo_vendor_adb_path,
)


def resolve_adb_path(auto_install: bool = True) -> Path:
    """
    Resolution order:
    1. ADBKIT_ADB_PATH
    2. droid-ctl/vendor/platform-tools/adb  (shipped with git clone — offline)
    3. ~/.droid-ctl/platform-tools/adb
    4. ANDROID_HOME / PATH adb (optional machine fallback)
    5. copy vendor → ~/.adbkit if auto_install (still offline)

    Network download is NOT automatic; use: droid-ctl install-tools --download
    """
    explicit = os.environ.get("ADBKIT_ADB_PATH")
    if explicit:
        path = Path(explicit).expanduser()
        if path.is_file():
            return path
        raise AdbNotFoundError(f"ADBKIT_ADB_PATH not found: {path}")

    vendor_adb = repo_vendor_adb_path()
    if vendor_adb is not None:
        return vendor_adb

    if is_installed():
        return bundled_adb_path()

    for var in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        sdk = os.environ.get(var)
        if sdk:
            candidate = Path(sdk) / "platform-tools" / ("adb.exe" if os.name == "nt" else "adb")
            if candidate.is_file():
                return candidate

    which = shutil.which("adb")
    if which:
        return Path(which)

    if auto_install:
        from droid_ctl.core.tools import copy_repo_vendor_to

        return copy_repo_vendor_to()

    raise AdbNotFoundError(
        "adb not found. Ensure vendor/platform-tools is in the droid-ctl repo, "
        "or run: droid-ctl install-tools --download"
    )
