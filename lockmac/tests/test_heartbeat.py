"""Tests for the dead-man heartbeat decision logic (pure)."""
from lockmac import tg, core


def test_heartbeat_due_when_interval_elapsed():
    assert tg.heartbeat_due(last_sent=0.0, now=100.0, interval=60) is True


def test_heartbeat_not_due_within_interval():
    assert tg.heartbeat_due(last_sent=100.0, now=130.0, interval=60) is False


def test_heartbeat_off_when_interval_zero():
    assert tg.heartbeat_due(last_sent=0.0, now=99999.0, interval=0) is False


def test_deadman_triggers_after_grace_without_ack():
    # heartbeat sent at 100, never acked (last_ack older), now 100+grace
    assert tg.deadman_triggered(last_sent=100.0, last_ack=50.0, now=400.0, grace=300) is True


def test_deadman_not_triggered_within_grace():
    assert tg.deadman_triggered(last_sent=100.0, last_ack=50.0, now=200.0, grace=300) is False


def test_deadman_not_triggered_when_acked():
    # acked after the heartbeat was sent → safe
    assert tg.deadman_triggered(last_sent=100.0, last_ack=150.0, now=999.0, grace=300) is False


def test_deadman_not_triggered_before_any_heartbeat():
    assert tg.deadman_triggered(last_sent=0.0, last_ack=0.0, now=999.0, grace=300) is False


def test_core_heartbeat_cfg_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(core, "CONFIG", tmp_path / "config.json")
    iv, gr, ac = core.heartbeat_cfg()
    assert iv == 0  # default off
    core.set_heartbeat(1800, 600, "veil")
    assert core.heartbeat_cfg() == (1800, 600, "veil")
    core.set_heartbeat(60, 120, "bogus")  # invalid action → lock
    assert core.heartbeat_cfg()[2] == "lock"
