# `/new` — Spawn a fresh agent session from Telegram

**Date:** 2026-06-19
**Status:** Design approved, pending implementation plan

## Goal

Add a Telegram command that opens a brand-new terminal session and launches an
AI coding agent (`claude` or `codex`) in a fresh working directory under
`~/fullStar`, optionally seeded with a first prompt. If the chosen CLI is not
installed, install it automatically as part of the launch. After spawning, route
the user's subsequent plain messages to the new session.

This extends the existing inbound flow: today a Telegram message is *injected*
into the current terminal window (`tg_relay_patches.py` →
`term_backend.inject_script()`). `/new` instead *creates* a new session.

## Command syntax

```
/new claude [initial prompt...]
/new codex  [initial prompt...]
```

- The agent name (`claude` | `codex`) is required and case-insensitive.
- Everything after the agent name is the agent's first prompt (optional).
- `/new` with no agent → reply with usage help listing valid agents.
- `/new <unknown>` → reply listing valid agents.

## Core mechanism — one chained shell line

Rather than multi-step AppleScript with timing waits, the spawn types a single
shell line into a new tab and presses Return. The shell performs mkdir → cd →
install-if-missing → launch-with-prompt atomically:

```sh
mkdir -p ~/fullStar/<dirname> && cd ~/fullStar/<dirname> \
  && (command -v claude >/dev/null 2>&1 || <installer>) \
  && claude --permission-mode bypassPermissions "<initial prompt>"
```

Rationale:

- **Auto-install** is the `|| <installer>` clause — it runs only when the CLI is
  missing (`command -v` fails), then control proceeds to the launch. This
  satisfies "auto-install in the tab" with no separate polling step.
- **First prompt** is passed as the agent's positional argument
  (`claude "..."` / `codex "..."`), avoiding any race where text is typed before
  the agent has booted. No clipboard paste is needed for the first prompt.
- **Empty prompt** → the launch command omits the quoted argument entirely.

### Directory name

Timestamp-based: `YYYY-MM-DD-HHMM` (e.g. `2026-06-19-2230`), generated at spawn
time. Always unique per minute and naturally time-sortable. `mkdir -p` is
idempotent if two spawns land in the same minute.

### New tab vs new window

AppleScript logic:

- If Terminal.app has **no window open**, create a new window (`do script ""`
  with no target, or `tell application "Terminal" to activate` then a new
  window) — this also gives the chained command a place to run.
- If a window **is** open, open a new **tab** in the front window
  (`tell application "System Events" to keystroke "t" using command down`),
  then type the command line into it.

This matches the requirement: "只有自己一个 terminal 窗口 → 建立一个新 tab".

## Retarget

After a successful spawn, the new tab becomes the active inject target so the
user's *next* plain messages drive the new session. Implementation: update the
relay's in-process target — the same `TG_ITERM_TAB` / window values that
`resolve_target()` reads (`iterm_target.py`). The new tab's index is the front
window's tab count after the `Cmd+T`. This persists for the relay process
lifetime; no new persistent state file is introduced (YAGNI).

Out of scope for this change: retargeting the long-running `iterm-monitor`
capture process (it is configured with a fixed target at launch). Output capture
of the new tab can be addressed separately if needed.

## New files

Following the many-small-files / high-cohesion convention already used in
`term-bridge/`:

- **`term-bridge/agent_cli.py`** — registry mapping each agent key to its launch
  command and installer command. Single source of truth, editable constants.
  - `claude`: launch `claude --permission-mode bypassPermissions`; installer
    `curl -fsSL https://claude.ai/install.sh | bash`
  - `codex`: launch `codex`; installer `npm install -g @openai/codex`
  - Exact installer strings to be verified against current official docs during
    implementation; they live here as editable constants.
  - Exposes a lookup that returns the agent's launch + installer, and a list of
    valid agent keys for help/validation.
- **`term-bridge/terminal_spawn_lib.py`** — pure builder. Given `(dirname, agent,
  prompt)` it returns:
  1. the chained shell line (with prompt safely single-quoted; empty prompt →
     no arg), and
  2. the AppleScript that opens a tab (or window) and types that line + Return.
  No side effects → unit-testable.
- **`term-bridge/terminal-spawn.py`** — thin CLI wrapper that builds via
  `terminal_spawn_lib` and runs the AppleScript via `osascript`; prints the new
  tab index (for retarget) and exits non-zero on failure.

## Wiring

In `tg_relay_patches.py` `handle_command`:

- Add a `/new` branch that parses `parts[1]` (agent) and the prompt remainder,
  validates against `agent_cli` valid keys, then on macOS invokes
  `terminal-spawn.py` via `_run`-style subprocess, captures the new tab index,
  updates the in-process target, and replies with a confirmation (agent, dir,
  tab, prompt preview). Mirrors the existing inbox/preview reply style.
- Add a `/new claude|codex [prompt]` line to the `/help` text.

## Error handling

- Unknown / missing agent → reply listing valid agents (from `agent_cli`).
- Non-macOS (`sys.platform != "darwin"`) → reply that spawn needs macOS, mirror
  the existing inject guard.
- `osascript` / spawn failure → reply with the error (truncated, e.g. `[:800]`),
  consistent with the existing "iTerm failed" reply path.

## Testing

pytest, matching existing `test_*.py` files in `term-bridge/`:

- **`agent_cli`** — valid-key lookups return expected launch/installer; valid-key
  list correct; unknown key handled.
- **`terminal_spawn_lib`** — shell line composition: with prompt vs without
  (no trailing arg), install clause present and gated by `command -v`, dirname
  injected, prompt single-quoting escapes embedded quotes safely.
- **`/new` parsing** — in `tg_relay_patches`/relay: valid agent + prompt, valid
  agent no prompt, unknown agent, bare `/new`.

## Non-goals

- No persistent routing-state file (in-process retarget only).
- No monitor-capture retargeting.
- No support for agents beyond `claude` / `codex` (registry makes adding them
  trivial later).
