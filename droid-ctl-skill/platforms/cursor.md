# adb_skill on Cursor

## Install

```bash
cd /path/to/adb_skill
./scripts/install-skill.sh
```

Skill path: `~/.cursor/skills/adb/SKILL.md`

## Pair with tgkit

Also install tg_skill for Telegram remote:

```bash
cd ../tg_skill && ./scripts/install-skill.sh
```

## Example prompts

- 「adb 截图，分析当前是什么页面」
- 「用 adb 点击坐标 540 1200，然后再截一张图」
- 「adb-tg-shot 把当前手机画面发到 Telegram」
- 「安装 build/output/app.apk 并启动，截图发 TG」

## Agent notes

- Always use `droid-ctl-skill/scripts/*.sh` when possible
- After `--json`, read the PNG at `path` for vision
- Re-screenshot after every tap to verify
- Set `ADB_SERIAL` when multiple devices

See [docs/REMOTE_WORKFLOW.md](../docs/REMOTE_WORKFLOW.md) for Telegram integration.
