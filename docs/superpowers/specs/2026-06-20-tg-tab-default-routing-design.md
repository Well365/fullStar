# 设计：`/tab` —— 用菜单选择持久转发目标 tab

**日期**：2026-06-20
**状态**：已确认，待实现
**主题**：Telegram `/tab` 命令，设定「无前缀消息」默认注入/回传的 iTerm tab

## 背景与问题

当前 Telegram → iTerm 的路由有两条来源：

1. 单条消息前缀（`[t3]` / `#3` / `[alias]` / `@t3:`），临时指定本条消息去哪个 tab。
2. 无前缀时回退到 `.env` 的 `TG_ITERM_*` 写死默认（`resolve_target()`）。

没有「运行时通过 Telegram 切换默认 tab」的办法——要改默认得编辑 `.env` 并重启。
实际后果（已复现）：手机发「现在项目状态如何」无前缀 → 落到 `.env` 默认 `w1/t1`，
而该 tab 恰是普通 shell（非 agent 会话），于是变成 `sh: command not found: 现在项目状态如何`。

用户诉求：用一个菜单命令选择「转发到第几个 tab」，且选了之后**持续生效**。

## 关键架构发现

注入和回传抓取**已经是按消息绑定同一个 target** 的：
`tg-relay/tg_relay_patches.py::handle_natural_language` 调 `parse_routed_message(text)` 得到 target，
既用于注入（`_inject_iterm(..., target)`），也用于回传（`_schedule_iterm_monitor_poll(target=target)`）。

因此只需让 `parse_routed_message` 在**无前缀**时回退到一个「持久默认 target」状态文件，
注入与每条消息的回传抓取就都自动跟随。常驻守护进程是另一处独立读取，需单独接入（见第 3 节）。

## 目标

- 新增 `/tab` 命令：无参列当前 tab 的 inline 按钮；带参 `/tab N` 直接设定。
- 选中后**持久化**默认 target，实时生效、重启不丢，机制与 `/format` 状态文件一致。
- 注入、每条消息回传、常驻守护（自动按 Enter / 空闲截图）全部跟随该默认。
- 单条消息前缀仍可临时覆盖。

## 非目标（YAGNI）

- 不做 per-chat 隔离的默认（单操作者模型，全局状态文件即可，与 `/format` 一致）。
- 不自动探测某 tab 是否在跑 agent（不可靠）；由用户用 `/tab` 自行选择正确 tab。
- 不改前缀语法。

## 路由优先级（高 → 低）

1. 单条消息前缀 `[t3]` / `#3` / `[alias]` / `@t3:`（临时覆盖，最高）
2. `/tab` 设的持久默认（**新增**）
3. `.env` 的 `TG_ITERM_*` 默认（兜底）

## 组件设计

### 1. `term-bridge/target_default.py`（新，纯逻辑 + 受限 I/O）

持久默认 target 的单一读写点。状态文件 `inbox/target-default.json`，存 `{"window": int|null, "tab": int}`。

- `read_default() -> ItermTarget | None`：读状态文件；缺失/损坏/字段非法 → 返回 `None`（视为未设）。
- `write_default(window: int | None, tab: int) -> ItermTarget`：原子写（临时文件 + `os.replace`），返回写入的 `ItermTarget`。
- `clear_default() -> None`：删除状态文件（供 `/tab off`）。
- 纯解析 `parse_state(raw: str) -> ItermTarget | None` 与序列化 `dump_state(t) -> str` 拆出，便于单测不碰磁盘。
- `current_target() -> ItermTarget`：`read_default() or resolve_target()`——给守护和路由共用的单一真源。

读时校验：`read_default` 仅做格式校验；「目标 tab 是否仍存在」的校验放在调用方（命令处理与守护），
避免纯模块依赖 `list_tabs`（AppleScript I/O）。

### 2. `term-bridge/iterm_route.py`（改一处接入点）

`parse_routed_message` 内：
```python
default = read_default() or resolve_target()
```
（原为 `default = resolve_target()`。）这是让注入 + 每条消息回传都跟随的唯一接入点。

无前缀消息：若 `read_default()` 指向的 tab 经 `list_tabs()` 校验已不存在，则回退 `resolve_target()`，
并由命令层提示用户（解析层本身不发消息）。

### 3. `term-bridge/iterm-monitor.py`（守护跟随）

- `_monitor_file` 改为基于 `current_target().log_suffix()`（原 `resolve_target()`），与守护循环同源。
- 守护**每轮循环顶部**重解析 `target = current_target()`（原在循环外只读一次）。
- 因状态文件按 `log_suffix()` 分命名空间，切 tab 自然换一套 `last-sent` / `auto-default-mark` / `screenshot-mark`，
  天然隔离——不会用 t1 的「已发送」压住 t3 的输出。
