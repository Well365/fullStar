# `/tab` Persistent Forwarding-Target Routing — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Telegram `/tab` command that sets a persistent default iTerm tab, so prefix-less messages inject into (and capture replies from) the chosen tab until changed.

**Architecture:** A new pure module `target_default.py` persists the chosen target to `inbox/target-default.json`. `parse_routed_message` (injection + per-message reply capture) and the `iterm-monitor` daemon (auto-Enter / idle screenshot) both resolve their default through `current_target() = read_default() or resolve_target()`, read fresh each time. Per-message prefixes still override. State files are namespaced per target (`log_suffix()`), so switching tabs is naturally isolated.

**Tech Stack:** Python 3.10+, pytest, python-telegram-bot (glue only). AppleScript I/O stays in `iterm_tabs`/`iterm_route`; new module is pure + JSON file I/O.

## Global Constraints

- Python ≥ 3.10; type annotations on all signatures (PEP 8, black/ruff).
- Immutable data: `ItermTarget` is `@dataclass(frozen=True)`; never mutate, return new copies.
- No silent error swallowing: corrupt/missing state → treat as unset and fall back, never raise.
- Atomic writes: temp file + `os.replace`.
- Routing priority (high→low): message prefix `[t3]`/`#3`/`[alias]` > `/tab` persistent default > `.env` `TG_ITERM_*`.
- State file path: `inbox/target-default.json`, schema `{"window": int|null, "tab": int}`.
- Tests live in `term-bridge/test_*.py`; run with `cd term-bridge && python -m pytest`.

---

## File Structure

- **Create** `term-bridge/target_default.py` — persist/read the sticky default target; `current_target()` single source.
- **Create** `term-bridge/test_target_default.py` — unit tests for the above.
- **Modify** `term-bridge/iterm_route.py` — `parse_routed_message` default via sticky-or-env with existence validation.
- **Create** `term-bridge/test_iterm_route_default.py` — routing-priority tests.
- **Modify** `term-bridge/tg_menu.py` — add `tab` to menu + action map + dynamic submenu/keyboard builder.
- **Modify** `term-bridge/test_tg_menu.py` — dynamic submenu + callback mapping tests.
- **Modify** `tg-relay/tg_relay_patches.py` — `/tab` command handler (`/tab`, `/tab N`, `/tab w:t`, `/tab off`).
- **Create** `tg-relay/test_tg_tab_command.py` — command-handler tests.
- **Modify** `tg-relay/tg-relay.py` — render dynamic `/tab` inline keyboard in `on_message`.
- **Modify** `term-bridge/iterm-monitor.py` — daemon resolves target via `current_target()` each loop; reload cursors on change.
- **Modify** `term-bridge/test_monitor_auto_default.py` — test `reload_cursors_on_change`.
- **Modify** docs: `README.md`, `README.ja.md`, `docs/FEATURES.md`, `docs/ITERM_MULTI_TAB.md`.

---

## Task 1: `target_default.py` — persistent default target

**Files:**
- Create: `term-bridge/target_default.py`
- Test: `term-bridge/test_target_default.py`

**Interfaces:**
- Consumes: `ItermTarget`, `resolve_target` from `iterm_target`.
- Produces:
  - `parse_state(raw: str) -> ItermTarget | None`
  - `dump_state(t: ItermTarget) -> str`
  - `default_path() -> Path`
  - `read_default(path: Path | None = None) -> ItermTarget | None`
  - `write_default(window: int | None, tab: int, path: Path | None = None) -> ItermTarget`
  - `clear_default(path: Path | None = None) -> None`
  - `current_target() -> ItermTarget`

- [ ] **Step 1: Write the failing test**

