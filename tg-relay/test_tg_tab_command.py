import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tg-relay"))
sys.path.insert(0, str(ROOT / "term-bridge"))

from tg_tab_command import resolve_tab_command
from iterm_route import TabInfo


# Real Terminal.app layout: 3 separate windows, each one tab (all tab==1).
# So /tab 2 must mean "the 2nd terminal" (flat index), not "tab number 2".
def _tabs():
    return 0, [
        TabInfo(1, 1, "agentA"),
        TabInfo(2, 1, "agentB"),
        TabInfo(3, 1, "shell"),
    ]


def test_no_arg_lists_tabs_with_flat_numbers():
    out = resolve_tab_command([], lambda: _tabs(), lambda w, t: None, lambda: None)
    assert "1." in out and "2." in out and "3." in out
    assert "w1/t1" in out and "w2/t1" in out and "w3/t1" in out
    assert "/tab" in out  # usage hint


def test_set_by_flat_index_picks_nth_terminal():
    written = {}
    out = resolve_tab_command(
        ["2"], lambda: _tabs(), lambda w, t: written.update(window=w, tab=t), lambda: None
    )
    assert written == {"window": 2, "tab": 1}  # 2nd terminal, not tab==2
    assert "w2/t1" in out and "✓" in out


def test_set_by_window_colon_tab_explicit():
    written = {}
    out = resolve_tab_command(
        ["3:1"], lambda: _tabs(), lambda w, t: written.update(window=w, tab=t), lambda: None
    )
    assert written == {"window": 3, "tab": 1}


def test_flat_index_out_of_range_reports_available():
    out = resolve_tab_command(["9"], lambda: _tabs(), lambda w, t: None, lambda: None)
    assert "不存在" in out and "w1/t1" in out and "w3/t1" in out


def test_unparseable_arg():
    out = resolve_tab_command(["w"], lambda: _tabs(), lambda w, t: None, lambda: None)
    assert "无法解析" in out


def test_off_clears_default():
    cleared = {"v": False}
    out = resolve_tab_command(
        ["off"], lambda: _tabs(), lambda w, t: None, lambda: cleared.__setitem__("v", True)
    )
    assert cleared["v"] is True
    assert "已清除" in out
