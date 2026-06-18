# Examples for LLM agents using tg-notify skill

## Notify build success

User: 「Android 包打好了，发到 TG」

Agent:

```bash
tgkit send "✅ Android 构建完成"
```

## Send log on failure

User: 「构建失败了，把最后说明和日志发 TG」

Agent:

```bash
tgkit send "❌ Android 构建失败，详见附件"
tgkit send --file logging/app.log
```

## Screenshot app window

User: 「打开 Calculator 截图发 Telegram」

Agent:

```bash
tgkit screenshot --app Calculator --wait 2 --caption "Calculator 窗口"
```

## Using wrappers with auto .env

Agent (from any subdirectory if .env is in project root):

```bash
/path/to/tg-notify-skill/scripts/tg-notify.sh "hello from wrapper"
/path/to/tg-notify-skill/scripts/tg-screenshot.sh --app Safari --wait 3
```

## Wrong vs right

| Wrong | Right |
|-------|-------|
| Hardcode bot token in script | Use `.env` / `TELEGRAM_BOT_TOKEN` |
| `curl` Telegram API manually | `tgkit send "msg"` |
| Screenshot on Linux with `--app` | macOS only; use `--photo` with existing file |
