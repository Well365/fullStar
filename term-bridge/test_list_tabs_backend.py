"""list_tabs() must enumerate whichever terminal TG_TERM_BACKEND selects.

The bug: list_tabs hardcoded iTerm, so with TG_TERM_BACKEND=terminal (the
default) it queried the wrong app and saw none of the user's Terminal.app tabs.
"""
from __future__ import annotations

import iterm_route as ir
import iterm_tabs
import terminal_tabs


def test_list_tabs_terminal_backend(monkeypatch):
    monkeypatch.setattr(ir, "resolve_backend", lambda: "terminal")
    monkeypatch.setattr(
        terminal_tabs,
        "list_targets",
        lambda: (0, [{"window": 2, "tab": 1, "name": "agentA", "sessions": 1}]),
    )
    code, tabs = ir.list_tabs()
    assert code == 0
    assert (tabs[0].window, tabs[0].tab, tabs[0].name) == (2, 1, "agentA")


def test_list_tabs_iterm_backend(monkeypatch):
    monkeypatch.setattr(ir, "resolve_backend", lambda: "iterm")
    monkeypatch.setattr(
        iterm_tabs,
        "list_targets",
        lambda: (0, [{"window": 1, "tab": 3, "name": "itab", "sessions": 1}]),
    )
    code, tabs = ir.list_tabs()
    assert code == 0
    assert (tabs[0].window, tabs[0].tab) == (1, 3)


def test_list_tabs_propagates_error_code(monkeypatch):
    monkeypatch.setattr(ir, "resolve_backend", lambda: "terminal")
    monkeypatch.setattr(terminal_tabs, "list_targets", lambda: (1, [{"error": "boom"}]))
    code, tabs = ir.list_tabs()
    assert code == 1
    assert tabs == []