- **切换检测**：纯函数 `reload_cursors_on_change(old_label, new_label) -> bool`。循环顶部若 target label 变化，
  从新 target 的状态文件重载游标（`last_seen_reply` = `_read_last_sent()` 等），避免拿旧 tab 残留比较。
- 启动日志 `target=` 打印 `current_target().label()`，附注「(可被 /tab 覆盖)」。

### 4. `term-bridge/tg_menu.py`（命令清单 + 动态子菜单）

- `MENU_COMMANDS` 增 `("tab", "选择转发目标 tab")`。
- `_ACTION_TO_CMD["tab"] = "/tab"`。
- `/tab` 子菜单**动态**（依赖当前开着的 tab），不入静态 `SUBMENUS`。新增：
  - `dynamic_submenu(cmd: str, tabs: list[TabInfo]) -> list[tuple[str,str]] | None`：
    `cmd == "/tab"` 时返回 `[(f"w{w}/t{t} · {name[:20]}", f"tab:{w}:{t}"), ...]`，否则 `None`。
  - callback `tab:<window>:<tab>` → `callback_to_command("tab", "<window>:<tab>")` → `"/tab <window>:<tab>"`。
- `menu_for_command` 保持只处理静态子菜单；动态子菜单由 relay 层在拿到 tab 列表后构建。

### 5. `tg-relay/tg_relay_patches.py`（命令 + callback 接线）

- `/tab` 处理：
  - 无参 → `list_tabs()`，用 `dynamic_submenu("/tab", tabs)` 渲染 inline 按钮；空列表回「没有打开的 iTerm 窗口」。
  - `/tab N`（单数字）→ 校验 N 在 `list_tabs()` 中；命中则 `write_default(window, tab)` 回执，未命中回「tab N 不存在，当前有：…」。
  - `/tab w:t`（callback 转来）→ 同 `write_default` 路径。
  - `/tab off` → `clear_default()` 回「已清除默认，回退 .env」。
- callback `tab:w:t` 经现有 `dispatch_callback` → `/tab w:t` → 上面处理。
- 回执文案：`✓ 默认目标已设为 w1/t3 (~/Documents/aiTrees/fullStar)`（目录名取自匹配的 `TabInfo.name`）。

## 错误与边界处理

- 状态文件缺失/损坏/字段非法 → 视为未设，回退 `.env`，不抛错。
- `/tab N` 越界 → 显式回「不存在 + 当前列表」，不静默。
- 持久默认指向的 tab 已关闭 → 路由层校验失败则回退 `.env`；若用户已切走，注入失败走现有 `iTerm failed:` 回执。
- 原子写：临时文件 + `os.replace`，避免半写状态文件被读到。

## 测试（pytest，沿用 `term-bridge/test_*.py`）

`test_target_default.py`：
- 读写往返；缺失文件 → `None`；损坏 JSON → `None`；字段缺失/类型错 → `None`。
- 原子写（写后立即可读，内容完整）。
- `current_target` 优先级：有默认用默认；无默认回退 `resolve_target`（monkeypatch env）。

`test_iterm_route`（或并入现有）：
- 有持久默认 + 无前缀 → 用默认。
- 有前缀 + 有持久默认 → 前缀覆盖默认。
- 无默认 + 无前缀 → 回退 env。

`test_tg_menu.py`：
- `dynamic_submenu("/tab", tabs)` 按钮文案与 callback 值。
- callback `tab:1:3` → `/tab 1:3` 映射。

`test_monitor_auto_default.py`（或新 `test_monitor_retarget.py`）：
- `reload_cursors_on_change` 在 label 变化/不变时的布尔行为（纯函数，不起真守护）。

## 文档更新（实现后）

- `README.md`：命令表加 `/tab`；在路由章节补「持久默认 + 优先级」说明。
- `README.ja.md`：命令表加 `/tab`。
- `docs/FEATURES.md`：新增 `/tab` 持久转发目标一节。
- `docs/ITERM_MULTI_TAB.md`：补 `/tab` 用法与优先级。

## 影响面小结

新增 1 个纯模块（`target_default.py`）、改 4 个文件各一处接入点
（`iterm_route.py` 路由默认、`iterm-monitor.py` 守护源、`tg_menu.py` 菜单、`tg_relay_patches.py` 接线）。
不改前缀语法、不改 `.env` 兼容、不改回传格式机制。
