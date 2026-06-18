from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from droid_ctl.core.adb_path import resolve_adb_path
from droid_ctl.core.exceptions import AdbNotFoundError


def test_resolve_explicit_path(tmp_path):
    adb = tmp_path / "adb"
    adb.write_text("#!/bin/sh\necho adb\n")
    adb.chmod(0o755)
    with patch.dict("os.environ", {"ADBKIT_ADB_PATH": str(adb)}, clear=False):
        assert resolve_adb_path(auto_install=False) == adb


def test_resolve_missing_explicit():
    with patch.dict("os.environ", {"ADBKIT_ADB_PATH": "/nonexistent/adb"}, clear=False):
        with pytest.raises(AdbNotFoundError):
            resolve_adb_path(auto_install=False)
