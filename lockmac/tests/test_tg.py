"""Tests for lockmac.tg pure logic (no network)."""
from lockmac import tg


def test_menu_includes_core_commands():
    cmds = [c for c, _ in tg._MENU]
    for c in ("veil", "unveil", "lock", "status", "deadman", "purge"):
        assert c in cmds


def test_parse_command_known():
    assert tg.parse_command("/veil") == "veil"
    assert tg.parse_command("/unveil") == "unveil"
    assert tg.parse_command("/lock") == "syslock"   # real system lock
    assert tg.parse_command("/status") == "status"


def test_parse_command_with_botname_suffix():
    assert tg.parse_command("/lock@MyBot") == "syslock"


def test_parse_command_case_and_whitespace():
    assert tg.parse_command("  /VEIL  ") == "veil"


def test_parse_command_unknown():
    assert tg.parse_command("/foo") is None
    assert tg.parse_command("hello") is None
    assert tg.parse_command("") is None


def test_extract_chat_id_latest():
    updates = {"result": [
        {"message": {"chat": {"id": 111}}},
        {"message": {"chat": {"id": 222}}},
    ]}
    assert tg.extract_chat_id(updates) == "222"


def test_extract_chat_id_empty():
    assert tg.extract_chat_id({"result": []}) is None
    assert tg.extract_chat_id({}) is None


def test_set_tg_roundtrip(tmp_path, monkeypatch):
    from lockmac import core
    monkeypatch.setattr(core, "CONFIG", tmp_path / "config.json")
    tg.set_tg("123:ABC", "999")
    cfg = core.load_config()
    assert cfg["tg_token"] == "123:ABC"
    assert cfg["tg_chat"] == "999"


def test_dispatch_unveil_wrong_totp_refused(tmp_path, monkeypatch):
    from lockmac import core, totp
    monkeypatch.setattr(core, "CONFIG", tmp_path / "config.json")
    core.set_totp_secret(totp.generate_secret())
    assert "二步验证码" in tg._dispatch("unveil", ["000000"])


def test_dispatch_deadman_config_via_tg(tmp_path, monkeypatch):
    from lockmac import core
    monkeypatch.setattr(core, "CONFIG", tmp_path / "config.json")
    out = tg._dispatch("deadman", ["0", "0", "purge", "3600"])
    assert "已更新" in out
    assert core.heartbeat_cfg() == (0, 0, "purge", 3600)


def test_dispatch_deadman_show_via_tg(tmp_path, monkeypatch):
    from lockmac import core
    monkeypatch.setattr(core, "CONFIG", tmp_path / "config.json")
    assert "dead-man" in tg._dispatch("deadman", [])


def test_dispatch_purge_add_via_tg(tmp_path, monkeypatch):
    from lockmac import core
    monkeypatch.setattr(core, "CONFIG", tmp_path / "config.json")
    out = tg._dispatch("purgecfg", ["add", str(tmp_path / "x")])
    assert "已加入" in out
    assert str(tmp_path / "x") in core.get_purge_dirs()


def test_dispatch_purge_add_rejects_system_via_tg(tmp_path, monkeypatch):
    from lockmac import core
    monkeypatch.setattr(core, "CONFIG", tmp_path / "config.json")
    assert "拒绝" in tg._dispatch("purgecfg", ["add", "/System/x"])


def test_install_tg_agent_refuses_without_creds(tmp_path, monkeypatch):
    # KeepAlive on tg-listen with no token would crash-loop → must refuse.
    from lockmac import core
    monkeypatch.setattr(core, "CONFIG", tmp_path / "config.json")
    ok, msg = core.install_tg_agent()
    assert ok is False
    assert "tg-setup" in msg
