# tg-notify Skill — Reference

## Install tg-notify (Python package)

```bash
pip install "tg-notify[dotenv]"
```

Verify:

```bash
which tgkit
tgkit send --help
tgkit screenshot --help
```

## Environment

```bash
# .env
TELEGRAM_BOT_TOKEN=your_token_from_botfather
TELEGRAM_CHAT_ID=123456789
# TGKIT_CONFIG_PATH=config.json   # optional JSON with chat_id
```

Load order for token/chat_id:

1. Explicit CLI flags (`--chat-id`)
2. Environment variables
3. `TGKIT_CONFIG_PATH` JSON field `chat_id`

## CLI commands

### `tgkit send`

| Option | Description |
|--------|-------------|
| `MESSAGE` | Positional text shorthand |
| `--text TEXT` | Text body |
| `--photo PATH` | Image with inline preview |
| `--file PATH` | Document attachment |
| `--caption TEXT` | Caption for photos |
| `--chat-id ID` | Override recipient |
| `--config-path PATH` | JSON for chat_id lookup |

Examples:

```bash
tgkit send "hello"
tgkit send --photo out.png --caption "UI"
tgkit send --file app.log
tgkit send "hi" --chat-id 999888777
```

### `tgkit screenshot` (macOS)

| Option | Description |
|--------|-------------|
| `--mode full\|interactive\|window` | Capture mode (default: full) |
| `--app NAME` | Open app by name, capture window |
| `--app-path PATH` | Open `.app` bundle path |
| `--bundle-id ID` | Open by bundle id |
| `--process NAME` | System Events process override |
| `--wait SECONDS` | Wait after launch (default: 2) |
| `--window-index N` | Window index (default: 1) |
| `--no-shadow` | No window shadow (window-id mode) |
| `--keep` | Keep temp screenshot file |
| `--caption TEXT` | Telegram caption |

Examples:

```bash
tgkit screenshot
tgkit screenshot --mode interactive
tgkit screenshot --app Calculator --wait 2
tgkit screenshot --app-path "/Applications/CocosCreator.app" --wait 5 -c "Cocos"
tgkit screenshot --app "Visual Studio Code" --process Code
```

## Wrapper scripts (this repo)

Located in `scripts/`:

| Script | Purpose |
|--------|---------|
| `load-env.sh` | Find and export `.env` |
| `tg-notify.sh` | Send text/file/photo |
| `tg-screenshot.sh` | Screenshot subcommands |
| `install-skill.sh` | Install SKILL.md to Cursor / Claude Code |

Usage:

```bash
./scripts/tg-notify.sh "message"
./scripts/tg-screenshot.sh --app Calculator
./scripts/tg-screenshot.sh --mode interactive
```

## Python API

```python
from tg_notify import text, file, photo, screenshot, app_screenshot

text("msg")
file("log.txt")
photo("img.png", caption="cap")
screenshot(mode="full")
app_screenshot(app="Calculator", wait_seconds=2, caption="cap")
```

## Platform skill install paths

| Platform | Path |
|----------|------|
| Cursor | `~/.cursor/skills/tg-notify/SKILL.md` |
| Claude Code | `~/.claude/skills/tg-notify/SKILL.md` |
| Project-scoped Cursor | `.cursor/skills/tg-notify/SKILL.md` |

Run `./scripts/install-skill.sh` to install to user-level Cursor and Claude Code.

## ChatGPT / Custom GPT

Copy the body of `SKILL.md` (without YAML frontmatter) into Custom GPT Instructions.
For execution without a local shell, expose tg-notify via an HTTP MCP server (out of scope for Plan A).
