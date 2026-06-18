"""Resolve libimobiledevice binaries (vendor → PATH → Homebrew)."""

import os
import shutil
from pathlib import Path
from typing import Optional

from iphone_ctl.core.exceptions import ToolNotFoundError

_BINARIES = ("idevice_id", "idevicescreenshot", "iproxy")


def package_root() -> Path:
    return Path(__file__).resolve().parents[2]


def vendor_bin_dir() -> Path:
    return package_root() / "vendor" / "bin"


def resolve_binary(name: str) -> Path:
    explicit = os.environ.get(f"IOSKIT_{name.upper()}")
    if explicit:
        p = Path(explicit).expanduser()
        if p.is_file():
            return p
        raise ToolNotFoundError(f"IOSKIT_{name.upper()} not found: {p}")

    vendor = vendor_bin_dir() / name
    if vendor.is_file():
        return vendor

    which = shutil.which(name)
    if which:
        return Path(which)

    brew = Path(f"/opt/homebrew/bin/{name}")
    if brew.is_file():
        return brew

    raise ToolNotFoundError(
        f"{name} not found. Install: brew install libimobiledevice\n"
        f"  or place binaries in {vendor_bin_dir()}"
    )