```python
# term-bridge/test_target_default.py
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import target_default as td
from iterm_target import ItermTarget


def test_parse_state_valid():
    assert td.parse_state('{"window": 1, "tab": 3}') == ItermTarget(window=1, tab=3)


def test_parse_state_window_null_is_front():
    assert td.parse_state('{"window": null, "tab": 2}') == ItermTarget(window=None, tab=2)


@pytest.mark.parametrize("raw", ["", "not json", "{}", '{"tab": 0}', '{"window": 1}', '{"tab": "x"}', "[]"])
def test_parse_state_invalid_returns_none(raw):
    assert td.parse_state(raw) is None


def test_dump_then_parse_roundtrip():
    t = ItermTarget(window=2, tab=5)
    assert td.parse_state(td.dump_state(t)) == t


def test_write_then_read_roundtrip(tmp_path):
    p = tmp_path / "target-default.json"
    written = td.write_default(1, 4, path=p)
    assert written == ItermTarget(window=1, tab=4)
    assert td.read_default(path=p) == ItermTarget(window=1, tab=4)


def test_read_missing_file_returns_none(tmp_path):
    assert td.read_default(path=tmp_path / "nope.json") is None


def test_read_corrupt_file_returns_none(tmp_path):
    p = tmp_path / "target-default.json"
    p.write_text("{ broken", encoding="utf-8")
    assert td.read_default(path=p) is None


def test_write_is_atomic_no_partial(tmp_path):
    p = tmp_path / "target-default.json"
    td.write_default(None, 7, path=p)
    # file is complete, parseable JSON with the expected fields
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data == {"window": None, "tab": 7}


def test_clear_default_removes_file(tmp_path):
    p = tmp_path / "target-default.json"
    td.write_default(1, 2, path=p)
    td.clear_default(path=p)
    assert not p.exists()
    td.clear_default(path=p)  # idempotent, no raise


def test_current_target_uses_default_when_set(tmp_path, monkeypatch):
    p = tmp_path / "target-default.json"
    td.write_default(1, 9, path=p)
    monkeypatch.setattr(td, "default_path", lambda: p)
    assert td.current_target() == ItermTarget(window=1, tab=9)


def test_current_target_falls_back_to_resolve(tmp_path, monkeypatch):
    monkeypatch.setattr(td, "default_path", lambda: tmp_path / "absent.json")
    monkeypatch.setattr(td, "resolve_target", lambda: ItermTarget(window=1, tab=1))
    assert td.current_target() == ItermTarget(window=1, tab=1)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd term-bridge && python -m pytest test_target_default.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'target_default'`.

- [ ] **Step 3: Write minimal implementation**

```python
# term-bridge/target_default.py
"""Persistent default forwarding target for Telegram routing.

The chosen iTerm tab is stored in inbox/target-default.json and read fresh on
every message / monitor poll, so /tab takes effect without a restart. Corrupt
or missing state is treated as "unset" and callers fall back to resolve_target()
(the .env default). current_target() is the single source of truth shared by the
routing layer and the monitor daemon.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from iterm_target import ItermTarget, resolve_target

ROOT = Path(__file__).resolve().parent.parent


def default_path() -> Path:
    return ROOT / "inbox" / "target-default.json"


def parse_state(raw: str) -> ItermTarget | None:
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    tab = data.get("tab")
    if not isinstance(tab, int) or isinstance(tab, bool) or tab < 1:
        return None
    window = data.get("window")
    if window is not None and (not isinstance(window, int) or isinstance(window, bool) or window < 1):
        return None
    return ItermTarget(window=window, tab=tab)


def dump_state(t: ItermTarget) -> str:
    return json.dumps({"window": t.window, "tab": t.tab})


def read_default(path: Path | None = None) -> ItermTarget | None:
    p = path or default_path()
    try:
        raw = p.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None
    return parse_state(raw)


def write_default(window: int | None, tab: int, path: Path | None = None) -> ItermTarget:
    t = ItermTarget(window=window, tab=tab)
    p = path or default_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(dump_state(t), encoding="utf-8")
    os.replace(tmp, p)
    return t


def clear_default(path: Path | None = None) -> None:
    p = path or default_path()
    try:
        p.unlink()
    except FileNotFoundError:
        pass


def current_target() -> ItermTarget:
    return read_default() or resolve_target()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd term-bridge && python -m pytest test_target_default.py -q`
Expected: PASS (all cases).

- [ ] **Step 5: Commit**

```bash
git add term-bridge/target_default.py term-bridge/test_target_default.py
git commit -m "feat: persistent default forwarding target (target_default.py)"
```

---

## Task 2: Route prefix-less messages through the sticky default

