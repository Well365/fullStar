# Cursor

## Install

```bash
git clone https://YOUR_GIT/tg_skill.git
cd tg_skill
./scripts/install-skill.sh
```

或项目级（团队共享）：

```bash
mkdir -p .cursor/skills/tgkit
cp /path/to/tg-notify-skill/SKILL.md .cursor/skills/tg-notify/
cp /path/to/tg-notify-skill/reference.md .cursor/skills/tg-notify/
```

## Usage

在 Cursor Agent 对话中：

- 「用 tg-notify 发 Telegram：构建完成」
- 「截 Calculator 窗口发到 TG」
- 「把 build.log 发到 Telegram」

Agent 应读取 `tg-notify` skill 并执行 `tgkit send` / `tgkit screenshot`。

## Notes

- 确保 Agent 运行 shell 的 cwd 下有 `.env`，或已 export `TELEGRAM_BOT_TOKEN`
- Skill 名称：`tg-notify`（frontmatter `name: tgkit`）
