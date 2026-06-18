---
name: tgkit
description: >-
  Sends Telegram text, files, photos, and macOS screenshots via the tg-notify CLI.
  Use when the user asks to notify Telegram, send a TG message, push build status
  to Telegram, tgshot, screenshot to Telegram, or Telegram alert. Requires tgkit
  installed and TELEGRAM_BOT_TOKEN in .env. macOS only for screenshot features.
disable-model-invocation: true
---

# tg-notify — Telegram Notify Skill

Teach the agent to send Telegram notifications using **tgkit CLI**. This skill is standalone and does not depend on any specific project.

**Composable:** `./mob install-skill --only tg` alone, or with `adb` / `ios` for device remote验收. See `mobile-agent/docs/SKILL_COMPOSE.md`.

## Prerequisites

1. Install tg-notify:

```bash
pip install "tg-notify[dotenv]"
# or from source: pip install "git+https://YOUR_GIT/tg_notify.git#egg=tgkit[dotenv]"
```

2. Configure environment (project root or home):

```bash
cp .env.example .env
# Edit .env — never commit it
```

Required variables:

| Variable | Required | Description |
|----------|----------|------|
| `TELEGRAM_BOT_TOKEN` | yes | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | recommended | Default recipient chat id |

Optional: `TGKIT_CONFIG_PATH` — JSON file with `chat_id` if not using `TELEGRAM_CHAT_ID`.

3. Verify (or run one-click setup from tg_skill repo):

```bash
# one-click: pip + .env + Cursor/Claude skills
/path/to/tg-notify-skill/scripts/setup-all.sh --project-dir . --test

tgkit send "tgkit skill test"
```

## When to use

- User wants to **send a message** to Telegram
- User wants **build/CI/deploy notification** on Telegram
- User wants to **send a file or screenshot** to Telegram
- User wants **macOS app window capture** sent to Telegram

## Agent workflow

1. Confirm `.env` exists or ask user to set `TELEGRAM_BOT_TOKEN`.
2. Prefer **CLI** over writing custom Python unless the user needs programmatic integration.
3. Run commands from the directory that contains `.env`, or export variables first.
4. Report success/failure from CLI exit code and stdout.
5. **Never** print or commit bot tokens.

## Command reference

### Send text

```bash
tgkit send "构建完成"
tgkit send --text "deploy done" --chat-id 123456789
```

Or use wrapper:

```bash
/path/to/tg-notify-skill/scripts/tg-notify.sh "构建完成"
```

### Send photo (inline preview)

```bash
tgkit send --photo screenshot.png --caption "结果"
```

### Send file (document attachment)

```bash
tgkit send --file build.log
```

### Screenshot (macOS)

```bash
# Full screen
tgkit screenshot

# Interactive region
tgkit screenshot --mode interactive

# Open app and capture its window
tgkit screenshot --app Calculator --wait 3
tgkit screenshot --app-path "/Applications/Safari.app" --caption "Safari"
tgkit screenshot --app Telegram --wait 3
```

Or wrapper:

```bash
/path/to/tg-notify-skill/scripts/tg-screenshot.sh --app Calculator
```

### Python API (optional)

```python
from tg_notify import text, photo, file, screenshot, app_screenshot

text("hello")
photo("a.png", caption="caption")
app_screenshot(app="Calculator", wait_seconds=3)
```

## macOS permissions

App/window screenshots need:

- **系统设置 → 隐私与安全性 → 辅助功能** — authorize Terminal / Cursor / iTerm
- **系统设置 → 隐私与安全性 → 屏幕录制** — same apps

If error `-1728` on window id, tg-notify automatically falls back to region capture.

## Safety rules

- Do not send secrets, tokens, or full `.env` contents via Telegram unless user explicitly asks
- Truncate long logs before sending; attach full log as `--file` if needed
- Ask confirmation before sending to a non-default `--chat-id`

## Troubleshooting

| Error | Fix |
|-------|-----|
| `TELEGRAM_BOT_TOKEN is not set` | Create `.env` with token |
| `chat_id is not set` | Set `TELEGRAM_CHAT_ID` or add `chat_id` to config JSON |
| `Process not running` | Increase `--wait`; check app name case (`telegram` → `Telegram`) |
| `辅助访问` / `-25211` | Grant Accessibility permission to terminal |
| `command not found: tgkit` | Run `pip install "tg-notify[dotenv]"` |

## More detail

See [reference.md](reference.md) for full command tables and platform install paths.