**Files:**
- Modify: `term-bridge/iterm_route.py` (`parse_routed_message`, add `_sticky_default`)
- Test: `term-bridge/test_iterm_route_default.py`

**Interfaces:**
- Consumes: `read_default` from `target_default`; existing `list_tabs`, `resolve_target`, `ItermTarget`.
- Produces: behavior change only — `parse_routed_message` default now sticky-or-env, validated against live tabs.

- [ ] **Step 1: Write the failing test**

```python
# term-bridge/test_iterm_route_default.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import iterm_route as ir
from iterm_route import TabInfo
from iterm_target import ItermTarget


def _tabs(*pairs):
    return 0, [TabInfo(window=w, tab=t, name=f"dir{t}") for w, t in pairs]


def test_no_prefix_uses_sticky_default(monkeypatch):
    monkeypatch.setattr(ir, "read_default", lambda: ItermTarget(window=1, tab=3))
    monkeypatch.setattr(ir, "list_tabs", lambda: _tabs((1, 1), (1, 3)))
    target, body, hit = ir.parse_routed_message("现在项目状态如何")
    assert (target.window, target.tab) == (1, 3)
    assert body == "现在项目状态如何"


def test_prefix_overrides_sticky_default(monkeypatch):
    monkeypatch.setattr(ir, "read_default", lambda: ItermTarget(window=1, tab=3))
    monkeypatch.setattr(ir, "list_tabs", lambda: _tabs((1, 1), (1, 2), (1, 3)))
    target, body, hit = ir.parse_routed_message("[t2] 列目录")
    assert target.tab == 2
    assert body == "列目录"


def test_no_default_falls_back_to_env(monkeypatch):
    monkeypatch.setattr(ir, "read_default", lambda: None)
    monkeypatch.setattr(ir, "resolve_target", lambda: ItermTarget(window=1, tab=1))
    target, body, hit = ir.parse_routed_message("无前缀消息")
    assert target.tab == 1


def test_sticky_default_for_closed_tab_falls_back(monkeypatch):
    # sticky points at t9 but only t1 is open now
    monkeypatch.setattr(ir, "read_default", lambda: ItermTarget(window=1, tab=9))
    monkeypatch.setattr(ir, "list_tabs", lambda: _tabs((1, 1)))
    monkeypatch.setattr(ir, "resolve_target", lambda: ItermTarget(window=1, tab=1))
    target, body, hit = ir.parse_routed_message("无前缀消息")
    assert target.tab == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd term-bridge && python -m pytest test_iterm_route_default.py -q`
Expected: FAIL — `AttributeError: ... has no attribute 'read_default'` (not imported yet) / wrong target.

- [ ] **Step 3: Write minimal implementation**

In `term-bridge/iterm_route.py`, add the import near the other imports (after line 15):

```python
from target_default import read_default  # noqa: E402
```

Add this helper above `parse_routed_message`:

```python
def _sticky_default() -> ItermTarget:
    """Persistent /tab default if set and still open, else the .env default."""
    d = read_default()
    if d is None:
        return resolve_target()
    if d.window is not None:
        code, tabs = list_tabs()
        if code == 0 and tabs and not any(t.window == d.window and t.tab == d.tab for t in tabs):
            return resolve_target()
    return d
```

In `parse_routed_message`, change the default line (was `default = resolve_target()`):

```python
    body = text.strip()
    default = _sticky_default()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd term-bridge && python -m pytest test_iterm_route_default.py test_target_default.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add term-bridge/iterm_route.py term-bridge/test_iterm_route_default.py
git commit -m "feat: route prefix-less messages through sticky /tab default"
```

---

## Task 3: `tg_menu.py` — `/tab` command + dynamic submenu

**Files:**
- Modify: `term-bridge/tg_menu.py`
- Test: `term-bridge/test_tg_menu.py`

**Interfaces:**
- Consumes: nothing new (pure module; receives tab rows from caller).
- Produces:
  - `MENU_COMMANDS` includes `("tab", "选择转发目标 tab")`.
  - `_ACTION_TO_CMD["tab"] = "/tab"`.
  - `tab_submenu(tabs: list[tuple[int, int, str]]) -> list[tuple[str, str]]` — buttons `(label, "tab:<w>:<t>")`.
  - `callback_to_command("tab", "1:3")` → `"/tab 1:3"`.

