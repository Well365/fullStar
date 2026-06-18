"""Bundled platform-tools in repo vendor/; network download is update-only."""

import os
import platform
import shutil
import stat
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional

from droid_ctl.core.exceptions import AdbkitError

_PLATFORM_URLS = {
    "Darwin": "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip",
    "Linux": "https://dl.google.com/android/repository/platform-tools-latest-linux.zip",
    "Windows": "https://dl.google.com/android/repository/platform-tools-latest-windows.zip",
}

_PLATFORM_VENDOR_NAMES = {
    "Darwin": "platform-tools-darwin",
    "Linux": "platform-tools-linux",
    "Windows": "platform-tools-windows",
}

ADB_EXE = "adb.exe" if sys.platform == "win32" else "adb"


def package_root() -> Path:
    """adbkit git repo root (parent of Python package directory)."""
    return Path(__file__).resolve().parents[2]


def vendor_root() -> Path:
    return package_root() / "vendor"


def default_home() -> Path:
    return Path(os.environ.get("ADBKIT_HOME", Path.home() / ".adbkit"))


def platform_tools_dir(home: Optional[Path] = None) -> Path:
    return (home or default_home()) / "platform-tools"


def bundled_adb_path(home: Optional[Path] = None) -> Path:
    return platform_tools_dir(home) / ADB_EXE


def _adb_in_dir(directory: Path) -> bool:
    return (directory / ADB_EXE).is_file()


def is_installed(home: Optional[Path] = None) -> bool:
    path = bundled_adb_path(home)
    return path.is_file() and os.access(path, os.X_OK)


def repo_vendor_candidates() -> list[Path]:
    """Vendor dirs shipped with git clone (platform-specific then generic)."""
    root = vendor_root()
    system = platform.system()
    names = []
    tagged = _PLATFORM_VENDOR_NAMES.get(system)
    if tagged:
        names.append(tagged)
    names.append("platform-tools")
    return [root / name for name in names]


def repo_vendor_dir() -> Optional[Path]:
    """platform-tools directory bundled in this git repo (offline default)."""
    for directory in repo_vendor_candidates():
        if _adb_in_dir(directory):
            return directory.resolve()
    return None


def repo_vendor_adb_path() -> Optional[Path]:
    vendor = repo_vendor_dir()
    if vendor is None:
        return None
    return vendor / ADB_EXE


def find_system_platform_tools_dir() -> Optional[Path]:
    """Optional fallback: machine-wide Android SDK (not used for install default)."""
    candidates: list[Path] = []
    for var in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        sdk = os.environ.get(var)
        if sdk:
            candidates.append(Path(sdk).expanduser() / "platform-tools")
    which = shutil.which("adb")
    if which:
        parent = Path(which).expanduser().resolve().parent
        if parent.name == "platform-tools":
            candidates.insert(0, parent)
    for raw in candidates:
        if _adb_in_dir(raw):
            return raw.resolve()
    return None


def _ensure_executable(dest: Path) -> None:
    if sys.platform == "win32":
        return
    for name in ("adb", "fastboot"):
        bin_path = dest / name
        if bin_path.is_file():
            bin_path.chmod(bin_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _copy_tree(source: Path, dest: Path) -> None:
    source = source.resolve()
    if not _adb_in_dir(source):
        raise AdbkitError(f"not a platform-tools directory: {source}")
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, dest, symlinks=True)
    _ensure_executable(dest)


def copy_platform_tools(source: Path, home: Optional[Path] = None) -> Path:
    """Copy platform-tools into ~/.droid-ctl/platform-tools/."""
    home = home or default_home()
    dest = platform_tools_dir(home)
    adb_path = bundled_adb_path(home)
    if dest.resolve() == source.resolve():
        return adb_path
    _copy_tree(source, dest)
    if not adb_path.is_file():
        raise AdbkitError(f"copy failed: {adb_path} missing")
    return adb_path


def copy_repo_vendor_to(home: Optional[Path] = None) -> Path:
    vendor = repo_vendor_dir()
    if vendor is None:
        raise AdbkitError(
            "no bundled platform-tools in vendor/. "
            "Clone droid-ctl with vendor/ or run: droid-ctl install-tools --download"
        )
    print(f"adbkit: copying bundled vendor from {vendor}", file=sys.stderr)
    return copy_platform_tools(vendor, home=home)


def download_url() -> str:
    system = platform.system()
    url = _PLATFORM_URLS.get(system)
    if not url:
        raise AdbkitError(f"Unsupported platform for download: {system}")
    return url


def download_platform_tools(
    home: Optional[Path] = None,
    *,
    into_vendor: bool = False,
) -> Path:
    """Download platform-tools from Google (update option only)."""
    if into_vendor:
        system = platform.system()
        tagged = _PLATFORM_VENDOR_NAMES.get(system, "platform-tools")
        dest = vendor_root() / tagged
        adb_path = dest / ADB_EXE
    else:
        home = home or default_home()
        dest = platform_tools_dir(home)
        adb_path = bundled_adb_path(home)

    url = download_url()
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "platform-tools.zip"
        print(f"adbkit: downloading platform-tools from {url}", file=sys.stderr)
        urllib.request.urlretrieve(url, zip_path)
        extract_root = Path(tmp) / "extract"
        extract_root.mkdir()
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(extract_root)
        src = extract_root / "platform-tools"
        if not src.is_dir():
            raise AdbkitError("Unexpected platform-tools zip layout")
        _copy_tree(src, dest)

    if not adb_path.is_file():
        raise AdbkitError(f"download failed: {adb_path} missing")
    return adb_path


def install_platform_tools(
    home: Optional[Path] = None,
    force: bool = False,
    force_download: bool = False,
    update_vendor: bool = False,
) -> Path:
    """
    Install platform-tools into ~/.droid-ctl/platform-tools/.

    Default: copy from git repo vendor/ (offline).
    --download: fetch from Google (update ~/.adbkit or vendor/ with --update-vendor).
    """
    home = home or default_home()
    adb_path = bundled_adb_path(home)

    if is_installed(home) and not force and not force_download:
        return adb_path

    if force_download:
        if update_vendor:
            path = download_platform_tools(into_vendor=True)
            print(f"adbkit: vendor updated → {path}", file=sys.stderr)
            return path
        download_platform_tools(home=home)
        print(f"adbkit: updated → {adb_path}", file=sys.stderr)
        return adb_path

    return copy_repo_vendor_to(home=home)
