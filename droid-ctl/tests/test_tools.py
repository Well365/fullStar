from pathlib import Path
from unittest.mock import patch

import pytest

from droid_ctl.core.tools import ADB_EXE, find_system_platform_tools_dir, repo_vendor_dir


def test_find_from_android_home(tmp_path):
    pt = tmp_path / "platform-tools"
    pt.mkdir()
    (pt / ADB_EXE).write_text("# fake adb")
    with patch.dict("os.environ", {"ANDROID_HOME": str(tmp_path)}, clear=False):
        with patch("droid_ctl.core.tools.shutil.which", return_value=None):
            assert find_system_platform_tools_dir() == pt.resolve()


def test_repo_vendor_dir_real():
    vendor = repo_vendor_dir()
    assert vendor is not None
    assert (vendor / ADB_EXE).is_file()


def test_resolve_prefers_repo_vendor(tmp_path):
    from droid_ctl.core.adb_path import resolve_adb_path

    vendor = repo_vendor_dir()
    assert vendor is not None
    with patch.dict("os.environ", {}, clear=True):
        path = resolve_adb_path(auto_install=False)
    assert path == vendor / ADB_EXE