- [ ] **Step 1: Write the failing test** (append to `term-bridge/test_tg_menu.py`)

```python
def test_menu_includes_tab():
    from tg_menu import MENU_COMMANDS
    assert ("tab", "选择转发目标 tab") in MENU_COMMANDS


def test_tab_submenu_builds_buttons():
    from tg_menu import tab_submenu
    rows = tab_submenu([(1, 1, "..rees/fullStar"), (1, 3, "myapp")])
    assert rows == [
        ("w1/t1 · ..rees/fullStar", "tab:1:1"),
        ("w1/t3 · myapp", "tab:1:3"),
    ]


def test_tab_submenu_empty_when_no_tabs():
    from tg_menu import tab_submenu
    assert tab_submenu([]) == []


def test_callback_to_command_tab():
    from tg_menu import callback_to_command
    assert callback_to_command("tab", "1:3") == "/tab 1:3"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd term-bridge && python -m pytest test_tg_menu.py -q`
Expected: FAIL — `ImportError: cannot import name 'tab_submenu'` / missing menu entry.

- [ ] **Step 3: Write minimal implementation** in `term-bridge/tg_menu.py`

Add to `MENU_COMMANDS` (e.g. after the `("tabs", ...)` entry):

```python
    ("tab", "选择转发目标 tab"),
```

Add to `_ACTION_TO_CMD`:

```python
    "tab": "/tab",
```

Add the dynamic builder (after `menu_for_command`):

```python
def tab_submenu(tabs: list[tuple[int, int, str]]) -> list[tuple[str, str]]:
    """Inline buttons for /tab from live tabs: (window, tab, name) → (label, callback)."""
    rows: list[tuple[str, str]] = []
    for window, tab, name in tabs:
        short = name.replace("\n", " ")[:20]
        rows.append((f"w{window}/t{tab} · {short}", f"tab:{window}:{tab}"))
    return rows
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd term-bridge && python -m pytest test_tg_menu.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add term-bridge/tg_menu.py term-bridge/test_tg_menu.py
git commit -m "feat: /tab command entry + dynamic tab submenu in tg_menu"
```

---

## Task 4: `/tab` command handler in the relay

**Files:**
- Modify: `tg-relay/tg_relay_patches.py` (add `/tab` branch in `handle_command`)
- Test: `tg-relay/test_tg_tab_command.py`

**Interfaces:**
- Consumes: `write_default`, `clear_default` from `target_default`; `list_tabs` from `iterm_route`.
- Produces: a pure `resolve_tab_command(parts, list_tabs_fn, write_fn, clear_fn) -> str` so logic is testable without telegram. `handle_command` calls it for `/tab`.

- [ ] **Step 1: Write the failing test**

```python
# tg-relay/test_tg_tab_command.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tg-relay"))
sys.path.insert(0, str(ROOT / "term-bridge"))

from tg_tab_command import resolve_tab_command
from iterm_route import TabInfo


def _tabs():
    return 0, [TabInfo(1, 1, "..rees/fullStar"), TabInfo(1, 3, "myapp")]


def test_no_arg_lists_tabs():
    out = resolve_tab_command([], lambda: _tabs(), lambda w, t: None, lambda: None)
    assert "w1/t1" in out and "w1/t3" in out
    assert "/tab" in out  # usage hint


def test_set_by_number_writes_default():
    written = {}
    out = resolve_tab_command(
        ["3"], lambda: _tabs(), lambda w, t: written.update(window=w, tab=t), lambda: None
    )
    assert written == {"window": 1, "tab": 3}
    assert "w1/t3" in out and "✓" in out


def test_set_by_window_colon_tab():
    written = {}
    out = resolve_tab_command(
        ["1:3"], lambda: _tabs(), lambda w, t: written.update(window=w, tab=t), lambda: None
    )
    assert written == {"window": 1, "tab": 3}


def test_unknown_number_reports_available():
    out = resolve_tab_command(["9"], lambda: _tabs(), lambda w, t: None, lambda: None)
    assert "不存在" in out and "t1" in out and "t3" in out


def test_off_clears_default():
    cleared = {"v": False}
    out = resolve_tab_command(
        ["off"], lambda: _tabs(), lambda w, t: None, lambda: cleared.__setitem__("v", True)
    )
    assert cleared["v"] is True
    assert "已清除" in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd tg-relay && python -m pytest test_tg_tab_command.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tg_tab_command'`.

