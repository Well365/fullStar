import pytest

from droid_ctl.core.device import parse_devices


SAMPLE = """List of devices attached
ABC123\tdevice product:foo model:Pixel_6 device:oriole transport_id:1
emulator-5554\toffline
"""


def test_parse_devices():
    devices = parse_devices(SAMPLE)
    assert len(devices) == 2
    assert devices[0].serial == "ABC123"
    assert devices[0].state == "device"
    assert devices[0].model == "Pixel_6"
    assert devices[1].state == "offline"


def test_key_map_import():
    from droid_ctl.ops.device import KEY_MAP

    assert KEY_MAP["HOME"] == 3
    assert KEY_MAP["BACK"] == 4
