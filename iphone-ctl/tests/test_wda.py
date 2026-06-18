import json
from unittest.mock import MagicMock, patch

import pytest

from iphone_ctl.core.wda import WdaClient


def test_wda_tap_builds_request():
    client = WdaClient(base_url="http://127.0.0.1:8100")
    client._session_id = "ABC-123"
    with patch.object(client, "_request") as mock_req:
        client.tap(100, 200)
        mock_req.assert_called_once_with(
            "POST",
            "/session/ABC-123/wda/tap",
            {"x": 100.0, "y": 200.0},
        )


def test_wda_swipe():
    client = WdaClient(base_url="http://127.0.0.1:8100")
    client._session_id = "S1"
    with patch.object(client, "_request") as mock_req:
        client.swipe(10, 20, 30, 40, duration=0.5)
        args = mock_req.call_args[0]
        assert args[0] == "POST"
        assert "dragfromtoforduration" in args[1]