- [ ] **Step 3: Write minimal implementation**

Create `tg-relay/tg_tab_command.py`:

```python
"""Resolve /tab subcommands to a reply string (pure; no telegram, no AppleScript I/O).

Forms: `/tab` (list), `/tab N`, `/tab W:T`, `/tab off`. list_tabs_fn returns the
(code, [TabInfo]) tuple; write_fn(window, tab) persists; clear_fn() removes the default.
"""
from __future__ import annotations

from typing import Callable


def _label(t) -> str:
    return f"w{t.window}/t{t.tab}"


def resolve_tab_command(
    args: list[str],
    list_tabs_fn: Callable[[], tuple[int, list]],
    write_fn: Callable[[int | None, int], object],
    clear_fn: Callable[[], None],
) -> str:
    code, tabs = list_tabs_fn()
    if not args:
        if code != 0 or not tabs:
            return "没有打开的 iTerm 窗口"
        lines = ["当前 tab（点 /tab 菜单按钮或发 /tab N 设为默认）:"]
        for t in tabs:
            lines.append(f"• {_label(t)} · {t.name.replace(chr(10), ' ')[:40]}")
        lines.append("用法: /tab 3  或  /tab off（清除）")
        return "\n".join(lines)

    arg = args[0].strip().lower()
    if arg == "off":
        clear_fn()
        return "已清除默认目标，回退 .env 默认"

    window: int | None = None
    tab: int | None = None
    if ":" in arg:
        w_str, _, t_str = arg.partition(":")
        try:
            window, tab = int(w_str), int(t_str)
        except ValueError:
            return f"无法解析: {args[0]}（用法 /tab 3 或 /tab 1:3）"
    else:
        try:
            tab = int(arg)
        except ValueError:
            return f"无法解析: {args[0]}（用法 /tab 3 或 /tab 1:3）"

    if code != 0 or not tabs:
        return "无法读取 iTerm 标签列表"
    matches = [t for t in tabs if t.tab == tab and (window is None or t.window == window)]
    if not matches:
        avail = ", ".join(_label(t) for t in tabs)
        return f"tab {args[0]} 不存在，当前有: {avail}"
    hit = matches[0]
    write_fn(hit.window, hit.tab)
    return f"✓ 默认目标已设为 {_label(hit)} ({hit.name.replace(chr(10), ' ')[:40]})"
```

Wire it into `tg-relay/tg_relay_patches.py` `handle_command` — add this branch (after the `/new` branch, before `/stop` group):

```python
        if cmd == "/tab":
            from tg_tab_command import resolve_tab_command
            from target_default import write_default, clear_default
            return resolve_tab_command(
                parts[1:], list_tabs, write_default, clear_default
            )
```

Add the `list_tabs` import at the top of `tg_relay_patches.py` (with the other `iterm_route` imports):

```python
from iterm_route import format_tabs_message, list_tabs, parse_routed_message
```

(Existing line imports `format_tabs_message, parse_routed_message`; extend it with `list_tabs`.)

- [ ] **Step 4: Run test to verify it passes**

Run: `cd tg-relay && python -m pytest test_tg_tab_command.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tg-relay/tg_tab_command.py tg-relay/test_tg_tab_command.py tg-relay/tg_relay_patches.py
git commit -m "feat: /tab command handler (list/set/off) wired into relay"
```

---

## Task 5: Render `/tab` dynamic inline keyboard in the telegram glue

**Files:**
- Modify: `tg-relay/tg-relay.py` (`on_message`)

**Interfaces:**
- Consumes: `tab_submenu` from `tg_menu`, `list_tabs` from `iterm_route`.
- Produces: bare `/tab` shows inline buttons; tapping one fires callback `tab:w:t` → existing `dispatch_callback` → `/tab w:t` (Task 4 handler).

This task wires telegram (not unit-tested — verified by the import smoke test + manual run). Keep the change minimal.

- [ ] **Step 1: Add the dynamic-keyboard branch**

In `tg-relay/tg-relay.py`, extend the import on line 15:

```python
from tg_menu import MENU_COMMANDS, dispatch_callback, menu_for_command, tab_submenu  # noqa: E402
```

Add `list_tabs` to the `iterm_route` imports in this file (find the existing `from iterm_route import ...`; if absent, add):

```python
from iterm_route import list_tabs  # noqa: E402
```

In `on_message`, replace the command branch (currently lines ~267-272):

```python
        if text.startswith("/"):
            base = text.strip().split()[0].lower().split("@")[0]
            if base == "/tab" and len(text.strip().split()) == 1:
                code, tabs = list_tabs()
                rows = tab_submenu([(t.window, t.tab, t.name) for t in tabs]) if code == 0 else []
                if rows:
                    await update.message.reply_text("选择默认 tab：", reply_markup=_keyboard(rows))
                    return
                await update.message.reply_text(_handle_command(text)[:4000])
                return
            sub = menu_for_command(text)
            if sub:
                await update.message.reply_text("请选择：", reply_markup=_keyboard(sub))
                return
            reply = _handle_command(text)
        else:
            reply = _handle_natural_language(chat_id, text)
        await update.message.reply_text(reply[:4000])
```

- [ ] **Step 2: Smoke-test imports**

Run: `cd tg-relay && python -c "import importlib.util, sys; sys.path.insert(0,'../term-bridge'); import ast; ast.parse(open('tg-relay.py').read()); print('parse ok')"`
Expected: `parse ok` (syntax valid). Full import requires `python-telegram-bot`; parsing is sufficient here.

- [ ] **Step 3: Run the whole suite to confirm no regressions**

Run: `cd term-bridge && python -m pytest -q && cd ../tg-relay && python -m pytest -q`
Expected: all PASS.

- [ ] **Step 4: Commit**

```bash
git add tg-relay/tg-relay.py
git commit -m "feat: dynamic /tab inline keyboard in telegram glue"
```

---

## Task 6: Daemon follows `/tab` default

**Files:**
- Modify: `term-bridge/iterm-monitor.py`
- Test: `term-bridge/test_monitor_auto_default.py` (append)

**Interfaces:**
- Consumes: `current_target` from `target_default`.
- Produces:
  - `_monitor_file` namespaced by `current_target().log_suffix()`.
  - main loop re-resolves `target = current_target()` each iteration.
  - `reload_cursors_on_change(old_label: str, new_label: str) -> bool` — True when the target changed.

- [ ] **Step 1: Write the failing test** (append to `term-bridge/test_monitor_auto_default.py`)

```python
def test_reload_cursors_on_change_detects_switch():
    import importlib.util, sys
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "iterm_monitor_mod", Path(__file__).resolve().parent / "iterm-monitor.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.reload_cursors_on_change("w1-t1", "w1-t3") is True
    assert mod.reload_cursors_on_change("w1-t3", "w1-t3") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd term-bridge && python -m pytest test_monitor_auto_default.py -k reload_cursors -q`
Expected: FAIL — `AttributeError: module ... has no attribute 'reload_cursors_on_change'`.

- [ ] **Step 3: Write minimal implementation** in `term-bridge/iterm-monitor.py`

Add import near the top (after the `from iterm_target import resolve_target` line):

```python
from target_default import current_target  # noqa: E402
```

Change `_monitor_file` (line 29-30) to use the shared source:

```python
def _monitor_file(kind: str) -> Path:
    return ROOT / "inbox" / f"iterm-monitor-{current_target().log_suffix()}.{kind}"
```

Add the pure helper (top-level, near `_monitor_file`):

```python
def reload_cursors_on_change(old_label: str, new_label: str) -> bool:
    """True when the resolved target changed since last poll (cursors must reload)."""
    return old_label != new_label
```

In the daemon loop, replace `target = resolve_target()` (line 348) with:

```python
    target = current_target()
```

At the top of the `while True:` loop body (right after `while True:`), re-resolve and reload cursors on switch:

```python
    while True:
        new_target = current_target()
        if reload_cursors_on_change(target.log_suffix(), new_target.log_suffix()):
            target = new_target
            last_seen_reply = _read_last_sent()
            last_extract_change_at = _read_last_sent_at() or time.time()
            last_capture = ""
            last_stable = ""
            stable_count = 0
            stable_since = time.time()
        code, current = _capture_tail(tail_lines)
```

Update the startup log line (line ~349-355) to note it is overridable — change `target=...` context by appending to the printed string:

```python
        f"target={target.label()} (可被 /tab 覆盖) tail={tail_lines} interval={interval}s "
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd term-bridge && python -m pytest test_monitor_auto_default.py -q`
Expected: PASS.

- [ ] **Step 5: Run the full suite**

Run: `cd term-bridge && python -m pytest -q`
Expected: all PASS (186 prior + new).

- [ ] **Step 6: Commit**

```bash
git add term-bridge/iterm-monitor.py term-bridge/test_monitor_auto_default.py
git commit -m "feat: monitor daemon follows /tab default (current_target each poll)"
```

---

## Task 7: Documentation

**Files:**
- Modify: `README.md`, `README.ja.md`, `docs/FEATURES.md`, `docs/ITERM_MULTI_TAB.md`

**Interfaces:** none (docs only).

- [ ] **Step 1: README.md — add `/tab` to the command table**

In the Telegram command table, add this row after the `/tabs` / `/format` rows:

```markdown
| `/tab [N]` | 选择转发目标 tab（无参弹按钮选，`/tab 3` 直接设，`/tab off` 清除）。设为持久默认,后续无前缀消息都进该 tab |
```

And add a sentence to the routing-priority note (near the prefix table):

```markdown
> **路由优先级**：单条消息前缀 `[t3]` > `/tab` 设的持久默认 > `.env` 的 `TG_ITERM_TAB`。
> 用 `/tab` 选一次后，后续无前缀消息的注入与回传都跟随该 tab（含卡住自动按 Enter / 空闲截图）。
```

- [ ] **Step 2: README.ja.md — add `/tab` row**

In the Japanese command table, add after the `/tabs` row:

```markdown
| `/tab [N]` | 転送先タブを選択（引数なしでボタン選択、`/tab 3` で直接設定、`/tab off` で解除）。永続デフォルトとして以降の無接頭辞メッセージに適用 |
```

- [ ] **Step 3: docs/FEATURES.md — add a `/tab` section**

Add a new numbered section (after the `/new` section):

```markdown
## 9. 持久转发目标 — `/tab`

- `/tab`（无参）弹出当前所有 tab 的按钮；`/tab 3` / `/tab 1:3` 直接设；`/tab off` 清除。
- 选中后持久化到 `inbox/target-default.json`，后续无前缀消息的**注入 + 回传 + 卡住自动按 Enter + 空闲截图**都跟随该 tab，重启不丢。
- 路由优先级：单条前缀 `[t3]` > `/tab` 默认 > `.env` 默认。
- 实现：`term-bridge/target_default.py`（`current_target()` 单一真源）+ `iterm_route.py` + `iterm-monitor.py`。
```

- [ ] **Step 4: docs/ITERM_MULTI_TAB.md — document `/tab` + priority**

Add a short section explaining `/tab` sets the sticky default and the three-level priority (prefix > /tab > .env). Mirror the wording from FEATURES.md section 9.

- [ ] **Step 5: Commit**

```bash
git add README.md README.ja.md docs/FEATURES.md docs/ITERM_MULTI_TAB.md
git commit -m "docs: document /tab persistent forwarding target"
```

---

## Self-Review Notes

- **Spec coverage:** `/tab` list/set/off (Tasks 4-5), persistence + priority (Tasks 1-2), dynamic menu (Task 3), daemon follows (Task 6), docs (Task 7) — all spec sections covered.
- **Type consistency:** `current_target() -> ItermTarget`, `read_default() -> ItermTarget | None`, `write_default(window, tab) -> ItermTarget`, `tab_submenu(list[tuple[int,int,str]]) -> list[tuple[str,str]]`, `resolve_tab_command(args, list_tabs_fn, write_fn, clear_fn) -> str`, `reload_cursors_on_change(str,str) -> bool` — used consistently across tasks.
- **State-file isolation:** monitor state files namespaced by `log_suffix()`; switching target switches namespace (Task 6), matching spec §3.
